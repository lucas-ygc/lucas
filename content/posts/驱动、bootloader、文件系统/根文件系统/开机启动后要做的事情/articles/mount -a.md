---
title: mount -a
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux驱动学习
abbrlink: e850795b
typora-root-url: ./..\..\..
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---

# mount -a
mount -a 命令用于挂载所有未挂载的已注册文件系统。扫描的文件来自fstable文件,没有这个，系统将不能正常工作。
1. 创建fstable文件
```shell
 #<file system> <mount point> <type> <options> <dump> <pass>
 proc            /proc          proc    defaults 0      0
 tmpfs          /tmp            tmpfs defaults   0      0
 sysfs            /sys          sysfs defaults  0       0
```
