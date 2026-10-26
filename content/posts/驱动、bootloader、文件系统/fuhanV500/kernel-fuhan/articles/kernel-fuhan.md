---
title: kernel-fuhan
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux驱动学习
abbrlink: d01ffb44
typora-root-url: ./..\..\..
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---

# kernel 开启硬件浮点
一般是在.config中开启 ,最好编译器也指定浮点类型。
性能：添加 NEON 优化选项可以进一步提升浮点运算性能


# 配置文件系统
为了方便，将文件系统打包到kernel中，并添加到根目录。
文件系统根目录下linuxur 要改为init。
否则需要在uboot中用参数传递"rdinit=/linuxrc"。指定启动程序

# 查看emmc是否正常工作
/dev/mmcblkp1 查看, 因为用的SD1接口，所以是mmcblkp1

# 驱动设备树配置
首先配置pinctrl，然后配置设备树。pinctrl是复用引脚的，一般这是第一步。