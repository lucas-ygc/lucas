---
title: 嵌入式视觉模型进阶 05：ShuffleNet：通道拆分与重排
date: 2026-10-24 00:00:00
categories: AI-深度学习
tags:
  - 嵌入式视觉模型进阶
  - 计算机视觉
  - 嵌入式部署
description: 通过通道编号追踪 shuffle 的作用，观察分组之间的信息交换与复制成本。
abbrlink: edge-vision-05-channel-shuffle
draft: false
cover: ../images/封面.svg
code:
  inline: true
  files:
    - main.py
    - README.md
    - requirements.txt
    - verification.md
    - .gitignore
  experiments:
    - id: practice
      title: 实验：ShuffleNet：通道拆分与重排
      file: main.py
      command: python3 main.py
---

> **第 5 / 30 课。** 前置：[上一课](/posts/edge-vision-04-mobilenetv3-se.html)。本篇的运行范围以实验说明和验证记录为准，构造样例不代表真实任务精度或板端性能。

## 分组减少连接，也限制交流

分组卷积把通道分到不同组，每组独立计算。如果连续两层始终使用相同分组，各组之间就缺少直接信息交流。channel shuffle 通过重新排列通道，让下一层分组接收到来自不同旧组的特征。

假设通道为 `[0,1,2,3,4,5,6,7]`，分两组后 reshape 为 `[2,4]`，交换组轴和组内轴再展平，得到 `[0,4,1,5,2,6,3,7]`。这些数字表示原通道身份，不是计算后的新特征值。

## 拆分、处理和拼接

ShuffleNetV2 的 stride=1 代表模块把通道拆成两半，一半直通，一半处理，然后拼接并 shuffle。降采样模块需要另行设计两个分支，不能把直通半支直接与缩小后的另一半拼接。

本课代码实现同形状的教学模块，重点是追踪信息流。它没有覆盖完整网络所有 stage 和降采样细节。

## 连续内存与真实成本

transpose 往往只是改变步幅。后续展平若需要连续内存，`contiguous()` 可能触发真实复制。参数为零的操作仍可能消耗带宽。部署时检查 compiler 是否能消除重排，或者是否产生额外 CPU 与 NPU 交接。

## 练习

先手算 groups=4 时的通道顺序，再运行代码核对。把 channels 改成奇数，看拆分分支为什么不能直接复用。

参考结论：groups=4 得到 `[0,2,4,6,1,3,5,7]`。本教学块要求偶数通道，以保持两支等宽；不同设计可以取消这个限制，但需要同步修改卷积与拼接契约。

## 配套实验与运行记录

```experiment
practice
```

在本篇代码目录执行 `python3 main.py`。依赖安装、可选入口见包内 `README.md`；实际运行结果见 [`verification.md`](/posts/edge-vision-05-channel-shuffle/code/verification.md.html)。下载包包含本课使用的辅助模块与样例。

## 参考与进一步阅读

[原始论文或官方文档](https://arxiv.org/abs/1807.11164)用于核对结构、接口和适用范围。本篇代码是围绕教学目标编写的最小实验；除明确注明的完整入口外，不视为对应论文模型的完整复现。

---

[完整进阶目录](/series/edge-vision-advanced/) · [入门系列](/series/vision-learning/) · [上一篇](/posts/edge-vision-04-mobilenetv3-se.html) · [下一篇](/posts/edge-vision-06-reparameterization.html)
