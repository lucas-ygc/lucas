# 本篇验证记录

日期：2026-10-12。

本次在主机重新执行：

- motion_test：ABI 大小、计数与方向、溢出、运动边界、相序连续性通过。
- speed_test：速度档位、绝对目标、用户态归零参数通过。
- 使用项目 ARM musl 工具链和已构建 Linux 5.10.221 执行 build.sh，通过。
- 生成 tuling_ptzmotor.ko、静态 ARM ptzctl、ptz_gpio_mux；file 确认为 ARM EABI5。
- 源码快照与项目对应原文件核对；ptz-board.dtsi 是原板级 DTS 的云台部分。

没有部署新模块、改动接线或让开发板运动。没有重新编译或烧录板级设备树。
主机测试不验证定时波形、冷启动电平、负载或真实角度。

历史依据为 SDK/Drivers/PtzMotor/README.txt 中 2026-10-11 的板端记录：
双轴各档短程往返及控制边界测试通过。完整撞限位归零、角度和长期可靠性仍待验证。
