---
title: mqtt
type: categories
categories: 网络
cover: "../images/封面.png"
description: mqtt笔记
swiper_index: 1
sticky: 1
typora-root-url: ./..\..\..
abbrlink: a100fb72
date: 2022-10-29 00:00:00
---


# 1、mqtt由来

解决问题：   
1、服务器必须实现的千万客户端的接入。    
2、单次数据量比较小，但不能出错。     
3、必须能够是适应高延迟，断网等不可靠风险。    
4、根据数据的重要程度和特性，设置不同等级的服务质量。(QoS0、QoS1、QoS2三种)    
5、可以保持长连接。   
6、低功耗场合不适合。   
7、建立在tcp上，非常可靠。    


## 1-1、关于第四条做说明


