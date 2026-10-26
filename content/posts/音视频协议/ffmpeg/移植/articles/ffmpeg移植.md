---
title: ffmpeg移植
type: categories
categories: 音视频协议
description: 音视频原理
swiper_index: 1
cover: "../images/封面.png"
abbrlink: 3a597416
date: 2022-09-29 00:00:00
---
# 1、音视频入门
## 1-1、视频
* 动画书
静态小人书，通过快速翻动，形成动态效果。--- 视频原理

* 视频
将一些列的静态影像以电信号的方式进行动态捕捉


# 一、扩展ffmpeg
```shell
ffmpeg -f v4l2 -r 30 -s 640x480 -i /dev/video0 -f alsa -ar 44100 -ac 2 -i default -c:v libx264 -preset medium -tune zerolatency -c:a aac -b:a 128k -f nut - | ffplay -
```
## ffmpeg移植
ffmpeg的移植依赖于x264和x265

### 1、移植x264
下载源码，创建build.sh脚本，内容如下。
```shell
#!/bin/bash
make clean
path="/home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/bin"
set_path=${PWD}/../
export PATH=${path}:$PATH
arm-none-linux-gnueabihf-gcc --version

./configure \
        --cross-prefix=arm-none-linux-gnueabihf- \
        --prefix=${set_path} \
    --host=arm-none-linux-gnueabihf \
    --enable-shared \
    --enable-static

make -j$(nproc)
make install
```
`--enable-static`没有会出现无法找到x264。
### 2、移植x265
* 安装需要的工具
```shell
sudo apt install yasm cmake cmake-curses-gui
```

* 在build文件夹下有一个arm-linux文件夹，在里面有一个crosscompile.cmake文件，这个是交叉编译的配置文件。
修改这个文件如下。

```shell
# CMake toolchain file for cross compiling x265 for ARM arch
# This feature is only supported as experimental. Use with caution.
# Please report bugs on bitbucket
# Run cmake with: cmake -DCMAKE_TOOLCHAIN_FILE=crosscompile.cmake -G "Unix Makefiles" ../../source && ccmake ../../source

set(CROSS_COMPILE_ARM 1)
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR armv7)

# specify the cross compiler
set(CMAKE_C_COMPILER /home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-gcc)
set(CMAKE_CXX_COMPILER /home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-g++)

# specify the target environment
SET(CMAKE_FIND_ROOT_PATH /home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/arm-none-linux-gnueabihf)

```
* CMAKE_FIND_ROOT_PATH 指定交叉编译工具链的一些库路径。

`要修改编译脚本中cmake -DCMAKE_TOOLCHAIN_FILE=./crosscompile.cmake -G "Unix Makefiles" ../../source && ccmake .`
将*.cmake改成自己的路径。这很重要，不然传参可能出错。
```shell

 BIN_INSTALL_DIR                  bin                                                                                                        
 CHECKED_BUILD                    OFF                                                                                                        
 CMAKE_BUILD_TYPE                 Release                                                                                                    
 CMAKE_INSTALL_PREFIX             /usr/local/x265    （这是本人设置的安装路径，可修改为你需要的安装路径）                                                                                       
 DETAILED_CU_STATS                OFF                                                                                                        
 ENABLE_AGGRESSIVE_CHECKS         OFF                                                                                                        
 ENABLE_ASSEMBLY                  ON                                                                                                         
 ENABLE_CLI                       ON                                                                                                         
 ENABLE_HDR10_PLUS                OFF                                                                                                        
 ENABLE_LIBNUMA                   ON                                                                                                         
 ENABLE_PIC                       OFF                                                                                                        
 ENABLE_PPA                       OFF                                                                                                        
 ENABLE_SHARED                    OFF    （这里默认是开启的，生成动态库，根据需要设置）                                                                                                        
 ENABLE_TESTS                     OFF                                                                                                        
 ENABLE_VTUNE                     OFF                                                                                                        
 FSANITIZE                                                                                                                                   
 LIBDL                            /opt/FriendlyARM/toolschain/4.5.1/arm-none-linux-gnueabi/sys-root/usr/lib/libdl.so    （不要漏了这个库，根据实际路径设置）                        
 LIB_INSTALL_DIR                  lib                                                                                                        
 NASM_EXECUTABLE                  /usr/bin/yasm    （yasm文件，在本文开头第一步已经安装好了）                                                                                              
 NO_ATOMICS                       OFF                                                                                                        
 NUMA_ROOT_DIR                    NUMA_ROOT_DIR-NOTFOUND                                                                                     
 STATIC_LINK_CRT                  OFF                                                                                                        
 WARNINGS_AS_ERRORS               OFF   

```
`源码默认支持软件浮点，修改为硬件浮点，需要修改cmake`

执行脚本，make

安装make install

### 
### 3、最后移植ffmpeg
下载源码github
```shell
git clone https://github.com/FFmpeg/FFmpeg.git
``` 
配置编译
这里有要加的--pkg-config="pkg-config --static",不加这个通不过编译，出现x264和x265的依赖问题.
```shell
 --pkg-config="pkg-config --static" 
```
配置上x265的路径，不然会报找不到x265的错误。
```shell
export PKG_CONFIG_PATH=${x265_path}/lib/pkgconfig 
```
```shell
#!/bin/bash

if [ "$1" = "arm-build" ]; then
make clean
path="/home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/bin"
set_out_path=${PWD}/../
x264_path=/home/ygc/Desktop/project/myproject/app-src/project/test/ffmpeg/x264_build/
x265_path=/home/ygc/Desktop/project/myproject/app-src/project/test/ffmpeg/x265_build/out
echo ${path}
echo ${set_path}

export PKG_CONFIG_PATH=${x264_path}/lib/pkgconfig:$PKG_CONFIG_PATH
echo "PKG_CONFIG_PATH is now: $PKG_CONFIG_PATH"


# ./configure --cross-prefix=arm-linux-gnueabihf- --enable-cross-compile --target-os=linux --cc=arm-linux-gnueabihf-gcc --arch=arm --prefix=/home/xfy/FFmpeg/ffmpeg_install --enable-shared --disable-static --enable-gpl --enable-nonfree --disable-ffplay --enable-swscale --enable-pthreads --disable-armv5te --disable-armv6 --disable-armv6t2 --disable-x86asm --disable-stripping --enable-libx264 --extra-cflags=-I/home/xfy/FFmpeg/x264_install/include --extra-ldflags=-L/home/xfy/FFmpeg/x264_install/lib --extra-libs=-ldl

export PKG_CONFIG_PATH=/home/ygc/Desktop/project/myproject/app-src/project/test/ffmpeg/x264_build/lib/pkgconfig
# 添加 x265 的 pkg-config 路径
export PKG_CONFIG_PATH=${x265_path}/lib/pkgconfig
pkg-config --modversion x264
pkg-config --exists x264 && pkg-config --cflags --libs x264

ls ${x264_path}/include/x264.h
ls ${x264_path}/lib/libx264.so
ls ${x264_path}/lib/pkgconfig/x264.pc
# ./configure \
     ./configure \
    --prefix=${set_out_path} \
    --enable-cross-compile \
    --pkg-config="pkg-config --static" \
    --cross-prefix=${path}/arm-none-linux-gnueabihf- \
    --extra-cflags="-I${x264_path}/include -I${x265_path}/include" \
    --extra-ldflags="-L${x264_path}/lib -L${x265_path}/lib" \
    --arch=arm \
    --disable-x86asm \
    --cc=arm-none-linux-gnueabihf-gcc \
    --target-os=linux \
    --enable-gpl \
    --enable-libx264 \
    --enable-shared \
    --disable-static \
    --enable-libx265 \
    --extra-libs=-ldl
    make -j$(nproc)
    sudo make install
fi

if [ "$1" = "x86-build" ]; then
make clean
set_path=${PWD}/../
echo ${set_path}
sudo apt-get update
sudo apt-get install nasm libfdk-aac-dev libx264-dev libx265-dev libvpx-dev libmp3lame-dev libopus-dev
./configure \
    --prefix=${set_path} \
    --enable-gpl \
    --enable-libx264 \
    --enable-libx265 \
    --enable-libvpx \
    --enable-libfdk-aac \
    --enable-nonfree \
    --enable-libmp3lame \
    --enable-libopus
    make -j$(nproc)
    sudo make install
fi
```