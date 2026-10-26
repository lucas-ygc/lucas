---
title: 嵌入式视觉模型进阶 23：OCR 识别：序列模型与 CTC
date: 2026-10-24 00:00:00
categories: AI-深度学习
tags:
  - 嵌入式视觉模型进阶
  - 计算机视觉
  - 嵌入式部署
description: 把图像宽度变为时间轴，运行小型 CNN-GRU-CTC 训练步并验证解码顺序。
abbrlink: edge-vision-23-ctc-recognition
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
      title: 实验：OCR 识别：序列模型与 CTC
      file: main.py
      command: python3 main.py
---

> **第 23 / 30 课。** 前置：[上一课](/posts/edge-vision-22-text-rectification.html)。本篇的运行范围以实验说明和验证记录为准，构造样例不代表真实任务精度或板端性能。

## 一张长图片怎样变成序列

卷积输出 `[N,C,H,W]`，可以沿高度聚合后把宽度 W 作为时间轴，得到 `[N,T,C]`。这要求保留沿文字方向的位置关系，不能把全部空间平均成一个向量再期待识别任意长文本。

RNN 用递归状态传递历史，LSTM 使用门控与细胞状态，GRU 使用较紧凑的门控结构。双向网络同时看左右上下文，适合整行离线识别，但不能直接作为不看未来的流式模型。本课用双向 GRU 实现最小可运行结构。

## CTC 解决的是对齐未知

标注只给字符串，没有给每个时间步对应哪个字符。CTC 对合法对齐路径求和，引入 blank 并允许字符重复占据多个时间步。它不是一种循环网络，也不要求一定搭配 RNN。

贪心解码顺序是先合并连续重复，再移除 blank。例如 `A,A,blank,A,B,B` 得到 `AAB`；若先移除 blank 再合并，会错误变成 AB。字符表、blank 索引与空格是否在词表中必须与权重一致。

## 运行与长度检查

脚本使用 `[2,1,16,32]` 构造输入，CNN 将时间长度变为 16，输出 `[T,N,4]` 的 log probabilities；目标是 AB 与 AA。连续重复目标需要 blank 隔开，因此最小时间长度还与重复字符数相关。

设置 zero_infinity 并不能代替长度检查；它可能把无效样本损失置零，掩盖标签错误。本课保留默认错误暴露并检查损失、梯度有限。

## 练习

把贪心序列中的 blank 删除，解释为什么结果变化。把输入宽度缩得过小，观察 AA 的对齐是否仍可行。参考结论：时间轴必须容纳标签及必要的重复分隔，宽度缩放策略直接影响可识别长度。

本实验只执行一个训练步，随机权重没有文字识别能力；完整流程还需要词表、数据、训练与独立评估。

## 配套实验与运行记录

```experiment
practice
```

在本篇代码目录执行 `python3 main.py`。依赖安装、可选入口见包内 `README.md`；实际运行结果见 [`verification.md`](/posts/edge-vision-23-ctc-recognition/code/verification.md.html)。下载包包含本课使用的辅助模块与样例。

## 参考与进一步阅读

[原始论文或官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.CTCLoss.html)用于核对结构、接口和适用范围。本篇代码是围绕教学目标编写的最小实验；除明确注明的完整入口外，不视为对应论文模型的完整复现。

---

[完整进阶目录](/series/edge-vision-advanced/) · [入门系列](/series/vision-learning/) · [上一篇](/posts/edge-vision-22-text-rectification.html) · [下一篇](/posts/edge-vision-24-ocr-pipeline.html)
