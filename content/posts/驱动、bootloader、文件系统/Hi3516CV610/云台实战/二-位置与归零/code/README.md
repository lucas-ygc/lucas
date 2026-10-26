# 云台实战二配套代码

本目录包含 CLI、ABI、运动规划和测试所需全部源文件，不依赖其他文章目录。
源文件取自项目 SDK/Drivers/PtzMotor，2026-10-12 快照；run-tests.sh 为教程入口。

## 主机测试

```sh
bash run-tests.sh
```

需要 C99 编译器及支持 --wrap 的链接器。absolute_test 检查规划，home_test 模拟 ioctl。
不会访问真实电机。不要使用 -DNDEBUG，否则断言验证会失效。

## 编译 ARM CLI 与板端回归

```sh
export CROSS_COMPILE=/absolute/path/to/arm-linux-musleabi-
"${CROSS_COMPILE}gcc" -std=c99 -Wall -Wextra -Werror -static ptzctl.c -o ptzctl
"${CROSS_COMPILE}gcc" -std=c99 -Wall -Wextra -Werror -static board_test.c -o ptz-board-test
```

板端必须使用与本头文件一致的模块。驱动构建在第一篇说明，本篇不重复打包内核驱动。
board_test 需要显式 --run，会实际移动两个轴；不是主机模拟测试。
先确认两轴停止、范围有效，且从当前物理位置向坐标增加方向有至少 64 半步余量。
它不归零、不修改参考位置，失败时尝试独立句柄停止两轴。

home 是用户态多阶段流程，会实际寻找端点并回中。完整撞限位归零仍待真实机械验证，
不能把模拟测试通过当成机构可以承受端点动作。CLI 普通 move-to 退出后运动继续。
