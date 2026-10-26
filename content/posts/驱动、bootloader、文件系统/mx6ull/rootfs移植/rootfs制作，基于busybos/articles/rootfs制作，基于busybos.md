---
title: rootfs移植-详细
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux驱动学习
abbrlink: 6d5e5a8
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---



主要介绍做中文支持和启动内核后的init脚本

有关于启动的脚本提前在这里说明：
```shell
setenv bootargs 'console=ttymxc0,115200 root=/dev/nfs nfsroot=192.168.8.217:/home/ygc/Desktop/project/nfs/rootfs,rw,nfsvers=3,proto=tcp ip=192.168.8.120:192.168.8.217:192.168.8.1:255.255.255.0::eth0:off init=/bin/sh nfsdebug=7'
```
初始化脚本 init= 什么可以不指定，就可以让系统判断。


# 1、下载源码，官网下载
比较简单，略

## 1-1、添加中文支持
printable_string.c中
将下面删除
```c
if (c >= 0x7f)
			break;
```
往下找
下面
```c
		break;
			if (c < ' ' || c >= 0x7f)
				*d = '?';
			d++;
```
改为
```c
	break;
			if (c < ' ')
				*d = '?';
			d++;    
```

unicode.c中
```c
	/* *d++ = (c >= ' ' && c < 0x7f) ? c : '?'; */
				*d++ = (c >= ' ') ? c : '?';
				src++;
```
下面还有一个
```c
/* if (c < ' ' || c >= 0x7f) */
				if (c < ' ')
					*d = '?';
				d++;
```
# 2、编译源码
makefie文件在源码目录下，修改makefie文件，指定交叉编译器
```
CROSS_COMPILE ?= 指定编译器地址
ARCH ?= arm
```

或者脚本编译
```shell
#!/bin/bash
path="/home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/bin"
export "CC=gcc CROSS_COMPILE=${path}/arm-none-linux-gnueabihf-"
export 
make defconfig
make menuconfig
```
# 3、添加中文支持
查看1.1：
/libbb/printable_string.c下
函数 printable_string
将关于0x7f的判断去掉
接着将ibbb/unicode.c中
在unicode_conv_to_printable2函数中
将关于0x7f的判断去掉


# 4、修改配置
##  4-1、先默认配置
```
make defconfig
```
## 4-2、打开图形配置界面

```
make menuconfig
```

4-3、选择编译的方式

* 这里需要选择动态编译，选择静态编译的话DNS会出现问题
```

Location:
-> Settings       
    -> Build static binary (no shared libs) 不要选
```

* 允许使用vi
```
Location :
-> Setting
    -> vi-style line editing commands
```

* 简化驱动加载，这个要取消
```
Location :
-> linux Module Utilities
    ->Simplified modules

```

* 将mdev工具全部打开
```

Location :
->Linux System Utilities
    ->mdev(16kb)
    包括子项全部打开

```

* 使能busybox的unicode编码以支持中文
```

Location :
->Settings
    ->support unicode
    ->Check $LC_ALL,$LANG, $LC_CTYPE environment variables

```


* 编译安装
```
make

make install CONFIG_PREFIX=/home/ygc/Desktop/project/nfs/rootfs

```

生成了rootfs下几个文件bin sbin usr linuxr,linux内核的lnit进程会去查找用户空间的init程序，找到以后会运行这用户空间init程序，从而切换到用户态，如果bootargs设置了init=/linuxrc，那么linuxrc就是可以作为用户空间的init程序，所以用户空间的init程序是busybox来生成的

# 5、想rootfs下/lib目录库文件
* 1、创建/lib目录和/usr/lib目录
```
mkdir lib
```
* 2、将交叉编译器中的库文件都复制过来
进入编译工具工具链下的libc/lib和lib目录下，将lib下的所有文件复制到rootfs/lib目录下,如果有链接文件，要把被链接文件也复制过去。

/usr/lib文件在工具链的libc/usr/lib目录下，复制到rootfs/usr/lib目录下。

# 6、完成创建其他的文件
```shell
mkdir dev proc mnt sys tmp root etc
```

* 在rootfs目录下创建etc/init.d/rcS文件，内容如下：
```/etc/init.d/rcS
#!/bin/bash

PATH=/sbin:/bin:/usr/sbin:/usr/bin:$PATH
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/lib:/usr/lib
export PATH LD_LIBRARY_PATH

mount -a
mkdir /dev/pts
mount -t devpts devpts /dev/pts
echo /sbin/mdev > /proc/sys/kernel/hotplug
mdev -s
```

* 创建/etc/fstab文件，内容如下：
```/etc/fstab
#<file system>   <mount point>     <type>       <options>       <dump>          <pass>
proc            /proc              proc         defaults        0               0
tmpfs           /tmp               tmpfs        defaults        0               0
sysfs           /sys               sysfs        defaults        0               0
```
* 创建/etc/inittab文件
```/etc/inittab
#etc/inittab

::sysinit:/etc/init.d/rcS
console::askfirst:-/bin/sh
::restart:/sbin/init
::ctrlaltdel:/sbin/reboot
::shutdown:/bin/umount -a -r
::shutdown:/sbin/swapoff -a
```


# 7、设置环境变量，挂在根文件系统
```
setenv bootargs 'console=ttymxc0,115200 root=/dev/nfs nfsroot=192.168.8.9:/home/ygc/Desktop/project/nfs/rootfs,proto=tcp rw ip=192.168.8.120:192.168.8.9:192.168.8.1:255.255.255.0::eth0:off'

saveenv
```



