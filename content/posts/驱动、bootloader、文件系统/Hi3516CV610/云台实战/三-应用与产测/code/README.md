# 云台实战三配套代码

## 可独立执行的主机测试

```sh
bash run-tests.sh
```

依赖 C++17、pthread、支持 --wrap 的链接器。Ptz.cpp、Ptz.h、ptz_ioctl.h、manager_test.cpp
已包含全部直接依赖；测试模拟 open/close/ioctl，不访问真实 GPIO，也不连接设备。
不要加 -DNDEBUG。

## 只读产测查询

Python 3 标准库即可，不需要 pip 依赖：

```sh
python3 status_client.py 192.168.8.214 status
python3 status_client.py 192.168.8.214 get-config
```

默认端口 8899，可用 --port 指定。仅允许 ptz_status、ptz_get_config，遇到失败退出码 1。
此工具为教程新增，本次只通过本地模拟 TCP 分帧检查，未重新连接真实开发板。

## 原项目路径映射

- Ptz.cpp：application/Middleware/Ptz/Ptz.cpp
- Ptz.h：application/Interfaces/Middleware/Ptz.h
- ptz_ioctl.h：application/Middleware/Ptz/ptz_ioctl.h
- manager_test.cpp：application/Middleware/Ptz/tests/manager_test.cpp
- integration/FuncPtz.cpp、FuncPtz.h：application/Apps/Func/Src/Ptz/
- integration/Install.cmake、Kconfig、ptz-features.conf.in：application/Middleware/Ptz/
- integration/ptzpanel.cpp、ptzpanel.h：GenerateTestTools/src/device/ui/
- integration/ptz_test.cpp：GenerateTestTools/tests/

以上是 2026-10-12 源码快照。integration 是阅读与工程接入参考，需要完整项目中的
IPC、命令模型、参数服务、线程框架、Qt 和设备服务模块，不能在解压目录独立编译。
项目没有把这些依赖伪装成精简示例。完整构建、配置和启动步骤见文章。

模拟测试没有验证真实归零、电机负载、闪存断电一致性或 Qt 网络到真实板端的完整链路。
历史测试与本次实际检查见 verification.md。
