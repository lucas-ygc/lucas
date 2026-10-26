---
title: 低版本内核适配exfat文件系统
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux驱动学习
abbrlink: 8b5bcc0c
typora-root-url: ./..\..\..
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---

# 低版本内核适配exfat文件系统
两种选择
1、exfat-nofuse --(社区版本) 
```shell
https://github.com/dorimanx/exfat-nofuse
```
2、exfat-linux --(三星维护的版本)

# exfat-nofuse
用于 exFAT、FAT12、FAT16 和 vfat （FAT32） 文件系统的 Linux 非熔断读/写内核驱动程序。
最初移植自 Android 内核 v3.0。



## 作为独立模块安装：
```shell
make
sudo make install
```
要手动加载驱动程序，请以 root 身份运行以下命令：
```shell
modprobe exfat
```

在我的例子中，您还可以使用CROSS_COMPILE标志指定自定义工具链：
```shell
CROSS_COMPILE=../dorimanx-SG2-I9100-内核/android-toolchain/bin/arm-eabi-
```
## 作为内核的一部分安装：
让我们以 [linux] 作为内核源代码 dir 的路径...
```shell
cd [linux]
cp -rvf exfat-nofuse [linux]/fs/exfat
```
编辑 [linux]/fs/Kconfig
```shell
 menu "DOS/FAT/NT Filesystems"

  source "fs/fat/Kconfig"
 +source "fs/exfat/Kconfig"
  source "fs/ntfs/Kconfig"
  endmenu
```
编辑 [linux]/fs/Makefile
```shell
  obj-$(CONFIG_FAT_FS)    += fat/
 +obj-$(CONFIG_EXFAT_FS)  += exfat/
  obj-$(CONFIG_BFS_FS)    += bfs/
```
```shell
cd [linux]
make menuconfig
```

# 工具集选择
选择三星的https://github.com/exfatprogs/exfatprogs.git工具。
