#include "Command/Command.h"
#include "FuncPtz.h"
#include "InterfacesMiddleware.h"
#include "InterfacesCore.h"
#include "ParamShmClient.h"
#include "ParamClient.h"
#include "IPCCommon.h"
#include "FuncCommon.h"
#include <cerrno>
#include <cstring>
#include <mutex>
#include <fstream>
#include <iterator>
#include <cmath>

namespace
{
    std::mutex initMutex;
    bool initialized = false;
    int initError = -ENODATA;
#ifdef CONFIG_PTZ
    bool unsignedField(const Json::Value &v, const char *name, unsigned &out)
    {
        const auto &n = v[name];
        if (n.isUInt()) {
            if (n.asUInt64() > 0xffffffffULL)
                return false;
            out = static_cast<unsigned>(n.asUInt64());
            return true;
        }
        if (!n.isInt() || n.asInt64() < 0 || n.asInt64() > 0xffffffffLL)
            return false;
        out = static_cast<unsigned>(n.asInt64());
        return true;
    }
    int readConfig(PtzConfig &c, Json::Value *raw = nullptr)
    {
        std::string text;
        Json::Value root;
        if (ParamShm::ReadJsonTable(ParamShm::ConfigShmName(), text))
            Json::Reader().parse(text, root);
        Json::Value p;
        if (root.isObject() && root["sys"].isObject())
            p = root["sys"]["ptz"];
        // 旧持久化参数没有新增硬件字段时，采用随产品打包的默认段，不恢复整张参数表。
        if (p.isNull()) {
            std::ifstream file("/usr/app/Bin/config_table.json");
            std::string data((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
            Json::Value defaults;
            if (!file || !Json::Reader().parse(data, defaults) || !defaults.isObject() || !defaults["items"].isObject() || !defaults["items"]["sys"].isObject() || !defaults["items"]["sys"]["value"].isObject())
                return -ENODATA;
            p = defaults["items"]["sys"]["value"]["ptz"];
        }
        if (raw)
            *raw = p;
        if (!p.isObject() || !unsignedField(p, "defaultLevel", c.defaultLevel))
            return -ENODATA;
        const char *names[] = {"h", "v"};
        for (unsigned i = 0; i < 2; ++i) {
            const auto &v = p[names[i]];
            auto &a = c.axis[i];
            if (!v.isObject() || !unsignedField(v, "maxSteps", a.maxSteps) || !unsignedField(v, "seekSteps", a.seekSteps) || !unsignedField(v, "homeLevel", a.homeLevel) || !v["positiveDirection"].isInt() || !v["parametersConfirmed"].isBool())
                return -EINVAL;
            a.positiveDirection = v["positiveDirection"].asInt();
            a.parametersConfirmed = v["parametersConfirmed"].asBool();
        }
        return 0;
    }
    Json::Value stateJson()
    {
        PtzState s;
        int rc = PtzGetStatus(s);
        Json::Value out;
        out["supported"] = true;
        out["available"] = rc == 0;
        out["error"] = rc;
        if (rc)
            return out;
        out["default_level"] = s.defaultLevel;
        const char *names[] = {"h", "v"};
        for (unsigned i = 0; i < 2; ++i) {
            auto &v = out[names[i]];
            const auto &a = s.axis[i];
            v["position"] = Json::Int64(a.position);
            v["target"] = Json::Int64(a.target);
            v["max_steps"] = a.maxSteps;
            v["speed"] = a.speed;
            v["running"] = a.running;
            v["calibrated"] = a.calibrated;
            v["parameters_confirmed"] = a.parametersConfirmed;
            v["phase"] = PtzPhaseName(a.phase);
            v["error"] = a.error;
        }
        return out;
    }
    Json::Value configJson(const PtzConfig &c)
    {
        Json::Value out;
        std::string revision = std::to_string(c.defaultLevel);
        out["default_level"] = c.defaultLevel;
        for (unsigned i = 0; i < 2; ++i) {
            auto &v = out[i ? "v" : "h"];
            const auto &a = c.axis[i];
            v["max_angle"] = a.maxSteps * 360.0 / 4096.0;
            v["max_steps"] = a.maxSteps;
            v["seek_steps"] = a.seekSteps;
            v["home_level"] = a.homeLevel;
            v["positive_direction"] = a.positiveDirection;
            v["parameters_confirmed"] = a.parametersConfirmed;
            revision += "/" + std::to_string(a.maxSteps) + "/" + std::to_string(a.seekSteps) + "/" + std::to_string(a.homeLevel) + "/" + std::to_string(a.positiveDirection) + "/" + std::to_string(a.parametersConfirmed);
        }
        out["revision"] = revision;
        return out;
    }
    int configureTravel(const PtzSetConfigCommand &p, Json::Value &result, std::string &message)
    {
        PtzConfig current;
        int rc = PtzGetConfig(current);
        if (rc)
            return rc;
        if (p.expectedRevision != configJson(current)["revision"].asString()) {
            message = "配置已改变，请重新读取";
            return -EAGAIN;
        }
        PtzTravelConfig t{};
        for (unsigned i = 0; i < 2; ++i) {
            t.maxSteps[i] = static_cast<unsigned>(std::llround(p.travel[i].maxAngle * 4096.0 / 360.0));
            t.seekSteps[i] = p.travel[i].seekSteps;
        }
        auto &client = ParamClient::instance();
        Json::Value sys;
        if (!client.get("config", "sys", sys, 3000, ParamClient::Source::Ipc) || !sys.isObject())
            return -EIO;
        Json::Value raw = sys.get("ptz", Json::Value());
        const bool missing = raw.isNull();
        if (missing) {
            PtzConfig unused;
            if (readConfig(unused, &raw))
                return -EIO;
        }
        if (!raw.isObject())
            return -EINVAL;
        unsigned defaultLevel = 0;
        if (!unsignedField(raw, "defaultLevel", defaultLevel) || defaultLevel != current.defaultLevel)
            return -EAGAIN;
        // 不覆盖其他接口已修改但 Func 尚未应用的硬件配置。
        for (unsigned i = 0; i < 2; ++i) {
            const auto &a = raw[i ? "v" : "h"];
            const auto &old = current.axis[i];
            if (!a.isObject())
                return -EINVAL;
            unsigned max = 0, seek = 0, homeLevel = 0;
            if (!unsignedField(a, "maxSteps", max) || !unsignedField(a, "seekSteps", seek) || max != old.maxSteps || seek != old.seekSteps || !unsignedField(a, "homeLevel", homeLevel) || homeLevel != old.homeLevel || !a["positiveDirection"].isInt() || a["positiveDirection"].asInt() != old.positiveDirection || !a["parametersConfirmed"].isBool() || a["parametersConfirmed"].asBool() != old.parametersConfirmed) {
                message = "设备参数与运行配置不一致，请重启 Func 后重新读取";
                return -EAGAIN;
            }
        }
        Json::Value updated = raw;
        for (unsigned i = 0; i < 2; ++i) {
            updated[i ? "v" : "h"]["maxSteps"] = t.maxSteps[i];
            updated[i ? "v" : "h"]["seekSteps"] = t.seekSteps[i];
        }
        // 旧设备尚无 sys.ptz 时，条件更新整个 sys，保留其他参数且防止并发覆盖。
        const std::string key = missing ? "sys" : "sys.ptz";
        Json::Value before = missing ? sys : raw, after = missing ? sys : updated;
        if (missing)
            after["ptz"] = updated;
        if (Json::FastWriter().write(before).size() + Json::FastWriter().write(after).size() + 512 >= sizeof(IPCMessage{}.payload))
            return -E2BIG;
        rc = PtzPrepareTravel(t);
        if (rc) {
            if (rc == -EBUSY)
                message = "请先停止两轴，再保存行程";
            if (rc == -ERANGE)
                message = "当前位置超出新范围，请先移回新范围内";
            if (rc == -EINVAL)
                message = "归零行程必须不少于运动范围，且满足归零速度的时长限制";
            return rc;
        }
        Json::Value response;
        bool saved = client.compareSet("config", key, after, before, 3000, &response);
        if (!saved && response.isNull()) {
            // 超时不等于落盘失败：重新读取确认，不能盲目报告成功。
            Json::Value actual;
            saved = client.get("config", key, actual, 3000, ParamClient::Source::Ipc) && Json::FastWriter().write(actual) == Json::FastWriter().write(after);
        }
        rc = PtzFinishTravel(saved);
        result["saved"] = saved;
        result["applied"] = saved && !rc;
        if (!saved) {
            message = response.isNull() ? "保存结果未确认，请重新读取设备配置" : response.get("message", "保存失败，运行范围已回退").asString();
            if (rc)
                message += "；驱动范围回退失败，需要重新校准";
            return rc ? rc : -EIO;
        }
        if (rc)
            return rc;
        PtzGetConfig(current);
        result["ptz_config"] = configJson(current);
        message = "已保存并应用";
        return 0;
    }
#endif
}
void InitFuncPtz()
{
#ifdef CONFIG_PTZ
    std::lock_guard<std::mutex> lock(initMutex);
    if (initialized)
        return;
    PtzConfig c;
    int rc = readConfig(c);
    if (!rc)
        rc = PtzInit(c);
    if (rc != initError)
        FUNC_WARN("PTZ initialization: %d\n", rc);
    initError = rc;
    initialized = !rc;
#endif
}
#ifdef CONFIG_PTZ
static void FuncPtzInitTask(bool running)
{
    if (running)
        InitFuncPtz();
}
REGISTER_TASK_INTERVAL(FuncPtzInitTask, 5);
#endif
void StopFuncPtz()
{
#ifdef CONFIG_PTZ
    std::lock_guard<std::mutex> lock(initMutex);
    PtzDeinit();
    initialized = false;
#endif
}

namespace
{
#ifndef CONFIG_PTZ
    int ptzUnavailable(Json::Value &result, std::string &message)
    {
        message = "PTZ disabled in Kconfig";
        result["ptz"]["supported"] = false;
        result["ptz"]["available"] = false;
        return -ENOTSUP;
    }
#else
    PtzAxis driverAxis(PtzCommandAxis axis)
    {
        return axis == PtzCommandAxis::H ? PtzAxis::H : axis == PtzCommandAxis::V ? PtzAxis::V
                                                                                  : PtzAxis::Both;
    }

    // 仅整理操作结果，不决定执行哪条命令。
    int motionResult(int code, Json::Value &result, std::string &message)
    {
        message = code ? strerror(-code) : "accepted";
        if (code == -ENODATA)
            message = "axis not calibrated";
        if (code == -EACCES)
            message = "homing direction and travel parameters not confirmed";
        result["accepted"] = code == 0;
        result["ptz"] = stateJson();
        return code;
    }
#endif
}

int FuncPtzStatus(Json::Value &result, std::string &message)
{
#ifndef CONFIG_PTZ
    ptzUnavailable(result, message);
    return 0;
#else
    result["ptz"] = stateJson();
    if (!result["ptz"]["available"].asBool())
        message = "PTZ configuration or driver unavailable";
    return 0;
#endif
}

int FuncPtzMoveTo(const PtzMoveToCommand &command, Json::Value &result, std::string &message)
{
#ifndef CONFIG_PTZ
    (void)command;
    return ptzUnavailable(result, message);
#else
    return motionResult(PtzMoveTo(driverAxis(command.axis), command.position, command.level), result, message);
#endif
}

int FuncPtzStop(const PtzStopCommand &command, Json::Value &result, std::string &message)
{
#ifndef CONFIG_PTZ
    (void)command;
    return ptzUnavailable(result, message);
#else
    return motionResult(PtzStop(driverAxis(command.axis)), result, message);
#endif
}

int FuncPtzHome(const PtzHomeCommand &command, Json::Value &result, std::string &message)
{
#ifndef CONFIG_PTZ
    (void)command;
    return ptzUnavailable(result, message);
#else
    return motionResult(PtzHome(driverAxis(command.axis), command.level), result, message);
#endif
}

int FuncPtzCenter(const PtzCenterCommand &command, Json::Value &result, std::string &message)
{
#ifndef CONFIG_PTZ
    (void)command;
    return ptzUnavailable(result, message);
#else
    return motionResult(PtzCenter(driverAxis(command.axis), command.level), result, message);
#endif
}

int FuncPtzManual(const PtzManualCommand &command, Json::Value &result, std::string &message)
{
#ifndef CONFIG_PTZ
    (void)command;
    return ptzUnavailable(result, message);
#else
    return motionResult(PtzManual(driverAxis(command.axis), command.increasing, command.level, command.owner, command.token, command.renew), result, message);
#endif
}

int FuncPtzRelease(const PtzReleaseCommand &command, Json::Value &result, std::string &message)
{
#ifndef CONFIG_PTZ
    (void)command;
    return ptzUnavailable(result, message);
#else
    return motionResult(PtzRelease(driverAxis(command.axis), command.owner, command.token), result, message);
#endif
}

int FuncPtzDisconnect(const PtzDisconnectCommand &command, Json::Value &result, std::string &message)
{
#ifndef CONFIG_PTZ
    (void)command;
    return ptzUnavailable(result, message);
#else
    return motionResult(PtzDisconnect(command.owner), result, message);
#endif
}

int FuncPtzGetConfig(Json::Value &result, std::string &message)
{
#ifndef CONFIG_PTZ
    return ptzUnavailable(result, message);
#else
    PtzConfig current;
    int code = PtzGetConfig(current);
    if (!code) {
        PtzConfig stored;
        code = readConfig(stored);
        if (!code && configJson(stored)["revision"] != configJson(current)["revision"]) {
            message = "保存参数与运行配置不一致，请重启 Func 后重新读取";
            return -EAGAIN;
        }
        if (!code)
            result["ptz_config"] = configJson(current);
    }
    if (code)
        message = strerror(-code);
    return code;
#endif
}

int FuncPtzSetConfig(const PtzSetConfigCommand &command, Json::Value &result, std::string &message)
{
#ifndef CONFIG_PTZ
    (void)command;
    return ptzUnavailable(result, message);
#else
    message.clear();
    const int code = configureTravel(command, result, message);
    if (code && message.empty())
        message = strerror(-code);
    return code;
#endif
}
