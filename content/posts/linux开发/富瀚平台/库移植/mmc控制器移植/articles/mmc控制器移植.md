---
title: 富瀚mmc移植
type: categories
categories: linux开发
abbrlink: fc7f7e68
cover: "../images/封面.png"
date: 2022-09-29 00:00:00
description:
---


# mmc 移植
linux自带的无法对出错的mmc进行处理，需要自己移植mmc工具，参考mmc-utils

# 编译脚本：

```shell
#!/bin/bash

CC=/home/tuling/.FuHan-arm-linux/opt/arm-fullhanv3-linux-uclibcgnueabi-b6/bin/arm-fullhanv3-linux-uclibcgnueabi-gcc
CROSS_COMPILE=/home/tuling/.FuHan-arm-linux/opt/arm-fullhanv3-linux-uclibcgnueabi-b6/bin/arm-fullhanv3-linux-uclibcgnueabi
ARCH=arm
export CC=/home/tuling/.FuHan-arm-linux/opt/arm-fullhanv3-linux-uclibcgnueabi-b6/bin/arm-fullhanv3-linux-uclibcgnueabi-gcc
export CROSS_COMPILE=/home/tuling/.FuHan-arm-linux/opt/arm-fullhanv3-linux-uclibcgnueabi-b6/bin/arm-fullhanv3-linux-uclibcgnueabi
export ARCH=arm
build()
{
        cd mmc-utils
        make clean
        make CROSS_COMPILE=/home/tuling/.FuHan-arm-linux/opt/arm-fullhanv3-linux-uclibcgnueabi-b6/bin/arm-fullhanv3-linux-uclibcgnueabi
        cd ..
}
if [ -d "mmc-utils" ];then
        build
else
        git clone https://git.kernel.org/pub/scm/utils/mmc/mmc-utils.git
        cd setup-tools/mmc
fi
```