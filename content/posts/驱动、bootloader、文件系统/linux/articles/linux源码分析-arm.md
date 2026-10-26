---
title: linux 源码分析-arm
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux驱动学习
abbrlink: 47c6620a
typora-root-url: ./..\..\..
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---
arm架构:
# linux 启动流程
linux启动先从head.s 开始，源码路径为：arch/arm/boot/head.s
1、head.s 启动函数
完成引导参数初始化，跳转start_kernel函数
2、start_kernel函数
源码路径为：init/main.c 
完成系统初始化，执行rest_init，调用kernel_init函数


# Kconfig配置
```shell
# SPDX-License-Identifier: GPL-2.0-only
#
# RF switch subsystem configuration
#
menuconfig RFKILL
	tristate "RF switch subsystem support"
	help
	  Say Y here if you want to have control over RF switches
	  found on many WiFi and Bluetooth cards.

	  To compile this driver as a module, choose M here: the
	  module will be called rfkill.

# LED trigger support
config RFKILL_LEDS
	bool
	depends on RFKILL
	depends on LEDS_TRIGGERS = y || RFKILL = LEDS_TRIGGERS
	default y

config RFKILL_INPUT
	bool "RF switch input support" if EXPERT
	depends on RFKILL
	depends on INPUT = y || RFKILL = INPUT
	default y if !EXPERT

config RFKILL_GPIO
	tristate "GPIO RFKILL driver"
	depends on RFKILL
	depends on GPIOLIB || COMPILE_TEST
	default n
	help
	  If you say yes here you get support of a generic gpio RFKILL
	  driver.

```
在 Linux 内核配置中，使用 `.config` 文件来设置这些选项。以下是具体的设置方法：

## 1. 设置 RFKILL 相关配置


```bash
# 启用 RFKILL 子系统
CONFIG_RFKILL=y

# 启用 LED 触发支持（可选）
CONFIG_RFKILL_LEDS=y

# 启用输入支持（可选，用于键盘快捷键控制）
CONFIG_RFKILL_INPUT=y

# 启用 GPIO 驱动（如果需要GPIO控制射频开关）
CONFIG_RFKILL_GPIO=y
```

## 2. 设置方法

### 方法一：直接编辑 .config 文件
```bash
# 编辑内核配置文件
vi .config

# 添加或修改以下行：
CONFIG_RFKILL=y
CONFIG_RFKILL_LEDS=y
CONFIG_RFKILL_INPUT=y
CONFIG_RFKILL_GPIO=y
```

### 方法二：使用 menuconfig
```bash
cd /path/to/your/kernel/source
make menuconfig
```

在菜单中导航到：
```
Networking support --->
  [*] RF switch subsystem support --->
    [*] RF switch input support
    [*] GPIO RFKILL driver
```

### 方法三：使用配置脚本
```bash
# 在内核源码目录中
scripts/config --file .config --enable RFKILL
scripts/config --file .config --enable RFKILL_LEDS
scripts/config --file .config --enable RFKILL_INPUT
scripts/config --file .config --enable RFKILL_GPIO
```

## 3. 配置说明

### 三态选项（tristate）：
- `y` - 编译进内核
- `#` - 不启用（注释掉）

### 布尔选项（bool）：
- `y` - 启用
- `#` - 不启用（注释掉）

## 4. 针对 WiFi 模块的建议配置

对于你的 ATBM USB WiFi 模块，推荐的配置是：

```bash
# RFKILL 子系统支持
CONFIG_RFKILL=y

# LED 触发支持（用于RF开关状态指示）
CONFIG_RFKILL_LEDS=y

# 输入支持（如果需要键盘快捷键控制）
CONFIG_RFKILL_INPUT=y

# GPIO 驱动（如果硬件有GPIO控制的RF开关）
# CONFIG_RFKILL_GPIO is not set
```

## 5. 验证配置

设置完成后，重新编译内核：

```bash
# 清理之前的编译
make clean

# 重新配置
make menuconfig  # 或使用你的配置

# 编译内核
make -j$(nproc)
```

## 6. 配置依赖关系

注意依赖关系：
- `RFKILL_LEDS` 需要 `RFKILL` 支持
- `RFKILL_INPUT` 需要 `RFKILL` 支持
- `RFKILL_GPIO` 需要 `RFKILL` 和 `GPIOLIB` 支持

