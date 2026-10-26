#include "Ptz.h"
#include "ptz_ioctl.h"
#include <cerrno>
#include <chrono>
#include <condition_variable>
#include <deque>
#include <functional>
#include <future>
#include <mutex>
#include <thread>
#include <pthread.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>

namespace
{
    using Clock = std::chrono::steady_clock;
    struct Axis {
        PtzAxisState state;
        int fd = -1;
        Clock::time_point deadline{}, lease{};
        std::string owner, token;
        bool manual = false;
        unsigned homeLevel = 1;
    };
    class Manager
    {
      public:
        ~Manager()
        {
            close();
        }
        int init(const PtzConfig &c)
        {
            std::lock_guard<std::mutex> life(lifecycle);
            if (worker.joinable())
                return -EALREADY;
            for (const auto &a: c.axis)
                if (!a.maxSteps || a.seekSteps < a.maxSteps || a.seekSteps > 60000 || (a.positiveDirection != 1 && a.positiveDirection != -1) || a.homeLevel < 1 || a.homeLevel > 5 || a.seekSteps > a.homeLevel * 100 * PTZ_MAX_SECONDS)
                    return -EINVAL;
            if (c.defaultLevel < 1 || c.defaultLevel > 5)
                return -EINVAL;
            config = c;
            quit = false;
            std::promise<int> startup;
            auto ready = startup.get_future();
            try {
                worker = std::thread([this, &startup] { loop(startup); });
            } catch (...) {
                return -EAGAIN;
            }
            int rc = ready.get();
            if (rc)
                worker.join();
            return rc;
        }
        void close()
        {
            std::lock_guard<std::mutex> life(lifecycle);
            {
                std::lock_guard<std::mutex> lock(mutex);
                quit = true;
            }
            cv.notify_all();
            if (worker.joinable())
                worker.join();
        }
        int call(std::function<int()> fn)
        {
            auto reply = std::make_shared<std::promise<int>>();
            auto ready = reply->get_future();
            {
                std::lock_guard<std::mutex> lock(mutex);
                if (!accepting || quit)
                    return -ENODEV;
                if (jobs.size() >= 32)
                    return -EBUSY;
                jobs.emplace_back([fn, reply] { reply->set_value(fn()); });
            }
            cv.notify_one();
            return ready.get();  // 仅等待短 ioctl/入状态机，不等待电机到位
        }
        int status(PtzState &s)
        {
            return call([this, &s] {
                poll();
                s.available = true;
                s.defaultLevel = config.defaultLevel;
                for (unsigned i = 0; i < 2; ++i)
                    s.axis[i] = axes[i].state;
                return 0;
            });
        }
        int stop(unsigned mask)
        {
            if (!validMask(mask))
                return -EINVAL;
            int rc = 0;
            for (unsigned i = 0; i < 2; ++i)
                if (mask & (1U << i)) {
                    auto &a = axes[i];
                    unsigned bit = 1U << i;
                    ptz_status prior{};
                    if (a.fd < 0 || ioctl(a.fd, PTZ_STATUS, &prior) || prior.axis[i].superseded)
                        a.state.calibrated = false;
                    // 独立句柄用于明确的用户停止；旧归零流程不再继续。
                    int r = ioctl(control, PTZ_STOP, &bit) ? -errno : 0;
                    a.manual = false;
                    a.owner.clear();
                    a.token.clear();
                    if (a.state.phase == PtzPhase::Seeking)
                        a.state.calibrated = false;
                    a.state.phase = a.state.calibrated ? PtzPhase::Ready : PtzPhase::Uncalibrated;
                    if (r) {
                        a.state.error = r;
                        rc = r;
                    } else {
                        a.state.error = 0;
                        int guarded = refreshGuard(i);
                        if (guarded) {
                            a.state.error = guarded;
                            rc = guarded;
                        }
                    }
                }
            poll();
            return rc;
        }
        int move(unsigned mask, long long target, unsigned level, bool center)
        {
            if (configuring)
                return -EBUSY;
            if (!validMask(mask) || level < 1 || level > 5)
                return -EINVAL;
            poll();
            for (unsigned i = 0; i < 2; ++i)
                if (mask & (1U << i)) {
                    const auto &a = axes[i];
                    if (!a.state.calibrated)
                        return -ENODATA;
                    long long p = center ? (config.axis[i].maxSteps + 1) / 2 : target;
                    if (p < 0 || p > config.axis[i].maxSteps)
                        return -ERANGE;
                }
            for (unsigned i = 0; i < 2; ++i)
                if (mask & (1U << i)) {
                    auto &a = axes[i];
                    int rc = sendMove(i, center ? (config.axis[i].maxSteps + 1) / 2 : target, level);
                    if (rc) {
                        fault(i, rc);
                        return rc;
                    }
                    a.manual = false;
                    a.owner.clear();
                    a.token.clear();
                    a.state.phase = PtzPhase::Ready;
                }
            return 0;
        }
        int home(unsigned mask, unsigned level)
        {
            if (configuring)
                return -EBUSY;
            if (!validMask(mask) || level > 5)
                return -EINVAL;
            for (unsigned i = 0; i < 2; ++i)
                if ((mask & (1U << i)) && config.axis[i].seekSteps > (level ? level : config.axis[i].homeLevel) * 100 * PTZ_MAX_SECONDS)
                    return -EINVAL;
            for (unsigned i = 0; i < 2; ++i)
                if ((mask & (1U << i)) && !config.axis[i].parametersConfirmed)
                    return -EACCES;
            int rc = stop(mask);
            if (rc)
                return rc;
            for (unsigned i = 0; i < 2; ++i)
                if (mask & (1U << i)) {
                    auto &a = axes[i];
                    const auto &c = config.axis[i];
                    a.homeLevel = level ? level : c.homeLevel;
                    a.state.calibrated = false;
                    ptz_set_position pos{i, c.positiveDirection, 0};
                    ptz_travel travel{i, c.seekSteps};
                    if (ioctl(a.fd, PTZ_SET_POSITION, &pos) || ioctl(a.fd, PTZ_SET_TRAVEL, &travel)) {
                        rc = -errno;
                        return failMask(mask, rc);
                    }
                    pos.position = c.seekSteps;
                    if (ioctl(a.fd, PTZ_SET_POSITION, &pos)) {
                        rc = -errno;
                        return failMask(mask, rc);
                    }
                    rc = sendMove(i, 0, a.homeLevel);
                    if (rc)
                        return failMask(mask, rc);
                    a.state.phase = PtzPhase::Seeking;
                }
            return 0;
        }
        int manual(unsigned mask, bool increasing, unsigned level, const std::string &owner, const std::string &token, bool renew)
        {
            if ((mask != 1 && mask != 2) || level < 1 || level > 5 || owner.empty() || token.empty() || owner.size() > 96 || token.size() > 96)
                return -EINVAL;
            unsigned i = mask == 1 ? 0 : 1;
            auto &a = axes[i];
            poll();
            if (renew) {
                if (!a.manual || a.owner != owner || a.token != token)
                    return -ESTALE;
            } else {
                int rc = move(mask, increasing ? config.axis[i].maxSteps : 0, level, false);
                if (rc)
                    return rc;
                a.manual = true;
                a.owner = owner;
                a.token = token;
            }
            a.lease = Clock::now() + std::chrono::milliseconds(800);
            return 0;
        }
        int release(unsigned mask, const std::string &owner, const std::string &token, bool disconnect)
        {
            if (!validMask(mask))
                return -EINVAL;
            int result = 0;
            for (unsigned i = 0; i < 2; ++i)
                if (mask & (1U << i)) {
                    const auto &a = axes[i];
                    if (a.manual && a.owner == owner && (disconnect || a.token == token)) {
                        int rc = stop(1U << i);
                        if (rc)
                            result = rc;
                    }
                }
            return result;
        }
        int getConfig(PtzConfig &c)
        {
            c = config;
            return 0;
        }
        int prepareTravel(const PtzTravelConfig &t)
        {
            if (configuring)
                return -EBUSY;
            poll();
            for (unsigned i = 0; i < 2; ++i) {
                const auto &s = axes[i].state;
                if (s.running || s.phase == PtzPhase::Seeking || s.phase == PtzPhase::Centering)
                    return -EBUSY;
                if (!t.maxSteps[i] || t.seekSteps[i] < t.maxSteps[i] || t.seekSteps[i] > 60000 || t.seekSteps[i] > config.axis[i].homeLevel * 100 * PTZ_MAX_SECONDS)
                    return -EINVAL;
                if (s.position < 0 || s.position > t.maxSteps[i])
                    return -ERANGE;
                if (s.error)
                    return s.error;
            }
            pendingTravel = t;
            changedTravel = 0;
            configuring = true;
            for (unsigned i = 0; i < 2; ++i)
                if (axes[i].state.calibrated) {
                    ptz_travel travel{i, t.maxSteps[i]};
                    if (ioctl(axes[i].fd, PTZ_SET_TRAVEL, &travel)) {
                        int rc = -errno;
                        int rollback = finishTravel(false);
                        return rollback ? rollback : rc;
                    }
                    changedTravel |= 1U << i;
                }
            return 0;
        }
        int finishTravel(bool commit)
        {
            if (!configuring)
                return -EINVAL;
            int rc = 0;
            for (unsigned i = 0; i < 2; ++i) {
                if (commit) {
                    config.axis[i].maxSteps = pendingTravel.maxSteps[i];
                    config.axis[i].seekSteps = pendingTravel.seekSteps[i];
                    axes[i].state.maxSteps = pendingTravel.maxSteps[i];
                } else if (changedTravel & (1U << i)) {
                    ptz_travel travel{i, config.axis[i].maxSteps};
                    if (ioctl(axes[i].fd, PTZ_SET_TRAVEL, &travel)) {
                        rc = -errno;
                        fault(i, rc);
                    }
                }
            }
            configuring = false;
            changedTravel = 0;
            return rc;
        }

      private:
        PtzConfig config;
        PtzTravelConfig pendingTravel{};
        bool configuring = false;
        unsigned changedTravel = 0;
        Axis axes[2];
        int control = -1;
        std::mutex mutex, lifecycle;
        std::condition_variable cv;
        std::deque<std::function<void()>> jobs;
        bool quit = false, accepting = false;
        std::thread worker;
        static bool validMask(unsigned m)
        {
            return m && !(m & ~3U);
        }
        int refreshGuard(unsigned i)
        {
            if (axes[i].fd >= 0)
                ::close(axes[i].fd);
            axes[i].fd = ::open("/dev/tuling_ptz", O_RDWR | O_CLOEXEC);
            if (axes[i].fd < 0)
                return -errno;
            unsigned mask = 1U << i;
            return ioctl(axes[i].fd, PTZ_GUARD, &mask) ? -errno : 0;
        }
        int sendMove(unsigned i, long long target, unsigned level)
        {
            ptz_move_to to{i, level * 100, target};
            if (ioctl(axes[i].fd, PTZ_MOVE_TO, &to))
                return -errno;
            axes[i].state.target = target;
            axes[i].deadline = Clock::now() + std::chrono::seconds(PTZ_MAX_SECONDS + 10);
            return 0;
        }
        void fault(unsigned i, int rc)
        {
            auto &a = axes[i];
            unsigned mask = 1U << i;
            // 保护句柄阻止旧动作清理时误停外部新命令。
            if (a.fd >= 0)
                ioctl(a.fd, PTZ_STOP, &mask);
            a.manual = false;
            a.owner.clear();
            a.token.clear();
            a.state.phase = PtzPhase::Fault;
            a.state.error = rc;
            a.state.calibrated = false;
        }
        int failMask(unsigned mask, int rc)
        {
            for (unsigned i = 0; i < 2; ++i)
                if (mask & (1U << i))
                    fault(i, rc);
            return rc;
        }
        void poll()
        {
            for (unsigned i = 0; i < 2; ++i) {
                auto &a = axes[i];
                ptz_status s{};
                if (a.fd < 0 || ioctl(a.fd, PTZ_STATUS, &s)) {
                    fault(i, -ENODEV);
                    continue;
                }
                const auto &d = s.axis[i];
                a.state.position = d.position;
                a.state.target = d.target;
                a.state.running = d.running;
                a.state.speed = d.speed;
                if (d.superseded) {
                    fault(i, -ESTALE);
                    continue;
                }
                if (a.manual && Clock::now() >= a.lease) {
                    unsigned bit = 1U << i;
                    if (ioctl(a.fd, PTZ_STOP, &bit))
                        fault(i, -errno);
                    a.manual = false;
                    a.owner.clear();
                    a.token.clear();
                    continue;
                }
                if (d.running && Clock::now() > a.deadline) {
                    fault(i, -ETIMEDOUT);
                    continue;
                }
                if (d.running)
                    continue;
                if (a.state.phase == PtzPhase::Seeking) {
                    if (d.position != 0) {
                        fault(i, -ECANCELED);
                        continue;
                    }
                    ptz_travel travel{i, config.axis[i].maxSteps};
                    if (ioctl(a.fd, PTZ_SET_TRAVEL, &travel)) {
                        fault(i, -errno);
                        continue;
                    }
                    a.state.calibrated = true;
                    int rc = sendMove(i, (travel.max_steps + 1) / 2, a.homeLevel);
                    if (rc) {
                        fault(i, rc);
                        continue;
                    }
                    a.state.phase = PtzPhase::Centering;
                } else if (a.state.phase == PtzPhase::Centering) {
                    if (d.position != (config.axis[i].maxSteps + 1) / 2) {
                        fault(i, -ECANCELED);
                        continue;
                    }
                    a.state.phase = PtzPhase::Ready;
                }
            }
        }
        void loop(std::promise<int> &startup)
        {
            pthread_setname_np(pthread_self(), "FuncPtz");
            control = ::open("/dev/tuling_ptz", O_RDWR | O_CLOEXEC);
            int rc = control < 0 ? -errno : 0;
            unsigned both = 3;
            if (!rc && ioctl(control, PTZ_STOP, &both))
                rc = -errno;
            for (unsigned i = 0; i < 2 && !rc; ++i) {
                axes[i] = Axis{};
                axes[i].state.maxSteps = config.axis[i].maxSteps;
                axes[i].state.parametersConfirmed = config.axis[i].parametersConfirmed;
                rc = refreshGuard(i);
            }
            {
                std::lock_guard<std::mutex> lock(mutex);
                accepting = !rc;
            }
            startup.set_value(rc);
            if (!rc)
                for (;;) {
                    std::function<void()> task;
                    {
                        std::unique_lock<std::mutex> lock(mutex);
                        cv.wait_for(lock, std::chrono::milliseconds(20), [this] { return quit || !jobs.empty(); });
                        if (!jobs.empty()) {
                            task = std::move(jobs.front());
                            jobs.pop_front();
                        } else if (quit)
                            break;
                    }
                    if (task)
                        task();
                    poll();
                }
            {
                std::lock_guard<std::mutex> lock(mutex);
                accepting = false;
            }
            if (control >= 0) {
                ioctl(control, PTZ_STOP, &both);
                ::close(control);
                control = -1;
            }
            for (auto &a: axes)
                if (a.fd >= 0) {
                    ::close(a.fd);
                    a.fd = -1;
                }
        }
    };
    Manager manager;
    unsigned mask(PtzAxis a)
    {
        return static_cast<unsigned>(a);
    }
}
int PtzInit(const PtzConfig &c)
{
    return manager.init(c);
}
void PtzDeinit()
{
    manager.close();
}
int PtzGetStatus(PtzState &s)
{
    return manager.status(s);
}
int PtzGetConfig(PtzConfig &c)
{
    return manager.call([&] { return manager.getConfig(c); });
}
int PtzPrepareTravel(const PtzTravelConfig &t)
{
    return manager.call([=] { return manager.prepareTravel(t); });
}
int PtzFinishTravel(bool commit)
{
    return manager.call([=] { return manager.finishTravel(commit); });
}
int PtzMoveTo(PtzAxis a, long long p, unsigned l)
{
    return manager.call([=] { return manager.move(mask(a), p, l, false); });
}
int PtzCenter(PtzAxis a, unsigned l)
{
    return manager.call([=] { return manager.move(mask(a), 0, l, true); });
}
int PtzStop(PtzAxis a)
{
    return manager.call([=] { return manager.stop(mask(a)); });
}
int PtzHome(PtzAxis a, unsigned level)
{
    return manager.call([=] { return manager.home(mask(a), level); });
}
int PtzManual(PtzAxis a, bool inc, unsigned l, const std::string &o, const std::string &t, bool renew)
{
    return manager.call([=] { return manager.manual(mask(a), inc, l, o, t, renew); });
}
int PtzRelease(PtzAxis a, const std::string &o, const std::string &t)
{
    return manager.call([=] { return manager.release(mask(a), o, t, false); });
}
int PtzDisconnect(const std::string &o)
{
    return manager.call([=] { return manager.release(3, o, "", true); });
}
const char *PtzPhaseName(PtzPhase p)
{
    switch (p) {
    case PtzPhase::Uncalibrated:
        return "uncalibrated";
    case PtzPhase::Seeking:
        return "seeking";
    case PtzPhase::Centering:
        return "centering";
    case PtzPhase::Ready:
        return "ready";
    default:
        return "fault";
    }
}
