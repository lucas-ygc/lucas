---
title: 嵌入式视觉模型进阶 22：OCR 检测：从文字区域到矫正图片
date: 2026-10-24 00:00:00
categories: AI-深度学习
tags:
  - 嵌入式视觉模型进阶
  - 计算机视觉
  - 嵌入式部署
description: 通过有序四边形和透视变换理解文字裁剪，保留阅读方向与边界信息。
abbrlink: edge-vision-22-text-rectification
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
      title: 实验：OCR 检测：从文字区域到矫正图片
      file: main.py
      command: python3 main.py
---

> **第 22 / 30 课。** 前置：[上一课](/posts/edge-vision-21-pose-decoding.html)。本篇的运行范围以实验说明和验证记录为准，构造样例不代表真实任务精度或板端性能。

## 文字框为什么不总是水平矩形

路牌、包装和倾斜文档上的文字可能旋转或透视变形。文本检测器输出可能是四边形、多边形或概率图。概率图还需要二值化、连通区域、轮廓过滤和扩张等处理，具体规则取决于模型。

本课输入已经确定的四个角点，练习检测之后的裁剪矫正，不实现 DB 检测网络。四点按左上、右上、右下、左下顺序提供；上游应同时保存阅读方向。简单按坐标排序对极端旋转或退化形状可能失效。

## 透视变换比仿射更一般

用四对对应点求 3×3 单应矩阵，把原图四边形映射到规则矩形。变换可描述平面在透视下的形变，但弯曲纸面不一定能用一个矩阵完全矫正。

输出宽度可按上下边较长者估计，高度按左右边较长者估计。最小尺寸、长宽比和退化面积需要检查，避免生成零大小图或极大缓冲。

## 几何与识别分开验证

脚本在构造图片中标出四点，检查矩阵将四点映射到目标角点，并执行实际 warpPerspective。角点误差很小不代表文字一定可读；插值、模糊和裁剪缺边仍可能使识别失败。

## 修改任务

交换右下与左下的顺序，观察四边形自交；将所有点放在同一直线，确认程序拒绝退化输入。再给裁剪边缘增加适量空白，比较字符是否完整，但不要把统一扩张比例当作所有检测器的默认值。

多文本区域的阅读排序应另行设计。单行从左到右排序适合本课示例，复杂表格、多栏页面或竖排文字需要版面分析，不能只按一个 x 坐标处理。

## 配套实验与运行记录

```experiment
practice
```

在本篇代码目录执行 `python3 main.py`。依赖安装、可选入口见包内 `README.md`；实际运行结果见 [`verification.md`](/posts/edge-vision-22-text-rectification/code/verification.md.html)。下载包包含本课使用的辅助模块与样例。

## 参考与进一步阅读

[原始论文或官方文档](https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html)用于核对结构、接口和适用范围。本篇代码是围绕教学目标编写的最小实验；除明确注明的完整入口外，不视为对应论文模型的完整复现。

---

[完整进阶目录](/series/edge-vision-advanced/) · [入门系列](/series/vision-learning/) · [上一篇](/posts/edge-vision-21-pose-decoding.html) · [下一篇](/posts/edge-vision-23-ctc-recognition.html)
