---
title: openssl和unzip和zip移植
type: categories
categories: linux开发
abbrlink: a003dbfe
cover: "../images/封面.png"
date: 2022-09-29 00:00:00
description:
---


# openssl 移植
编译脚本：
```shell
#!/bin/bash
make clean
mkdir output
export CC=/home/wangyp/project/dtcwyp/opt/arm-fullhanv3-linux-uclibcgnueabi-b6/bin/arm-fullhanv3-linux-uclibcgnueabi-gcc
./Configure \
            no-zlib \
            --shared \
            --prefix=$(pwd)/output openssl-1.0.2h \
            os/compiler:arm-fullhanv3-linux-uclibcgnueabi-b6 \
            -DOPENSSL_THREADS \
            -Wno-psabi -mcpu=cortex-a7 -mfloat-abi=hard -mfpu=neon-vfpv4 -fno-aggressive-loop-optimizations

make
make install
```


# 其他zip和unzip比较简单
略

# valgrind
```shell
#!/bin/bash
make clean
export PATH=$PATH:/home/tuling/.FuHan-arm-linux/opt/arm-fullhanv3-linux-uclibcgnueabi-b6/bin/
export CFLAGS="-Wno-psabi -mcpu=cortex-a7 -mfloat-abi=hard -mfpu=neon-vfpv4 -fno-aggressive-loop-optimizations"
export CXXFLAGS="-Wno-psabi -mcpu=cortex-a7 -mfloat-abi=hard -mfpu=neon-vfpv4 -fno-aggressive-loop-optimizations"
echo $PATH
./configure --host=arm-fullhanv3-linux-uclibcgnueabi  --prefix=$(pwd)/./output

make V=1
make install
```