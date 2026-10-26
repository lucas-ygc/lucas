---
title: rootfs移植
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux驱动学习
abbrlink: c1179e11
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---


#  编译选项
```shell 
1、
Location:
        ->Settings
                ->vi-style line editor commands
# 选中

2、
Location:
        ->Settings
                ->Build static binary (no shared libs)
# 这个主要是选择是否动态编译，不能选

3、
Location:
        ->Linux Module Utilities
                ->Simplified module 
#  不能选

4、
Location:
        ->Linux System Utilities
                ->mdev(16kb) 
                # 下面的全选
5、
Location:
        ->Settings
                        ->Support Unicode
                        ->Check $LC_ALL, $LC_CTYPE, $LANG environment variables 
                        # 选择这两个

```
# 内核启动脚本
## 热插拔管理
热插拔主要由/proc/sys/kernel/hotplug控制
主要两种方法：mdev和udev

rcS
```shell
#!/bin/sh
PATH=/sbin:/bin:/usr/sbin:/usr/bin:$PATH
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/lib:/usr/lib
export PATH LD_LIBRARY_PATH

mount -a
mkdir /dev/pts
mount -t devpts devpts /dev/pts
echo /sbin/mdev > /proc/sys/kernel/hotplug
mdev -s
```

fstab
```shell
 #<file system> <mount point> <type> <options> <dump> <pass>
 proc            /proc          proc    defaults 0      0
 tmpfs          /tmp            tmpfs defaults   0      0
 sysfs            /sys          sysfs defaults  0       0
```


这里巨坑
一定要将编译工具链下的lib全部拷贝，不管so.什么
file 一下看看是不是有什么文件没有拷过去，一定要把需要的全部拷贝，最重要的就是

# 附录
移植脚本
```shell

export CROSS_COMPILE=/home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-
export ARCH=arm
curpath=$(pwd)

build() {

	if [ $1 == "clean" ];
	then
	echo "clean"
		make clean
	fi
	make defconfig
	# make menuconfig 添加配置
	cp ./rootfs-re ./rootfs -rf
	make -j$(nproc)
	make install CONFIG_PREFIX=${curpath}/rootfs/output

	cp -rf ${curpath}/rootfs-init/* ${curpath}/output/
	rm -rf /home/ygc/Desktop/project/nfs/*
	cp -rf ${curpath}/rootfs/output /home/ygc/Desktop/project/nfs/
	mv /home/ygc/Desktop/project/nfs/output /home/ygc/Desktop/project/nfs/rootfs

	cd /home/ygc/Desktop/project/nfs/rootfs 
	mkdir -p lib
	cp /home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/arm-none-linux-gnueabihf/lib/* lib/ -d
	cp /home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/arm-none-linux-gnueabihf/lib/*.* lib/ -d
	cp /home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/arm-none-linux-gnueabihf/libc/lib/* lib/ -d
	cp /home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/arm-none-linux-gnueabihf/libc/lib/*.* lib/ -d

	mkdir -p usr/lib
	cp /home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/arm-none-linux-gnueabihf/libc/usr/lib/*.a usr/lib/ -d
	cp /home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/arm-none-linux-gnueabihf/libc/usr/lib/*.so usr/lib/ -d

	mkdir -p dev bin mnt proc sys root tmp var etc

	sudo chmod 777 -Rf /home/ygc/Desktop/project/nfs/rootfs
}

if [ -f "rootfs" ]; then
	echo "rootfs exists"
else
	echo "rootfs does not exist"
	if [ -f "busybox-1.35.0.tar.bz2" ];then
        	echo "busybox-1.35.0.tar.bz2 exists"
		if [ -d "rootfs" ]; then
			echo "rootfs exists"
			cd rootfs
			build $1
		else
			echo "rootfs does not exist"
			tar -xvjf busybox-1.35.0.tar.bz2 
			mv busybox-1.35.0 rootfs
			cd rootfs
			build $1
		fi
		
	else
        	echo "busybox-1.35.0.tar.bz2 does not exist"
        	wget https://busybox.net/downloads/busybox-1.35.0.tar.bz2
		tar -xvjf busybox-1.35.0.tar.bz2 
		mv busybox-1.35.0 rootfs
		cd rootfs
		build $1
	fi
fi
```