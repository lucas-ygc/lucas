---
title: 海思NPU模型转换 05 预处理与AIPP
date: 2026-08-05 00:00:00
categories: AI-深度学习
tags:
  - Hi3516CV610
  - 模型转换
  - ONNX
  - NPU
description: 推导颜色、planar 布局、均值缩放、ROI 和 AIPP 的完整输入约定。
abbrlink: hi3516-npu-convert-05
cover: ../images/封面.png
draft: false
---

> 系列编排日期为 2026 年 8 月；技术基线核对与教学代码 CPU 验证日期为 2026-10-12。适用 Hi3516CV610 与本系列注明的 SDK/工具版本，实测范围见第 12 章。

[返回系列目录](/posts/hi3516-npu-convert-01.html) · 本篇属于 12 章与 4 份附录。

大量“转换后精度下降”实际来自输入不一致。排查时应把一张图拆成几何变换、存储布局和数值变换三部分，分别固定和验证。

## 文档入口与处理顺序

查《ATC工具使用指南》3.2.4，重点是 3.2.4.1.1 AIPP 规格、3.2.4.1.2.4 `model_format`、3.2.4.1.2.6 均值与缩放，以及 crop、resize、padding 子节。静态与动态 AIPP 分别查 3.2.4.1.3、3.2.4.1.4。

Hi3516CV610 的 AIPP 处理顺序按本版文档为 Crop → Pad → 色彩转换 → 通道转换 → 减均值与缩放 → Resize。不能假设它与自己组合的 OpenCV 调用天然相同。本项目常把 ROI、resize 和 letterbox 放在 CPU，只让 AIPP 负责通道和数值变换，从而更容易保存完全一致的输入字节。

## 明确 RGB BGR 和 planar

OpenCV 常用图像是 HWC 的 BGR 交错排列：`B0 G0 R0 B1 G1 R1 ...`。`BGR_PLANAR` 则连续保存整张 B 平面、G 平面、R 平面。它们总字节数相同，排列完全不同。

```python
# image 必须是 uint8、HWC、BGR
planar = np.ascontiguousarray(image.transpose(2, 0, 1))
planar.tofile("input.bgr")
```

320×320 三通道 UINT8 的逻辑输入为 307200 字节。这个数字用于校验教学文件；ACL 设备 buffer 可能因 stride 对齐而更大，写设备内存时仍要逐行处理。

`input_format=BGR_PLANAR` 描述传入 AIPP 的存储，`model_format=RGB` 描述模型所需通道语义。PIPNet 使用 BGR 输入转 RGB，再按 ImageNet 方式归一化；YuNet 这条路径保持 BGR。不能把某份 aipp.cfg 改个分辨率就用于另一个网络。

## 均值与缩放推导

常见训练输入是：

```text
x_float = (x_uint8 / 255 - mean) / std
        = (x_uint8 - 255 * mean) * (1 / (255 * std))
```

因此 AIPP 的 `mean_chn` 使用像素尺度均值，`var_reci_chn` 使用 `1/(255*std)`。PIPNet RGB 均值为 123.675、116.28、103.53，对应标准差 0.229、0.224、0.225 时，缩放系数分别按上述公式计算。应按转换后的模型通道顺序填写，并对照本版 AIPP 文档确认通道转换位置。

YuNet 教学路径的首层权重已乘以 255，AIPP 再除以 255：

```text
aipp_op {
  aipp_mode: static
  related_input_rank: 0
  input_format: BGR_PLANAR
  model_format: BGR
  src_image_size_w: 320
  src_image_size_h: 320
  mean_chn_0: 0
  mean_chn_1: 0
  mean_chn_2: 0
  var_reci_chn_0: 0.00392156862
  var_reci_chn_1: 0.00392156862
  var_reci_chn_2: 0.00392156862
}
```

原始模型与变换后模型不能共用这份配置而不做判断。对原始模型直接增加 `/255`，或者 CPU 和 AIPP 都归一化，会改变结果。

## 几何变换必须记录细节

letterbox 至少有目标大小、缩放比例、取整方式、插值、填充值和填边位置六项。居中填 114 与左上对齐填黑，即使同为 320 输入，也不是同一输入。

教学 YuNet 对预先选好的头部 ROI 使用 `scale=320/max(width,height)`，尺寸四舍五入，双线性缩放，左上放置，右侧和底部填 0。对于原图坐标，先减 padding，再除以记录的缩放比例，再加 ROI 左上角；若实际宽高取整造成比例略异，应与业务使用的逆变换保持一致。

项目的 `PrepareOcclusionCalibration.py` 中 YuNet 默认 1280、居中填 114、最近邻插值，与当前级联中的头 ROI、320、左上黑边路径不同。它可以作为数据准备代码参考，但必须调整几何策略后才能服务当前实验。

## 静态与动态 AIPP 的选择

静态 AIPP 把配置固化到模型，适合固定输入。动态 AIPP 需要运行时按接口设置参数，并遵守该芯片的格式和尺寸限制；它不是任意 OpenCV 操作的通用替代，也不能自动解决模型本身不支持动态 shape 的问题。

多输入模型要核对 `related_input_rank` 指向哪一个输入。图像分支和特征分支可能使用不同 dtype，不应把同一 AIPP 套到所有输入。选择动态路线前先跑通静态基准，可以减少同时变化的因素。

## 如何验证输入一致

用红绿蓝色块验证通道，用带坐标网格的图验证几何，用常量 0、128、255 验证数值范围。保存原图、处理后的 PNG、连续 BGR planar 字节和其 SHA-256。CPU 基准直接从同一份字节恢复输入，再执行 AIPP 对应的数学变换。

若同一输入文件在 PC 和板端输出不同，才继续查运行时；若两端的输入哈希都不同，应先修数据入口。编码为 JPEG 会增加解码和压缩差异，用无损 PNG 或原始字节保存对齐样本更合适。

[上一篇 导出和整理ONNX](/posts/hi3516-npu-convert-04.html) · [系列目录](/posts/hi3516-npu-convert-01.html) · [下一篇 校准数据与量化](/posts/hi3516-npu-convert-06.html)
