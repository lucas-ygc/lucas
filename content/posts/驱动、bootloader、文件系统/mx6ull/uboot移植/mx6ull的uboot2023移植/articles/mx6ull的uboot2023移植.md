---
title: mx6ull的uboot--2023版本移植
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux驱动学习
abbrlink: a8487789
typora-root-url: ./..\..\..
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---

# 获取uboot源码
https://github.com/nxp-imx
nxp官方维护的仓库
拿到源码，编译。略

# 采用和我芯片一样的模板编译
编译mx6ull_14x14x_evk_defconfig
编译后直接搜索mx6ull_14x14x_evk_defconfig


# 和之前移植有一些心得
arch/arm/dts中，添加自己的设备树文件后，要在这个文件夹下有个makefile中添加上自己的设备树
这里改好还要去arch/arm/mach-imx/Kconfig中添加自己的设备树配置项,不然设备树还是编译不到。里面还要
配置自己板子的Kconfig
