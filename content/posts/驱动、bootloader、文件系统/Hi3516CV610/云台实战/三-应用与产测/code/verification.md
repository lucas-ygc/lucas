# 本篇验证记录

日期：2026-10-12。

本次重新执行：

- 下载包 run-tests.sh：管理器模拟驱动测试通过，覆盖归零、中断、双轴、行程、
  手动租期、旧 token、断线、外部替换、配置范围回退及线程退出。
- Ptz.cpp 使用项目 ARM musl g++、C++17、-Wall -Wextra -Werror -pthread 编译为对象通过。
- 完整项目 gtt-ptz-test 目标重新构建通过，Qt offscreen CTest 1/1 通过。
- status_client.py 使用本地 socketpair 模拟分段帧，验证 accepted/completed、query_id
  及只读命令约束通过；没有连接真实开发板或外部网络。

本次未重新编译全部 Func/ProdAgent，也未执行设备参数保存、固件部署或机械运动。
integration 源码依赖完整项目，独立包只对管理器与查询工具提供可独立运行入口。

历史设备验证来自 application/Doc/PTZ.txt（2026-10-11）：真实产测状态/停止、
配置保存/读回/恢复及边界拒绝通过；应用层完整撞限位归零尚未验证。

特别核对：当前 Ptz.cpp 在空闲时也采用约 20ms wait_for 周期轮询；ABI 两份头文件
存在排版差异，但字段和命令定义相同。正文以源码为准，不照抄旧路径和简写描述。
