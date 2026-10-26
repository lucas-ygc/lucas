---
title: 嵌入式视觉模型进阶 11：完整 YOLOv8 推理：从图片到原图目标框
date: 2026-10-24 00:00:00
categories: AI-深度学习
tags:
  - 嵌入式视觉模型进阶
  - 计算机视觉
  - 嵌入式部署
description: 固定 YOLOv8 检测导出契约，完成 letterbox、分类别 NMS 与坐标还原。
abbrlink: edge-vision-11-yolov8-inference
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
      title: 实验：完整 YOLOv8 推理：从图片到原图目标框
      file: main.py
      command: python3 main.py
---

> **第 11 / 30 课。** 前置：[上一课](/posts/edge-vision-10-detector-loss.html)。本篇的运行范围以实验说明和验证记录为准，构造样例不代表真实任务精度或板端性能。

## 先固定一个可以检查的版本契约

本课限定 Ultralytics YOLOv8 的普通检测 ONNX：batch=1、固定方形输入、FP32、`nms=False`，输出 `[1,4+C,A]`，前四行是输入像素坐标的中心宽高，后面 C 行是类别分数，不另乘 objectness。分割、姿态、带 NMS 导出、其他 YOLO 家族不能直接复用。

本课自写推理入口不导入 Ultralytics。它接收本地 ONNX、图片和类别数；启动时检查类型、布局、通道与输出数量。真实权重不随包提供。默认无参数运行使用构造输出，验证完整前后处理链。

## 预处理要留下逆变换信息

保持纵横比缩放到输入框内，剩余边缘填充 114。记录实际缩放后的宽高以及左上 padding。OpenCV 读取 BGR，模型输入转 RGB、除以 255、转 NCHW，并保持 float32。整数舍入会让两个轴的实际缩放比略有差异，代码分别记录 sx、sy。

## 输出解码与筛选

每个候选取最大类别分数，再做阈值过滤。将 cxcywh 转 xyxy；NMS 按类别执行，同位置的不同类别不会互相抑制。最后减 padding、除缩放比例并裁剪到原图范围，丢弃退化框。

本课候选按最高分截断到 3000 以限制 Python NMS 开销，这个上限可能影响拥挤场景召回，需要在验收协议中记录。

## 真实模型运行

安装包内依赖后运行 `python3 main.py --model model.onnx --image frame.jpg --classes 80`。类别数必须与你的模型一致。程序输出 JSON 框列表，不自动下载权重。

用包含边缘目标和非方形尺寸的图片，与原训练框架比较结果；比较同一输入上的原始 logits，再比较后处理。只看画出的框“差不多”不足以确认精度。

## 练习

把构造图片改成竖图，核对横向 padding；把两个高重叠框类别设为不同，确认它们都保留。若模型输出已经是 xyxy 或已带 NMS，应写新的契约适配器，不能只修改一个 transpose 蒙混通过。

## 配套实验与运行记录

```experiment
practice
```

在本篇代码目录执行 `python3 main.py`。依赖安装、可选入口见包内 `README.md`；实际运行结果见 [`verification.md`](/posts/edge-vision-11-yolov8-inference/code/verification.md.html)。下载包包含本课使用的辅助模块与样例。

## 参考与进一步阅读

[原始论文或官方文档](https://docs.ultralytics.com/models/yolov8/)用于核对结构、接口和适用范围。本篇代码是围绕教学目标编写的最小实验；除明确注明的完整入口外，不视为对应论文模型的完整复现。

---

[完整进阶目录](/series/edge-vision-advanced/) · [入门系列](/series/vision-learning/) · [上一篇](/posts/edge-vision-10-detector-loss.html) · [下一篇](/posts/edge-vision-12-train-detector.html)
