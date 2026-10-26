---
title: AAC音频格式详解
type: categories
categories: 音视频协议
description: AAC音频格式详解
swiper_index: 1
abbrlink: f2d77ef1
typora-root-url: ./..\..\..
cover: "../images/封面.png"
date: 2022-09-29 00:00:00
---

# 1、格式头
头名字叫ADTS,如下格式：
```
aac_data:ff f9 6c 40 16 ff fc 1 8 9e d8 12 76 2c 12 41 e8 ff 0 43 5d 43 49 48 5 92 b1 b2 85 ae ce 47 65 93 15 c6 cb a0 a8 82 b7 a 4e e0 cf 15 99 b0 66 fc c6 79 5e 6a 7e 74 93 1e 4d 9b 5c 4e f2 ca 7d d1 3a 77 b3 6b 29 54 51 bc fe 9e 72 77 91 19 ab 18 85 ad 10 9c 56 b6 87 6b d4 40 14 e5 d5 99 a 4b 1f 5d
```
以ff f9开头。储存了音频的采样率、声道数、采样位数等信息。长度为7个字节。

如果要将 AAC 数据通过 RTP 发送，一般都需要 ADTS。
如果要写入 .aac 文件供播放器识别，也需要 ADTS。
如果要写入 MP4，则应去掉 ADTS，改用 AAC LATM 或容器本身的描述方式。

第一个字节固定ff。