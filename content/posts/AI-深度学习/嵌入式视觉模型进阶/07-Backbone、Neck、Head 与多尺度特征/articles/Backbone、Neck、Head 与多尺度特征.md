---
title: 嵌入式视觉模型进阶 07：Backbone、Neck、Head 与多尺度特征
date: 2026-10-24 00:00:00
categories: AI-深度学习
tags:
  - 嵌入式视觉模型进阶
  - 计算机视觉
  - 嵌入式部署
description: 从不同步长的特征图理解检测网络的分工与小目标信息。
abbrlink: edge-vision-07-feature-pyramid
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
      title: 实验：Backbone、Neck、Head 与多尺度特征
      file: main.py
      command: python3 main.py
---

> **第 7 / 30 课。** 前置：[上一课](/posts/edge-vision-06-reparameterization.html)。本篇的运行范围以实验说明和验证记录为准，构造样例不代表真实任务精度或板端性能。

## 三个角色不等于三个固定文件

Backbone 把图片变为多层特征；Neck 整合来自不同层的表示；Head 根据任务产生分类、位置或掩码输出。某些网络把这些角色混在同一模块中，读代码时应按数据作用识别，而不是只看类名。

本课构建五个 stride=2 的卷积 stage，输入 `[1,3,128,128]`。取第三、四、五层作为 C3、C4、C5，步长分别为 8、16、32，形状是 `[1,32,16,16]`、`[1,64,8,8]`、`[1,128,4,4]`。这里 C3 的编号是教学命名，不保证与所有网络一致。

## 一个特征格子不是一个像素

stride=8 表示相邻输出格在输入坐标中相距约 8 像素，不代表每个格只看 8×8 区域。感受野取决于整个前序网络。把小目标缩到不足几个像素后，后续上采样不能凭空恢复被丢弃的细节。

高分辨率层通常保留更多空间位置，深层通常整合更大范围的信息。多尺度检测利用这种互补，但也增加内存和后处理候选数。

## 运行与检查

脚本记录三层输出，并用反向传播检查三层都接入计算图。不要把“梯度存在”写成“学到了有效特征”，后者必须用任务数据评价。

## 动手任务

输入改为 130×130，手算每次 padding=1、kernel=3、stride=2 的尺寸。结果按向上取整逐层变化，不一定严格等于 H/8、H/16、H/32。后续融合使用目标尺寸插值，避免默认乘二造成拼接失败。

交付一张层名、通道、步长、空间大小、元素数表；若显存不足，先找哪些特征被同时保留，而不是只看模型文件大小。

## 配套实验与运行记录

```experiment
practice
```

在本篇代码目录执行 `python3 main.py`。依赖安装、可选入口见包内 `README.md`；实际运行结果见 [`verification.md`](/posts/edge-vision-07-feature-pyramid/code/verification.md.html)。下载包包含本课使用的辅助模块与样例。

## 参考与进一步阅读

[原始论文或官方文档](https://arxiv.org/abs/1612.03144)用于核对结构、接口和适用范围。本篇代码是围绕教学目标编写的最小实验；除明确注明的完整入口外，不视为对应论文模型的完整复现。

---

[完整进阶目录](/series/edge-vision-advanced/) · [入门系列](/series/vision-learning/) · [上一篇](/posts/edge-vision-06-reparameterization.html) · [下一篇](/posts/edge-vision-08-fpn-pan.html)
