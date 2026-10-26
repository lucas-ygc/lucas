---
title: 嵌入式视觉模型进阶 28：面向 NPU 的计算图与算子兼容
date: 2026-10-24 00:00:00
categories: AI-深度学习
tags:
  - 嵌入式视觉模型进阶
  - 计算机视觉
  - 嵌入式部署
description: 检查 ONNX 静态形状、算子和数值替换，建立真实编译报告的阅读方法。
abbrlink: edge-vision-28-npu-graph
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
      title: 实验：面向 NPU 的计算图与算子兼容
      file: main.py
      command: python3 main.py
---

> **第 28 / 30 课。** 前置：[上一课](/posts/edge-vision-27-depth-restoration.html)。本篇的运行范围以实验说明和验证记录为准，构造样例不代表真实任务精度或板端性能。

## 支持一个算子名字还不够

Conv 的支持可能受 kernel、stride、groups、通道数、布局、数据类型和张量尺寸限制。算子都在支持表中，整图仍可能因动态 shape 或编译内存约束失败。本课的白名单仅用于演示审查方法，不代表任何海思芯片支持表。

固定输入的 H、W 并不保证内部计算都变成静态；Shape、Gather、Reshape 等组合可能保留形状计算。应先做模型检查与 shape inference，再查看编译器实际处理结果。

## 替换必须证明数值与任务效果

本课把 Hard-Swish 写成 Add、Clip、Mul、Div，比较其与框架原算子的输出。代数等价不保证执行速度相同，编译器可能融合原算子，反而对拆解图执行更多节点。

不要只因为某个算子转换失败就删除它。LayerNorm、Softmax、插值模式和坐标变换都承载模型语义；近似替换需要原始数值对照和真实验证集评价。

## 分区与 CPU 回退

某些运行环境可把不支持的片段放到 CPU，这不等于全图在 NPU 运行。频繁分区可能造成设备间拷贝、同步和缓存维护开销。模型很小而整体很慢时，应检查分区边界，而不只是减少权重。

脚本导出教学网络、打印算子类型与输入 shape，并用示意白名单标出需人工复核的节点。它不调用专有编译器，也不输出虚构的板端支持结论。

## 练习与平台衔接

加入动态 batch 或不同插值，观察图变化。建立“节点—限制—处理策略—数值验证—板端耗时”表，然后进入[海思 NPU 模型转换](/series/hi3516-npu-conversion/)按实际 SDK 文档验证。

交付转换日志、工具版本、输入契约和失败最小模型。不要只保留一个最终二进制，否则后续无法判断是模型变化还是编译工具变化导致结果差异。

## 配套实验与运行记录

```experiment
practice
```

在本篇代码目录执行 `python3 main.py`。依赖安装、可选入口见包内 `README.md`；实际运行结果见 [`verification.md`](/posts/edge-vision-28-npu-graph/code/verification.md.html)。下载包包含本课使用的辅助模块与样例。

## 参考与进一步阅读

[原始论文或官方文档](https://onnx.ai/onnx/repo-docs/ShapeInference.html)用于核对结构、接口和适用范围。本篇代码是围绕教学目标编写的最小实验；除明确注明的完整入口外，不视为对应论文模型的完整复现。

---

[完整进阶目录](/series/edge-vision-advanced/) · [入门系列](/series/vision-learning/) · [上一篇](/posts/edge-vision-27-depth-restoration.html) · [下一篇](/posts/edge-vision-29-quantization-distillation.html)
