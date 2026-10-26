---
title: lcd多点触摸屏
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: lcd多点触摸屏
abbrlink: a8a22b35
typora-root-url: ./..\..\..
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---

# lcd多点触摸屏
## linux内核中分为两类
Type A：适用于触摸点不能被区分或者追踪，此类型的设备上报原始数据(此类型在实际使
用中非常少！)。
Type B：适用于有硬件追踪并能区分触摸点的触摸设备，此类型设备通过 slot 更新某一个
触摸点的信息，FT5426 就属于此类型，一般的多点电容触摸屏 IC 都有此能力。
触摸点的信息通过一系列的 ABS_MT 事件(有的资料也叫消息)上报给 linux 内核，只有
ABS_MT 事件是用于多点触摸的。
