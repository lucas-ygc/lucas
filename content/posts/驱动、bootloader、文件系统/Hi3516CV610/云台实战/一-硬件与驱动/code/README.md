# 云台实战一配套代码

目标为 BA4K / Hi3516CV610、32 位 ARM、海思 Linux 5.10.221。
驱动、CLI、头文件、接线调试工具和测试取自 2026-10-12 项目源码。
build.sh、run-tests.sh 为文章提供的独立入口。

## 主机逻辑测试

```sh
bash run-tests.sh
```

需要 C99 编译器。只运行 motion_test 和 speed_test，不操作硬件；不要加 -DNDEBUG。

## 交叉编译

```sh
export KERNEL_DIR=/absolute/path/to/built/linux
export CROSS_COMPILE=/absolute/path/to/arm-linux-musleabi-
bash build.sh
```

替换占位路径。内核需已完成匹配板端的构建，具备生成头、.config、Module.symvers。
产物在 build/：模块、ptzctl、ptz_gpio_mux、ptz.sh。没有自动部署或运动。
完整项目入口仍是 bash SDK/Build.sh l 和 bash SDK/Build.sh ptz。

ptz-board.dtsi 是本板已有 DTS 的 PTZ 片段，需合入板级 DTS，不能独立编译。
不包含完整内核、工具链或固件。迁移其他板卡必须重新核对 GPIO 和 pinmux 地址。

## 使用边界

ptz.sh 与 ptz_gpio_mux 只供明确的接线调试，不能与内核驱动或其他 GPIO 控制者同时使用。
ptzctl move-to 会实际运动，命令退出不停止电机，使用 ptzctl stop 显式停止。
位置是相序计数；停止释放线圈，不保持力。正常软件范围与机械余量需实测。
板端首次操作及临时局部坐标步骤见正文。

## 来源

原项目 SDK/Drivers/PtzMotor/ 中对应同名文件；板级片段来自
SDK/local/linux/arch/arm/boot/dts/hi3516cv610-demb-flash.dts。
电机规格图来自原目录 1.png，随文章 images 保存。
