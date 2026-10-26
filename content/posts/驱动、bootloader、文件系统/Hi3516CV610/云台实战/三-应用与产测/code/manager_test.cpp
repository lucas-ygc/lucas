#include "Ptz.h"
#include "ptz_ioctl.h"
#include <cassert>
#include <cerrno>
#include <cstdarg>
#include <cstdio>
#include <map>
#include <mutex>
#include <thread>
#include <chrono>
#include <sys/ioctl.h>
struct DriverAxis {
    long long pos = 0, target = 0;
    unsigned max = 0, speed = 0;
    bool running = false, freeze = false;
    unsigned long long gen = 0;
};
struct File {
    unsigned mask = 0;
    unsigned long long gen[2] = {0, 0};
};
static DriverAxis axes[2];
static std::map<int, File> files;
static int nextfd = 100;
static bool freezeCenter = false;
static int failTravelAxis = -1;
static std::mutex m;
extern "C" int __wrap_open(const char *, int, ...)
{
    std::lock_guard<std::mutex> l(m);
    files[++nextfd] = File{};
    return nextfd;
}
extern "C" int __wrap_close(int fd)
{
    std::lock_guard<std::mutex> l(m);
    files.erase(fd);
    return 0;
}
extern "C" int __wrap_ioctl(int fd, unsigned long cmd, ...)
{
    va_list ap;
    va_start(ap, cmd);
    void *p = va_arg(ap, void *);
    va_end(ap);
    std::lock_guard<std::mutex> l(m);
    auto &f = files.at(fd);
    unsigned mask = 0;
    if (cmd == PTZ_STOP || cmd == PTZ_GUARD)
        mask = *static_cast<unsigned *>(p);
    else if (cmd == PTZ_MOVE_TO)
        mask = 1U << static_cast<ptz_move_to *>(p)->axis;
    else if (cmd == PTZ_SET_POSITION)
        mask = 1U << static_cast<ptz_set_position *>(p)->axis;
    else if (cmd == PTZ_SET_TRAVEL)
        mask = 1U << static_cast<ptz_travel *>(p)->axis;
    for (unsigned i = 0; i < 2; ++i)
        if ((mask & f.mask & (1U << i)) && f.gen[i] != axes[i].gen) {
            errno = ESTALE;
            return -1;
        }
    if (cmd == PTZ_STATUS) {
        auto &s = *static_cast<ptz_status *>(p);
        s = {};
        for (unsigned i = 0; i < 2; ++i) {
            auto &a = axes[i];
            if (a.running && !a.freeze) {
                a.pos = a.target;
                a.running = false;
            }
            s.axis[i].running = a.running;
            s.axis[i].position = a.pos;
            s.axis[i].target = a.target;
            s.axis[i].speed = a.speed;
            s.axis[i].generation = a.gen;
            s.axis[i].superseded = (f.mask & (1U << i)) && f.gen[i] != a.gen;
        }
        return 0;
    }
    if (cmd == PTZ_GUARD) {
        f.mask |= mask;
        for (unsigned i = 0; i < 2; ++i)
            if (mask & (1U << i))
                f.gen[i] = axes[i].gen;
        return 0;
    }
    if (cmd == PTZ_STOP) {
        for (unsigned i = 0; i < 2; ++i)
            if (mask & (1U << i)) {
                axes[i].running = false;
                axes[i].target = axes[i].pos;
            }
    }
    if (cmd == PTZ_SET_POSITION) {
        auto &v = *static_cast<ptz_set_position *>(p);
        axes[v.axis].pos = v.position;
        axes[v.axis].target = v.position;
    }
    if (cmd == PTZ_SET_TRAVEL) {
        auto &v = *static_cast<ptz_travel *>(p);
        if (static_cast<int>(v.axis) == failTravelAxis) {
            failTravelAxis = -1;
            errno = EIO;
            return -1;
        }
        axes[v.axis].max = v.max_steps;
    }
    if (cmd == PTZ_MOVE_TO) {
        auto &v = *static_cast<ptz_move_to *>(p);
        auto &a = axes[v.axis];
        if (v.target < 0 || v.target > a.max) {
            errno = ERANGE;
            return -1;
        }
        a.target = v.target;
        a.speed = v.speed;
        a.running = a.pos != a.target;
        if (freezeCenter && v.target == 50)
            a.freeze = true;
    }
    for (unsigned i = 0; i < 2; ++i)
        if (mask & (1U << i))
            f.gen[i] = ++axes[i].gen;
    return 0;
}
static void waitReady()
{
    for (int i = 0; i < 100; ++i) {
        PtzState s;
        assert(!PtzGetStatus(s));
        if (s.axis[0].phase == PtzPhase::Ready && s.axis[1].phase == PtzPhase::Ready)
            return;
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
    assert(false);
}
int main()
{
    PtzConfig c;
    for (auto &a: c.axis) {
        a.maxSteps = 100;
        a.seekSteps = 120;
        a.homeLevel = 1;
    }
    assert(!PtzInit(c));
    assert(PtzHome(PtzAxis::Both) == -EACCES);
    assert(PtzMoveTo(PtzAxis::H, 5, 1) == -ENODATA);
    PtzDeinit();
    for (auto &a: c.axis)
        a.parametersConfirmed = true;
    assert(!PtzInit(c));
    {
        std::lock_guard<std::mutex> l(m);
        axes[0].freeze = true;
        axes[1].freeze = true;
    }
    assert(PtzHome(PtzAxis::Both, 6) == -EINVAL);
    assert(!PtzHome(PtzAxis::Both, 4));
    {
        PtzState state;
        assert(!PtzGetStatus(state));
        assert(state.axis[0].speed == 400 && state.axis[1].speed == 400);
    }
    assert(!PtzStop(PtzAxis::H));
    PtzState s;
    assert(!PtzGetStatus(s));
    assert(!s.axis[0].calibrated && s.axis[1].phase == PtzPhase::Seeking);
    assert(!PtzStop(PtzAxis::Both));
    {
        std::lock_guard<std::mutex> l(m);
        axes[0].freeze = false;
        axes[1].freeze = false;
    }
    assert(!PtzHome(PtzAxis::Both));
    waitReady();
    assert(!PtzGetStatus(s) && s.axis[0].position == 50 && s.axis[1].position == 50);
    {
        std::lock_guard<std::mutex> l(m);
        freezeCenter = true;
    }
    assert(!PtzHome(PtzAxis::H, 5));
    assert(!PtzGetStatus(s) && s.axis[0].phase == PtzPhase::Centering && s.axis[0].speed == 500);
    assert(!PtzStop(PtzAxis::H));
    assert(!PtzGetStatus(s) && s.axis[0].calibrated && s.axis[0].phase == PtzPhase::Ready);
    {
        std::lock_guard<std::mutex> l(m);
        freezeCenter = false;
        axes[0].freeze = false;
    }
    assert(PtzMoveTo(PtzAxis::H, 101, 1) == -ERANGE);
    assert(!PtzMoveTo(PtzAxis::Both, 20, 3));
    assert(!PtzGetStatus(s) && s.axis[0].position == 20 && s.axis[1].position == 20);
    PtzTravelConfig travel{{80, 70}, {120, 120}};
    assert(!PtzPrepareTravel(travel));
    assert(PtzMoveTo(PtzAxis::H, 30, 1) == -EBUSY);
    assert(PtzHome(PtzAxis::Both) == -EBUSY);
    assert(!PtzFinishTravel(false));  // 模拟落盘失败：两轴原范围恢复。
    {
        std::lock_guard<std::mutex> l(m);
        assert(axes[0].max == 100 && axes[1].max == 100);
        failTravelAxis = 1;
    }
    assert(PtzPrepareTravel(travel) == -EIO);
    {
        std::lock_guard<std::mutex> l(m);
        assert(axes[0].max == 100 && axes[1].max == 100);
    }
    assert(!PtzPrepareTravel(travel));
    assert(!PtzFinishTravel(true));
    PtzConfig actual;
    assert(!PtzGetConfig(actual));
    assert(actual.axis[0].maxSteps == 80 && actual.axis[1].maxSteps == 70);
    assert(actual.axis[0].seekSteps == 120);
    assert(!PtzGetStatus(s) && s.axis[0].calibrated && s.axis[1].calibrated);
    travel.maxSteps[1] = 10;
    assert(PtzPrepareTravel(travel) == -ERANGE);
    assert(!PtzGetConfig(actual) && actual.axis[0].maxSteps == 80 && actual.axis[1].maxSteps == 70);
    travel.maxSteps[1] = 70;
    travel.seekSteps[0] = 60;
    assert(PtzPrepareTravel(travel) == -EINVAL);
    travel.seekSteps[0] = 120;
    {
        std::lock_guard<std::mutex> l(m);
        axes[0].freeze = true;
    }
    assert(!PtzManual(PtzAxis::H, true, 1, "owner", "one", false));
    assert(PtzPrepareTravel(travel) == -EBUSY);
    assert(!PtzManual(PtzAxis::H, true, 1, "owner", "one", true));
    assert(!PtzRelease(PtzAxis::H, "owner", "old"));
    assert(!PtzGetStatus(s) && s.axis[0].running);
    std::this_thread::sleep_for(std::chrono::milliseconds(900));
    assert(!PtzGetStatus(s) && !s.axis[0].running);
    assert(PtzManual(PtzAxis::H, true, 1, "owner", "one", true) == -ESTALE);
    assert(!PtzManual(PtzAxis::H, true, 1, "owner", "two", false));
    assert(!PtzDisconnect("owner"));
    assert(!PtzGetStatus(s) && !s.axis[0].running);
    // 外部句柄修改 H，V 的校准与控制仍保留；停止不能错误恢复 H 的可信状态。
    {
        std::lock_guard<std::mutex> l(m);
        ++axes[0].gen;
    }
    assert(!PtzStop(PtzAxis::H));
    assert(!PtzGetStatus(s) && !s.axis[0].calibrated && s.axis[1].calibrated);
    assert(!PtzMoveTo(PtzAxis::V, 30, 2));
    PtzDeinit();
    assert(PtzGetStatus(s) == -ENODEV);
    assert(files.empty());
    puts("PASS: homing/cancel/axis independence, bounds, leases, stale renewals, disconnect, external replacement, shutdown");
}
