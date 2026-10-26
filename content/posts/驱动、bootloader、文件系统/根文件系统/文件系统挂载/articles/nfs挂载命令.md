---
title: nfs挂载跟文件系统
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux驱动学习
abbrlink: 661705ae
typora-root-url: ./..\..\..
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---

# nfs挂载第一种方法（用于调试，会跳过引导，导致不会执行rs文件）
```shell
setenv bootargs 'console=ttymxc0,115200 root=/dev/nfs nfsroot=192.168.8.217:/home/ygc/Desktop/project/nfs/rootfs,rw,nfsvers=3,proto=tcp ip=192.168.8.120:192.168.8.217:192.168.8.1:255.255.255.0::eth0:off init=/bin/sh nfsdebug=7'
```

# nfs挂载第二种方法（用于生产）
```shell
setenv bootargs 'console=ttymxc0,115200 root=/dev/nfs nfsroot=192.168.8.217:/home/ygc/Desktop/project/nfs/rootfs,rw,sync,nfsvers=3,proto=tcp ip=192.168.8.120:192.168.8.217:192.168.8.1:255.255.255.0::eth0:off  nfsdebug=7'
```