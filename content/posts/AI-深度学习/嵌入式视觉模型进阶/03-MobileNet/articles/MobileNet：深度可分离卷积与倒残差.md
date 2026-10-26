---
title: 嵌入式视觉模型进阶 03：MobileNet：深度可分离卷积与倒残差
date: 2026-10-24 00:00:00
categories: AI-深度学习
tags:
  - 嵌入式视觉模型进阶
  - 计算机视觉
  - 嵌入式部署
description: 实现 MobileNetV1 与 V2 的代表模块，理解扩展、深度卷积和线性投影。
abbrlink: edge-vision-03-mobilenet-blocks
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
      title: 实验：MobileNet：深度可分离卷积与倒残差
      file: main.py
      command: python3 main.py
---

> **第 3 / 30 课。** 前置：[上一课](/posts/edge-vision-02-convolution-variants.html)。本篇的运行范围以实验说明和验证记录为准，构造样例不代表真实任务精度或板端性能。

## 从减少空间卷积成本开始

V1 式模块先对各通道做 depthwise，再用 pointwise 交换通道信息。以 16→24、3×3 为例，普通卷积有 3456 个权重，可分离结构有 `16×9+16×24=528` 个，均忽略 BN 和偏置。这是结构选择，不是对原卷积的无损压缩。

## 为什么先变宽再变窄

V2 的代表模块先用 1×1 把通道扩展为隐藏维度，在较宽空间执行 depthwise，再用 1×1 投影回输出维度。扩展系数为 6 时，16 通道变为 96。中间特征更大，因此较少参数并不保证较少激活内存。

“倒残差”对应窄输入、宽中间、窄输出的残差结构。线性瓶颈强调最后的窄投影后不再接 ReLU6，以免进一步截断低维信息。它不是说整个模块没有非线性。

## 残差连接有条件

只有 stride=1 且输入输出通道相同时，示例模块才直接加回输入。16→24 或 stride=2 时不能直接相加。若另外添加投影捷径，就改变了本课要复现的模块约定。

运行代码分别检查同形状和降采样情形。参数初始化固定，但没有训练，因此本课只验证计算结构。

## 动手修改与部署关注点

把扩展系数从 6 改为 2，统计权重及隐藏激活元素。再在最后投影后错误地添加 ReLU6，对包含负值的输入比较输出分布。

参考结论：缩小扩展系数会降低中间通道与成本，但不能直接断言任务精度保持；修改激活意味着修改模型，必须重训或重新验证。实际部署还要检查 depthwise 内核效率及通道对齐要求。

## 配套实验与运行记录

```experiment
practice
```

在本篇代码目录执行 `python3 main.py`。依赖安装、可选入口见包内 `README.md`；实际运行结果见 [`verification.md`](/posts/edge-vision-03-mobilenet-blocks/code/verification.md.html)。下载包包含本课使用的辅助模块与样例。

## 参考与进一步阅读

[原始论文或官方文档](https://arxiv.org/abs/1801.04381)用于核对结构、接口和适用范围。本篇代码是围绕教学目标编写的最小实验；除明确注明的完整入口外，不视为对应论文模型的完整复现。

---

[完整进阶目录](/series/edge-vision-advanced/) · [入门系列](/series/vision-learning/) · [上一篇](/posts/edge-vision-02-convolution-variants.html) · [下一篇](/posts/edge-vision-04-mobilenetv3-se.html)
