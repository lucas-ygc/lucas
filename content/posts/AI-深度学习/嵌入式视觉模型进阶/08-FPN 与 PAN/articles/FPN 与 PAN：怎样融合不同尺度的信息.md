---
title: 嵌入式视觉模型进阶 08：FPN 与 PAN：怎样融合不同尺度的信息
date: 2026-10-24 00:00:00
categories: AI-深度学习
tags:
  - 嵌入式视觉模型进阶
  - 计算机视觉
  - 嵌入式部署
description: 搭建自顶向下与自底向上的融合路径，检查相加、拼接和空间对齐。
abbrlink: edge-vision-08-fpn-pan
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
      title: 实验：FPN 与 PAN：怎样融合不同尺度的信息
      file: main.py
      command: python3 main.py
---

> **第 8 / 30 课。** 前置：[上一课](/posts/edge-vision-07-feature-pyramid.html)。本篇的运行范围以实验说明和验证记录为准，构造样例不代表真实任务精度或板端性能。

## 为什么不能直接把特征相加

C3、C4、C5 通道与分辨率不同。先用 1×1 横向投影把它们转为相同通道数，再把低分辨率特征插值到高分辨率层的实际大小，才能逐元素相加。相加要求所有维度兼容；拼接只要求除拼接轴以外的维度一致，并会增加通道数。

FPN 的典型思路是把深层信息逐级向高分辨率传播。PAN 类路径再把融合后的高分辨率信息向下聚合。具体模型会选择相加、拼接和不同卷积块，本课是最小路径演示，不是任意 YOLO neck 的逐层复刻。

## 追踪本课路径

输入通道为 32、64、128，统一成 24。先得到 P5，再计算 `P4=L4+up(P5)`、`P3=L3+up(P4)`。向下用 stride=2 的卷积，将 P3 加到 P4，再将结果加到 P5。

本课使用 17、9、5 的奇数尺寸，检验“按目标 size 插值”的必要性。若只是写 scale_factor=2，会出现 5→10 与 9 不匹配。

## 运行后应该看什么

输出层的空间大小不变、通道变为 24；反向梯度能到达每个输入层。使用随机特征只能验证结构，不能据此判断小目标效果。

## 修改任务与工程检查

把相加替换成 concat，先计算后续卷积的输入通道，再运行。将输出通道从 24 改为 48，记录权重和激活增长。交付 neck 的输入输出表，并说明为什么降低 backbone 成本后，neck 仍可能占据主要运行时间。

## 配套实验与运行记录

```experiment
practice
```

在本篇代码目录执行 `python3 main.py`。依赖安装、可选入口见包内 `README.md`；实际运行结果见 [`verification.md`](/posts/edge-vision-08-fpn-pan/code/verification.md.html)。下载包包含本课使用的辅助模块与样例。

## 参考与进一步阅读

[原始论文或官方文档](https://arxiv.org/abs/1803.01534)用于核对结构、接口和适用范围。本篇代码是围绕教学目标编写的最小实验；除明确注明的完整入口外，不视为对应论文模型的完整复现。

---

[完整进阶目录](/series/edge-vision-advanced/) · [入门系列](/series/vision-learning/) · [上一篇](/posts/edge-vision-07-feature-pyramid.html) · [下一篇](/posts/edge-vision-09-detection-head.html)
