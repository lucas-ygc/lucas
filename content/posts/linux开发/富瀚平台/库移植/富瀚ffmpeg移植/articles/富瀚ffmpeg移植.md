---
title: 富瀚ffmpeg移植
type: categories
categories: linux开发
abbrlink: d35c4abc
cover: "../images/封面.png"
date: 2022-09-29 00:00:00
description:
---

编译脚本：
```shell
rm -rf ffmpeg

# sudo chown $USER:$USER /output
output=${PWD}/output
rm -rf output
mkdir -p ./output
build_ffmpeg() {
cd ffmpeg
# make distclean
export PATH=/home/tuling/.FuHan-arm-linux/opt/arm-fullhanv3-linux-uclibcgnueabi-b6/bin:$PATH
CROSS_COMPILE=/home/tuling/.FuHan-arm-linux/opt/arm-fullhanv3-linux-uclibcgnueabi-b6/bin/arm-fullhanv3-linux-uclibcgnueabi-
export CC=${CROSS_COMPILE}gcc
export CXX=${CROSS_COMPILE}g++
export AR=${CROSS_COMPILE}ar
export AS=${CROSS_COMPILE}as
export LD=${CROSS_COMPILE}ld
# export STRIP=${CROSS_COMPILE}strip
echo $CC
# ./configure \
#   --prefix=$output \
#   --target-os=linux \
#   --arch=arm \
#   --cross-prefix=${CROSS_COMPILE} \
#   --enable-cross-compile \
#   --disable-x86asm \
#   --disable-shared \
#   --enable-static \
#   --disable-programs \
#   --disable-doc \
#   --disable-ffmpeg \
#   --disable-ffplay \
#   --disable-ffprobe \
#   --enable-pic \
#   --disable-symver \
#   --disable-everything \
#   --enable-muxer=mp4 \
#   --enable-muxer=hevc \
#   --enable-muxer=aac \
#   --enable-neon \
#   --enable-debug \
#   --enable-bsf=h264_mp4toannexb,aac_adtstoasc \
#   --enable-protocol=file \
#   --disable-asm  \
#   --extra-ldflags="-mfloat-abi=hard -Wl,--no-warn-mismatch" \
#   --extra-cflags="-march=armv7-a -mfpu=neon-vfpv4 -mfloat-abi=hard" \

  
# ./configure \
#   --prefix=$output \
#   --target-os=linux \
#   --arch=arm \
#   --cross-prefix=${CROSS_COMPILE} \
#   --enable-cross-compile \
#   --disable-x86asm \
#   --disable-shared \
#   --enable-static \
#   --disable-programs \
#   --disable-doc \
#   --disable-ffmpeg \
#   --disable-ffplay \
#   --disable-ffprobe \
#   --enable-pic \
#   --disable-symver \
#   --disable-everything \
#   --enable-muxer=avi \
#   --enable-encoder=msmpeg4v2 \
#   --enable-encoder=msmpeg4 \
#   --enable-encoder=pcm_s16le \
#   --enable-muxer=mp4 \
#   --enable-muxer=matroska \
#   --enable-muxer=webm \
#   --enable-muxer=hevc \
#   --enable-muxer=aac \
#   --enable-neon \
#   --enable-debug \
#   --enable-bsf=h264_mp4toannexb,aac_adtstoasc \
#   --enable-protocol=file \
#   --disable-asm \
#   --extra-ldflags="-mfloat-abi=hard -Wl,--no-warn-mismatch" \
#   --extra-cflags="-march=armv7-a -mfpu=neon-vfpv4 -mfloat-abi=hard"
./configure \
  --prefix=$output \
  --target-os=linux \
  --arch=arm \
  --cross-prefix=${CROSS_COMPILE} \
  --enable-cross-compile \
  --disable-x86asm \
  --disable-shared \
  --enable-static \
  --disable-programs \
  --disable-doc \
  --disable-ffmpeg \
  --disable-ffplay \
  --disable-ffprobe \
  --disable-symver \
  --disable-everything \
  --enable-muxer=mp4 \
  --enable-demuxer=mp4 \
  --enable-demuxer=mov \
  --enable-muxer=hevc \
  --enable-demuxer=hevc \
  --enable-parser=hevc \
    --enable-decoder=aac \
  --enable-encoder=pcm_s16le \
  --enable-debug \
  --enable-bsf=h264_mp4toannexb \
    --enable-bsf=h264_mp4toannexb,aac_adtstoasc,hevc_mp4toannexb \
  --enable-protocol=file \
  --extra-ldflags="-mfloat-abi=hard -Wl,--no-warn-mismatch" \
  --extra-cflags="-march=armv7-a -mfpu=neon-vfpv4 -mfloat-abi=hard"
# 避免汇编代码绕过浮点ABI检查
# ./configure \
#   --enable-cross-compile \
#   --arch=armv7-a \
#   --target-os=linux \
#   --cross-prefix=arm-fullhanv3-linux-uclibcgnueabi- \
#   --extra-cflags="-mfloat-abi=hard -mfpu=neon-vfpv4 -fPIC" \
#   --extra-ldflags="-mfloat-abi=hard -Wl,--no-warn-mismatch" \
# make -j$(nproc)

make -j$(nproc)
make install

}


if [ -d "ffmpeg" ]; then
  echo "FFmpeg exists"
else
   git clone https://gitee.com/mirrors/ffmpeg.git ffmpeg
   cd ffmpeg
  #  git checkout n3.4
  git checkout n4.4
    # git checkout   n6.0
fi

build_ffmpeg

```