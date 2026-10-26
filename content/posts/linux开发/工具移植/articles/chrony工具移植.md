---
title: chrony工具移植
type: categories
categories: linux开发
cover: "../images/封面.png"
swiper_index: 1
abbrlink: 5b931532
sticky: 1
typora-root-url: ./..\..\..
date: 2022-10-29 00:00:00
description:
---
# chrony工具移植

```shell
#!/bin/bash

# 设置交叉编译环境
export PATH=/usr/local/go/bin:$PATH
export CROSS_COMPILE=/home/tuling/project/optTL/fuhanV500/arm-fhv512c-linux-uclibcgnueabihf-b2/bin/arm-fhv512c-linux-uclibcgnueabihf-
export PATH=/home/tuling/project/optTL/fuhanV500/arm-fhv512c-linux-uclibcgnueabihf-b2/bin:$PATH

name=arm-fhv512c-linux-uclibcgnueabihf

# 设置编译器和链接器
export CC=${name}-gcc
export CXX=${name}-g++
export AR=${name}-ar
export AS=${name}-as
export RANLIB=${name}-ranlib
export LD=${name}-ld
export STRIP=${name}-strip

# 设置编译标志
export CFLAGS="-Wno-psabi -mcpu=cortex-a7 -mfloat-abi=hard -mfpu=neon-vfpv4 -fno-aggressive-loop-optimizations"
export CXXFLAGS="-Wno-psabi -mcpu=cortex-a7 -mfloat-abi=hard -mfpu=neon-vfpv4 -fno-aggressive-loop-optimizations"
export LDFLAGS="-lpthread"      

# 输出目录
output=${PWD}/output
mkdir -p ${output}

# 构建函数
buildchronyd() {
    echo "开始编译 chronyd..."

    # 显式传递交叉编译器参数
    ./configure \
        --host=arm-fhv512c-linux-uclibcgnueabihf \
        # --prefix=../output \
        --disable-cmdmon \
        --disable-refclock \
        CC=${CC} \
        CXX=${CXX} \
        AR=${AR} \
        AS=${AS} \
        RANLIB=${RANLIB} \
        LD=${LD} \
        STRIP=${STRIP}

    make clean
    make
    make install DESTDIR=${output} 
}

# 检查并克隆源码
if [ ! -d "chrony" ]; then
    echo "chrony does not exist"
    git clone https://gitlab.com/chrony/chrony.git
else
    echo "chrony exists"
fi

cd chrony
buildchronyd
```


# 测试
```shell
cat > /etc/chrony.conf << 'EOF'
server ntp.aliyun.com
server time.aliyun.com
server ntp.tencent.com
pidfile /var/run/chronyd.pid
dumpdir /var/lib/chrony
dumponexit yes
makestep 1000 20
rtcsync
EOF

/mnt/chronyd -d > /var/log/chronyd.log 2>&1 &
```
