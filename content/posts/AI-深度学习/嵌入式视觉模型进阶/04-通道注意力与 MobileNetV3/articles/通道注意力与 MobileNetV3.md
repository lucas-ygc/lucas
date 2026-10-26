---
title: 嵌入式视觉模型进阶 04：通道注意力与 MobileNetV3
date: 2026-10-24 00:00:00
categories: AI-深度学习
tags:
  - 嵌入式视觉模型进阶
  - 计算机视觉
  - 嵌入式部署
description: 实现 SE 和 Hard-Swish，检查注意力广播以及激活的分段行为。
abbrlink: edge-vision-04-mobilenetv3-se
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
      title: 实验：通道注意力与 MobileNetV3
      file: main.py
      command: python3 main.py
---

> **第 4 / 30 课。** 前置：[上一课](/posts/edge-vision-03-mobilenet-blocks.html)。本篇的运行范围以实验说明和验证记录为准，构造样例不代表真实任务精度或板端性能。

## 一个通道应当占多大权重

SE 先对 H、W 做全局平均，得到 `[N,C,1,1]` 描述，再经过降维、非线性和升维产生通道权重。权重与原特征逐通道相乘，空间位置共享该通道的缩放系数。它没有为每个像素生成一份独立注意力，也没有改变通道数。

降维比例描述隐藏层宽度，不是必须严格整除的数学限制；工程实现往往还会对齐到设备友好的通道数。本课使用 `max(1,C//4)`，避免小通道时变成零。

## Hard-Swish 为什么容易拆解

`h-swish(x)=x×ReLU6(x+3)/6`。当 x≤−3 时为零；x≥3 时为 x；中间为二次段。它与 Swish 的曲线不同，不能直接用一个替换另一个而宣称等价。Hard-Sigmoid 常用于门控，本课取 `ReLU6(x+3)/6`。

MobileNetV3 组合了多种模块选择。本课实现的是其中的关键组件，不是重新宣称实现了完整搜索过程或完整 V3 网络。完整模型可用第 1 课的方法逐层审查。

## 实验与工程判断

脚本手写 Hard-Swish 并与框架函数逐值比较，再检查 SE 权重范围和输出形状。将输入设为全零，观察门控是否必定为零；答案是否定的，门控取决于学习参数与偏置。

NPU 可能把激活识别成融合算子，也可能分解为 Add、Clip、Mul 等节点。应查看转换报告与实际耗时；模块名称里带“轻量”不是兼容性保证。

## 课后交付

画出 `[N,C,H,W]→[N,C,1,1]→[N,C/r,1,1]→[N,C,1,1]`，注明最后乘法的广播方向。将平均池化误写为只沿 W 归约，比较它变成了怎样的空间依赖。

## 配套实验与运行记录

```experiment
practice
```

在本篇代码目录执行 `python3 main.py`。依赖安装、可选入口见包内 `README.md`；实际运行结果见 [`verification.md`](/posts/edge-vision-04-mobilenetv3-se/code/verification.md.html)。下载包包含本课使用的辅助模块与样例。

## 参考与进一步阅读

[原始论文或官方文档](https://arxiv.org/abs/1905.02244)用于核对结构、接口和适用范围。本篇代码是围绕教学目标编写的最小实验；除明确注明的完整入口外，不视为对应论文模型的完整复现。

---

[完整进阶目录](/series/edge-vision-advanced/) · [入门系列](/series/vision-learning/) · [上一篇](/posts/edge-vision-03-mobilenet-blocks.html) · [下一篇](/posts/edge-vision-05-channel-shuffle.html)
