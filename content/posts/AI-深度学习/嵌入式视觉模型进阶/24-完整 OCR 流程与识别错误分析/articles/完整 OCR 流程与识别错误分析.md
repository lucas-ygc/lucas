---
title: 嵌入式视觉模型进阶 24：完整 OCR 流程与识别错误分析
date: 2026-10-24 00:00:00
categories: AI-深度学习
tags:
  - 嵌入式视觉模型进阶
  - 计算机视觉
  - 嵌入式部署
description: 串起区域定位、排序、裁剪和识别，用数字样例定位端到端错误。
abbrlink: edge-vision-24-ocr-pipeline
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
      title: 实验：完整 OCR 流程与识别错误分析
      file: main.py
      command: python3 main.py
---

> **第 24 / 30 课。** 前置：[上一课](/posts/edge-vision-23-ctc-recognition.html)。本篇的运行范围以实验说明和验证记录为准，构造样例不代表真实任务精度或板端性能。

## 先把系统接口跑通

完整 OCR 至少包含区域定位、方向处理或矫正、识别与结果排序。第 22 课处理透视文本行，第 23 课解释 CTC。本课用更可控的清晰数字图片实现端到端流程：阈值与连通组件定位，单行排序、裁剪，再做模板匹配识别。

这是传统算法的系统基线，不是 PP-OCR 网络复现，也不支持任意字体、粘连、中文和复杂排版。选择受控样例是为了让每个中间结果都有可检查的答案。实际网络适配时保留同样的区域与文本接口，替换检测和识别模块。

## 检测结果不能丢掉位置

识别输出保存 text、box 和 score。文本排列顺序应由版面决定，不能直接使用检测器数组顺序。本课只有一行，因此按 x 排序；多行需先分行再排序，竖排与表格需要额外规则。

识别失败时保留裁剪图和位置，区分是未找到区域、裁剪缺字、方向错误、字符表错误还是模型看错。端到端文本错误可能完全来自检测，不能全部归咎于识别网络。

## 字符错误率如何计算

CER 用编辑距离除以真值字符数，包括替换、删除和插入。它与逐位置比较不同，插入一个字符不应让后面所有字符都算成替换。CER 可以超过 1；空真值单独统计插入，不直接除零。

脚本对自生成的“120”定位并识别，再对含一个插入的字符串验证编辑距离。这里只验证同字体同尺度样例，不把结果写成真实 OCR 准确率。

## 练习与真实数据衔接

改变字体尺度、加入旋转或让两个字符接触，观察首先失败的模块。记录区域级召回与裁剪后的识别 CER，再记录端到端 CER。模板失效时可以替换为经过训练的识别网络，但仍需固定词表和输入处理。

PP-OCR 等实际系统的版本可能使用不同识别骨干，不能把“所有 OCR 都是 CNN+LSTM”写成结论。部署时分别计时检测和识别，并统计一帧区域数增加后的总延迟。

## 配套实验与运行记录

```experiment
practice
```

在本篇代码目录执行 `python3 main.py`。依赖安装、可选入口见包内 `README.md`；实际运行结果见 [`verification.md`](/posts/edge-vision-24-ocr-pipeline/code/verification.md.html)。下载包包含本课使用的辅助模块与样例。

## 参考与进一步阅读

[原始论文或官方文档](https://github.com/PaddlePaddle/PaddleOCR)用于核对结构、接口和适用范围。本篇代码是围绕教学目标编写的最小实验；除明确注明的完整入口外，不视为对应论文模型的完整复现。

---

[完整进阶目录](/series/edge-vision-advanced/) · [入门系列](/series/vision-learning/) · [上一篇](/posts/edge-vision-23-ctc-recognition.html) · [下一篇](/posts/edge-vision-25-light-segmentation.html)
