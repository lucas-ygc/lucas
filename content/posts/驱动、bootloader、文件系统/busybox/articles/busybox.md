---
title: busybox
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux驱动学习
abbrlink: 8507fae1
typora-root-url: ./..\..\..
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---


# 将rootfs打包到内核启动
根文件目录下默认编译出来时linuxrc,需要改为init。
```shell
进入根文件目录打包
        cd $rootdir/../pack/rootfs
        sudo chmod -R 777 .
        sudo chown -R root:root .
        mv linuxrc init
        chmod +x init
        find . | cpio -o -H newc > ../rootfs.cpio
        cd ../
        chmod 644 rootfs.cpio
```

# 更改命令提示符
```shell
PS1='TuLing# '
```