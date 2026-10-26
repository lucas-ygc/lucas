#pragma once
#include <cstdint>
#include <string>

// 仅 Func 初始化管理器；进程内业务调用这些接口，跨进程走现有 IPC。
enum class PtzAxis : unsigned { H = 1,
                                V = 2,
                                Both = 3 };
enum class PtzPhase { Uncalibrated,
                      Seeking,
                      Centering,
                      Ready,
                      Fault };
struct PtzAxisConfig {
    unsigned maxSteps = 0, seekSteps = 0;
    int positiveDirection = 1;
    unsigned homeLevel = 1;
    bool parametersConfirmed = false;
};
struct PtzConfig {
    PtzAxisConfig axis[2];
    unsigned defaultLevel = 1;
};
struct PtzAxisState {
    long long position = 0, target = 0;
    unsigned maxSteps = 0, speed = 0;
    bool running = false, calibrated = false, parametersConfirmed = false;
    PtzPhase phase = PtzPhase::Uncalibrated;
    int error = 0;
};
struct PtzState {
    bool available = false;
    unsigned defaultLevel = 1;
    PtzAxisState axis[2];
};
// 返回 0 表示已接受，负数为 errno；完成状态通过 PtzGetStatus 查询。
int PtzInit(const PtzConfig &config);
void PtzDeinit();
int PtzMoveTo(PtzAxis axis, long long position, unsigned level);
// level=0 使用各轴配置的 homeLevel；1..5 覆盖本次归零和回中速度。
int PtzHome(PtzAxis axis, unsigned level = 0);
int PtzCenter(PtzAxis axis, unsigned level);
int PtzStop(PtzAxis axis);
// 按住方向键：begin 建立本次会话，renew 仅续期，不重启已停止的动作。
// token 由产测端为每次按下生成；owner 由 ProdAgent 分配，不接受客户端指定。
int PtzManual(PtzAxis axis, bool increasing, unsigned level, const std::string &owner, const std::string &token, bool renew);
int PtzRelease(PtzAxis axis, const std::string &owner, const std::string &token);
int PtzDisconnect(const std::string &owner);
int PtzGetStatus(PtzState &state);
int PtzGetConfig(PtzConfig &config);
// Func 参数保存事务：准备时要求两轴静止，期间拒绝新运动，停止/查询仍可用。
// 未校准轴只更新应用范围；下次归零时建立驱动范围，不伪造位置。
struct PtzTravelConfig {
    unsigned maxSteps[2], seekSteps[2];
};
int PtzPrepareTravel(const PtzTravelConfig &travel);
int PtzFinishTravel(bool commit);
const char *PtzPhaseName(PtzPhase phase);
