---
title: 海思NPU模型转换 07 执行ATC转换
date: 2026-08-07 00:00:00
categories: AI-深度学习
tags:
  - Hi3516CV610
  - 模型转换
  - ONNX
  - NPU
description: 逐项解释可复核的 ATC 命令、输出产物、日志与 original OM 的含义。
abbrlink: hi3516-npu-convert-07
cover: ../images/封面.png
draft: false
---

> 系列编排日期为 2026 年 8 月；技术基线核对与教学代码 CPU 验证日期为 2026-10-12。适用 Hi3516CV610 与本系列注明的 SDK/工具版本，实测范围见第 12 章。

[返回系列目录](/posts/hi3516-npu-convert-01.html) · 本篇属于 12 章与 4 份附录。

执行 ATC 前，模型、AIPP、校准清单和输出目录应当已经确定。命令应完整保存，而不是仅在 shell 历史中留下一次临时执行。

## 文档入口与最小准备

查《ATC工具使用指南》2.1～2.3、3.2.2 模型参数、3.2.3 输出参数、3.2.4 输入、3.2.5 输出约定、3.2.6 量化及 3.2.9.1 目标芯片。`save_original_model` 见 3.3.3.1。

以下命令在本项目 SVP 容器中执行，使用第 12 章已经生成的实验目录。示例为固定 320 的 YuNet，不可仅改模型文件名就用于其他网络。

## 一份可复核的 ATC 命令

```bash
source /usr/local/Ascend/ascend-toolkit/svp_latest/x86_64-linux/script/setenv.sh
case_dir=/workspace/application/.temp/yunet320-run
mkdir "$case_dir/om"
atc --version > "$case_dir/om/atc-version.txt" 2>&1
atc --model="$case_dir/yunet320_input255.onnx" \
  --framework=5 \
  --soc_version=Hi3516CV610 \
  --input_shape='input:1,3,320,320' \
  --input_type='input:UINT8' \
  --input_format=NCHW \
  --batch_num=1 \
  --online_model_type=0 \
  --insert_op_conf="$case_dir/aipp.cfg" \
  --compile_mode=1 \
  --quant_mode=0 \
  --weight_quant_per_channel=1 \
  --image_list="input:$case_dir/calibration.txt" \
  --output="$case_dir/om/yunet320" \
  --output_reorder=0 \
  --output_type=FP32 \
  --save_original_model=true \
  --dump_data=0 \
  --log_level=0 \
  > "$case_dir/om/convert.log" 2>&1
```

执行前需要把配套 `aipp_yunet.cfg` 复制为实验目录中的 `aipp.cfg`。第 12 章的 `convert_yunet.sh` 自动复制配置、拒绝已有 `om` 目录，并检查生成文件；实际复现优先使用脚本，避免漏掉准备动作。此处把完整参数展开便于阅读。

反斜杠必须是该行最后一个字符。不要在 `\` 后增加空格或行内注释。多输入参数带分号时保留引号；路径中有空格时也要正确引用。

## 这些参数为什么成组出现

`framework=5` 指定 ONNX；`soc_version` 固定目标；`input_shape` 使用实际输入名；`input_type=UINT8` 描述外部图像输入；AIPP 负责转成模型需要的数值。原始 ONNX 中 FLOAT 与外部 UINT8 并非矛盾，前提是预处理配置与工具支持相匹配。

`compile_mode=1`、`quant_mode=0` 和按通道权重量化共同定义本次基线，不能省略后再依赖印象补写。`output_reorder=0` 保持原图输出顺序；`output_type=FP32` 方便统一解析，但内部仍有量化。

`output` 是输出前缀，不应先随意加 `.om` 再猜最终文件名。一个实验的所有生成物放到同一目录，转换前保证目录是新建的，防止失败后误用旧模型。

## 转换完成后检查什么

首先检查进程退出码和日志，再检查产物是否非空、时间戳是否属于本次实验、目标配置是否正确。保存 `atc --version`、完整命令、AIPP 副本、清单副本及所有模型哈希。

`save_original_model=true` 产生 `*_original.om`，按手册用于功能仿真，也包含可上板的离线模型。名字里的 original 不是“未量化原始浮点网络”，也不能据此推断输出一定未经过后处理。它与普通 OM 的关系应通过本次生成物和工具说明判断。

项目 YuNet 的 `BuildOm.sh` 在存在 original 文件时会把它复制成常规 `.om` 名称，因此只看部署文件名也无法确定内部差异。比对 SHA-256 和加载后的描述信息更可靠。

## 失败时保留完整现场

日志的最后一行往往只是失败汇总。定位第一个实质错误，记录输入节点、算子、shape、属性、错误码以及工具版本。环境错误、校准读取错误、图解析错误和引擎编译错误应分别处理。

`check_report`、shape dump 和数据 dump 的配置见对应参数节；使用 dump 前确认额外输入与存储要求。数据 dump 常依赖校准输入，不是无条件输出每层结果的开关。诊断实验单独建目录，避免大体积 dump 混进发布包。

## 本阶段的验收边界

本阶段的成功条件是指定版本工具生成了可追溯产物，后续仍必须验证仿真、板端执行和业务指标。教程提供的命令按本地工具文档与项目脚本整理；本次编写没有重新执行 ATC，不能把命令展示当作本次芯片精度或性能实测。

[上一篇 校准数据与量化](/posts/hi3516-npu-convert-06.html) · [系列目录](/posts/hi3516-npu-convert-01.html) · [下一篇 输出与后处理约定](/posts/hi3516-npu-convert-08.html)
