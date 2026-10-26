#pragma once
#include "Command/CommandTypes.h"
#include "JsonSrc/json.h"

void InitFuncPtz();
void StopFuncPtz();
int FuncPtzStatus(Json::Value &result, std::string &message);
int FuncPtzMoveTo(const PtzMoveToCommand &command, Json::Value &result, std::string &message);
int FuncPtzStop(const PtzStopCommand &command, Json::Value &result, std::string &message);
int FuncPtzHome(const PtzHomeCommand &command, Json::Value &result, std::string &message);
int FuncPtzCenter(const PtzCenterCommand &command, Json::Value &result, std::string &message);
int FuncPtzManual(const PtzManualCommand &command, Json::Value &result, std::string &message);
int FuncPtzRelease(const PtzReleaseCommand &command, Json::Value &result, std::string &message);
int FuncPtzDisconnect(const PtzDisconnectCommand &command, Json::Value &result, std::string &message);
int FuncPtzGetConfig(Json::Value &result, std::string &message);
int FuncPtzSetConfig(const PtzSetConfigCommand &command, Json::Value &result, std::string &message);
