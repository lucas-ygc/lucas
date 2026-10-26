# CT1820B 教程配套代码

适用：BA4K / Hi3516CV610，Linux 5.10.221 厂商内核，独立供电。
驱动和 Temperature.cpp、Temperature.h 为项目 2026-10-12 源码快照。
read_temperature.cpp 与 build-module.sh 为教程补充。
不包含厂商 SDK、工具链、内核、板级完整 DTS、固件或数据手册。

## 构建用户态示例

在本目录执行，按本机位置设置工具链前缀：

```sh
export CROSS_COMPILE=/absolute/path/to/arm-linux-musleabi-
"${CROSS_COMPILE}g++" -std=c++17 -Wall -Wextra -Werror \
    -DCONFIG_SENSOR_CT1820B -I. Temperature.cpp read_temperature.cpp \
    -o read_temperature
```

将 read_temperature 复制到具有匹配 musl 运行库的目标板，加载驱动并等待发现设备后执行：

```sh
./read_temperature
```

必须恰好存在一个 /sys/bus/w1/devices/28-*/temperature。失败输出负 errno，退出码 1。
主机可以使用 g++ 编译做语法检查，但没有真实节点时不能验证硬件测温。

## 构建内核模块

KERNEL_DIR 必须是完成构建且与板端运行内核匹配的源码树，含 .config、生成头和 Module.symvers。
内核需启用 CONFIG_W1=m、CONFIG_W1_MASTER_GPIO=m，并关闭 CONFIG_W1_SLAVE_THERM。

```sh
export KERNEL_DIR=/absolute/path/to/built/linux
export CROSS_COMPILE=/absolute/path/to/arm-linux-musleabi-
bash build-module.sh
```

脚本先执行内核 modules 构建以生成 W1 导出符号，再编译 ct1820b.ko。
wire.ko 与 w1-gpio.ko 从同一内核的 drivers/w1/ 与 drivers/w1/masters/ 获取。
完整项目仍优先使用项目根目录下 bash SDK/Build.sh l 和 bash SDK/Build.sh temperature。

ct1820b-board.dtsi 只展示本板温度相关配置；合入已有 DTS 时避免重复节点和标签。
其他板卡必须重新确认 GPIO、地址单元和 pinmux 寄存器。

## 板端加载

确认内核、设备树已更新且未加载旧模块后，在三个模块所在目录执行：

```sh
insmod wire.ko
insmod ct1820b.ko
insmod w1-gpio.ko
ls /sys/bus/w1/devices/
cat /sys/bus/w1/devices/28-*/temperature
```

更新前停止读取者，依次卸载 w1_gpio、ct1820b、wire。wire 若有其他使用者，不应强制卸载。
不使用 insmod -f，不让 w1_therm 同时占用 0x28 家族。

## 验证范围

历史记录：2026-10-10 板端 30 次读取成功，26625～26687 毫摄氏度；不是精度校准。
应用接口原项目记录了主机测试和交叉编译通过，应用接口上板测试尚未完成。
本次教程配套代码的检查结果见 verification.md。
