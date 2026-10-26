---
title: 海思NPU模型转换 B 附录BATC与AIPP参数表
date: 2026-08-14 00:00:00
categories: AI-深度学习
tags:
  - Hi3516CV610
  - 模型转换
  - ONNX
  - NPU
description: 集中核对输入、量化、输出、AIPP 配置与常见概念混淆。
abbrlink: hi3516-npu-convert-b
cover: ../images/封面.png
draft: false
---

> 系列编排日期为 2026 年 8 月；技术基线核对与教学代码 CPU 验证日期为 2026-10-12。适用 Hi3516CV610 与本系列注明的 SDK/工具版本，实测范围见第 12 章。

[返回系列目录](/posts/hi3516-npu-convert-01.html) · 本篇属于 12 章与 4 份附录。

参数表用于检查配置是否完整，不能替代模型自身的输入输出定义。表中的 YuNet 数值仅适用于第 12 章的固定 320、首层乘 255 路线。

## ATC 基本参数

| 参数 | 教学示例 | 含义与检查点 |
| --- | --- | --- |
| `--model` | `yunet320_input255.onnx` | 必须是实际验证过的变换后模型 |
| `--framework` | `5` | 本工具 ONNX 输入框架 |
| `--soc_version` | `Hi3516CV610` | 不与板型目录后缀混用 |
| `--input_shape` | `input:1,3,320,320` | 输入名和顺序必须来自模型 |
| `--input_format` | `NCHW` | 图输入维度约定，区别于 AIPP 像素格式 |
| `--input_type` | `input:UINT8` | 外部字节类型，配合 AIPP |
| `--batch_num` | `1` | 本样例固定 batch |
| `--online_model_type` | `0` | 沿用项目离线转换路线 |
| `--insert_op_conf` | AIPP 文件路径 | 文件内容与模型变换一起版本化 |
| `--output` | `om/yunet320` | 输出前缀与实验目录 |

输入名称中的大小写、冒号和多输入分号都有语法意义。多输入配置不要按屏幕显示顺序猜测，要对照 ONNX 和转换器实际接收的输入集合。

## 量化与输出参数

| 参数 | 本样例配置 | 不能误解为 |
| --- | --- | --- |
| `--compile_mode` | `1` | 整网 FP16 |
| `--quant_mode` | `0` | 激活位宽配置 |
| `--weight_quant_per_channel` | `1` | 所有算子都采用通道量化 |
| `--image_list` | `input:清单路径` | 自动复现业务 ROI 与 letterbox |
| `--output_reorder` | `0` | 可以不检查实际输出描述 |
| `--output_type` | `FP32` | 内部无量化损失 |
| `--save_original_model` | `true` | 导出未量化原始框架模型 |
| `--dump_data` | `0` | 开启所有中间层数据导出 |
| `--log_level` | `0` | 足以替代保存完整命令与版本 |

`gfpq_param_file`、`high_precision_layer`、`concat_auto_fallback_to_fp16` 和 `output_quantized` 没有在主样例中启用。需要使用时查对应小节、目标芯片限制和依赖关系，单独建立对照实验。不要把多个“可能提升精度”的开关一次全部打开。

## 静态 AIPP 字段

| 字段 | YuNet 示例 | 检查方式 |
| --- | --- | --- |
| `aipp_mode` | `static` | 配置固化到模型 |
| `related_input_rank` | `0` | 指向正确图像输入 |
| `input_format` | `BGR_PLANAR` | 字节是三平面，不是交错 HWC |
| `model_format` | `BGR` | 与源模型的通道语义一致 |
| `src_image_size_w/h` | `320/320` | 对应 CPU 已处理的图像大小 |
| `mean_chn_0/1/2` | `0/0/0` | 本路线不减额外均值 |
| `var_reci_chn_0/1/2` | `0.00392156862` | 对应首层已乘 255 的图 |

本配置没有启用 AIPP 几何变换，ROI、缩放和填边由 CPU 完成。若加入 crop、padding 或 resize，需要按本芯片的顺序重新推导输入，不能继续沿用 CPU 旧基准。

## 输入计算检查表

| 训练或原模型语义 | 等价像素尺度表达 | 容易出现的错误 |
| --- | --- | --- |
| FLOAT 0～255 | `x_uint8` 转 FLOAT | 无依据增加除 255 |
| FLOAT 0～1 | `x_uint8 / 255` | CPU 和 AIPP 重复缩放 |
| ImageNet 标准化 | `(x-255*mean)/(255*std)` | 均值仍写 0.x，或通道错位 |
| 本教程 YuNet 变体 | 输入除 255，首层权重乘 255 | 使用原始模型却套变体 AIPP |

公式中的 `x` 是完成正确通道转换后的像素值。归一化表达式相同但颜色顺序不同，依然是不同输入。

## 输出读取参数

读取时记录 index、name、dtype、dims、stride 和 buffer bytes。类型大小接口返回 bit 数，应除以 8；逻辑行宽不能超过 stride，所有行不能超过实际 buffer 大小。先验证边界再复制，避免错误配置转化为越界读写。

教学比较器只接受 FP32、固定正整数 shape 和完整输出集合。更换 FP16、INT8、动态形状或硬化后输出时，应明确扩展解析逻辑与量化参数，不能只改 NumPy dtype。

[上一篇 附录A文档检索表](/posts/hi3516-npu-convert-a.html) · [系列目录](/posts/hi3516-npu-convert-01.html) · [下一篇 附录C错误现象与排查表](/posts/hi3516-npu-convert-c.html)
