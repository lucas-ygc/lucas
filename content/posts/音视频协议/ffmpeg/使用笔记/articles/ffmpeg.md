---
title: ffmpeg
type: categories
categories: 音视频协议
description: ffmpeg
swiper_index: 1
abbrlink: 2ffce39e
typora-root-url: ./..\..\..
cover: "../images/封面.png"
date: 2022-09-29 00:00:00
---
# 示例
ffplay -ar 8000 -ac 1 -f mulaw out.g711u
-ar 指定音频采样率
-ac 指定音频声道数
-f 指定音频格式，这里使用mulaw格式

将wav音频转换为mulaw格式(g711u)
ffmpeg -i input.wav -ar 8000 -ac 1 -acodec pcm_mulaw output.ulaw
-i 指定输入文件
-ar 指定音频采样率
-ac 指定音频声道数
-acodec 指定音频编码格式，这里使用pcm_mulaw

将mp3音频转换为wav格式，再转为mulaw格式才行，直接转有概率转的不对
ffmpeg -i song.mp3 -ar 8000 -ac 1 -ab 8 song.wav
-i 指定输入文件
-ar 指定音频采样率
-ac 指定音频声道数
-ab 指定音频码率

# PCM（脉冲编码调制）在FFmpeg中有以下常见类型：


pcm_s16le
16位有符号小端格式（Signed 16-bit Little Endian），常用于WAV文件的默认编码。

pcm_s16be
16位有符号大端格式（Signed 16-bit Big Endian），适用于特定硬件或协议需求。

pcm_u8
8位无符号格式（Unsigned 8-bit），数据范围0-255，音质较低但兼容老设备。

pcm_mulaw
G.711 μ-law编码，用于电话音频压缩，压缩比高但音质有限（如示例中的pcm_mulaw）。

pcm_alaw
G.711 A-law编码，与μ-law类似，适用于欧洲和中国的电话系统。

pcm_f32le/pcm_f64le
32/64位浮点格式（Float 32/64-bit LE），用于高精度音频处理。


