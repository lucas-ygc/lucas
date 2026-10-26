---
title: 海思NPU模型转换 09 PC仿真与精度比对
date: 2026-08-09 00:00:00
categories: AI-深度学习
tags:
  - Hi3516CV610
  - 模型转换
  - ONNX
  - NPU
description: 用项目功能仿真库重放输入，按输出名称剥离 padding 并比较 CPU 基准。
abbrlink: hi3516-npu-convert-09
cover: ../images/封面.png
draft: false
---

> 系列编排日期为 2026 年 8 月；技术基线核对与教学代码 CPU 验证日期为 2026-10-12。适用 Hi3516CV610 与本系列注明的 SDK/工具版本，实测范围见第 12 章。

[返回系列目录](/posts/hi3516-npu-convert-01.html) · 本篇属于 12 章与 4 份附录。

PC 仿真用于验证编译产物的功能和数值行为。它不提供真实板端的 NPU 时延、MMZ 峰值或多模型并发能力，应当与板端测试分别记录。

## 文档与工具选择

《快速上手指南》第 5 章介绍仿真与精度调试，5.1.1～5.1.4 依次帮助理解误差来源、隔离阶段、使用 MindCmd 比对和调整精度。《MindCmd 使用指南》第 2 章的安装及全局配置、第 3 章 Samples、第 4 章一键推理和第 6 章原框架推理可作为自动化入口，其中 6.3 对应 ONNX。

MindCmd 的命令行和样例配置应使用同包版本。先运行该版本帮助并复制对应 Samples 到实验目录，再填写模型、输入及工具路径；不能将网上另一版命令照搬进来。本项目另有直接链接功能仿真库的可追踪路线，下面采用这条路线展示输入和输出文件。

## 分成三组数值比较

第一组比较原框架与导出的 ONNX，验证导出。第二组比较原始 ONNX 与等价改写 ONNX，验证图变换。第三组比较改写 ONNX 的 CPU 输出与 OM 功能仿真，评估编译和量化。

如果第二组已经失败，第三组的误差不能全部归因于量化。若只比较最终框，则 Sigmoid、阈值、NMS 和坐标变化可能把真正的数值问题遮住。先比较原始张量，再比较任务结果。

## 使用项目 benchmark 进行功能仿真

准备：第 12 章生成的 `yunet320_original.om`、`input_0.bgr`，以及同版本工具包。以下命令在转换容器内执行：

```bash
source /usr/local/Ascend/ascend-toolkit/svp_latest/x86_64-linux/script/setenv.sh
svp=/usr/local/Ascend/ascend-toolkit/svp_latest
case_dir=/workspace/application/.temp/yunet320-run
mkdir "$case_dir/sim"
export LD_LIBRARY_PATH="$svp/toolkit/tools/sim/lib:$svp/atc/lib64:$svp/atc/third_party_lib:${LD_LIBRARY_PATH:-}"
g++ -std=c++17 -O2 \
  -I"$svp/acllib/include" -I"$svp/acllib/include/acl" \
  /workspace/application/Dependent/shared/head_yunet_luvli/hi3516/benchmark.cpp \
  -L"$svp/toolkit/tools/sim/lib" -lfuncsim \
  -o "$case_dir/sim/yunet-sim" \
  > "$case_dir/sim/build.log" 2>&1
SVP_BENCHMARK_WARMUPS=0 "$case_dir/sim/yunet-sim" \
  "$case_dir/om/yunet320_original.om" "$case_dir/input_0.bgr" \
  320 320 1 "$case_dir/sim/output" \
  > "$case_dir/sim/run.log" 2>&1
```

这个 benchmark 是项目专用辅助程序，假设模型有图像、task、work 共三个输入 buffer，默认图像为三通道 UINT8；不满足这些条件时应使用适配过的程序或厂商样例。它不是任意多输入模型执行器。

成功后应有模型描述日志、每个输出的 `output_索引.bin`，且运行返回成功。若加载阶段失败，先查 OM 类型、仿真库路径和版本；不要为了“跑通”把板端库与 PC 仿真库混合链接。

## 读取带 stride 的结果

回到具备 NumPy 的宿主机 Python 环境，执行：

```bash
python3 application/.temp/npu-handbook-tools/compare_outputs.py \
  --reference application/.temp/yunet320-run/input255_0.npz \
  --log application/.temp/yunet320-run/sim/run.log \
  --prefix application/.temp/yunet320-run/sim/output \
  --output application/.temp/yunet320-run/sim/compare.json \
  > application/.temp/yunet320-run/sim/compare.log 2>&1
```

`--prefix` 不包含 `_0.bin`。比较器按日志中的输出名称匹配 NPZ，并去除 padding。输出名不匹配时应检查图输出与硬化配置，不要把脚本改成“只比较第一个同尺寸 tensor”。

## 如何解读数值指标

MAE 表示平均绝对差；RMSE 更强调大误差；max_abs 能发现局部异常；余弦相似度反映整体方向，但对幅值缩放不敏感，零范数也没有正常定义。不能仅凭余弦接近 1 判断所有数值正确。

概率输出、回归输出和热图的数值尺度不同，需要分别设门槛。教学脚本的 `--atol` 仅作为自定最大绝对误差检查，不提供量化模型通用阈值。不传时只报告差异，不会把“成功生成 JSON”标为模型精度通过。

之后在独立真实验收集上比较检测召回、框偏差、关键点误差或分割指标。对阈值附近发生变化的样本，保存原始分数和候选集合，判断是否影响任务。

## 进一步定位与完成条件

若整体输出差异明显，先检查 AIPP 和输入字节，再按厂商数据 dump 流程比较中间层，找到第一个明显偏离的位置。shape 正确却整体倍数变化常提示归一化；局部层开始恶化可能与量化范围、算子实现或改图有关，仍需相邻节点证据支持。

本阶段完成时应有原始输入哈希、CPU 基准、仿真原始文件、描述日志、逐输出指标以及任务级对照。模拟器耗时只能记为本机诊断信息，不填写到板端性能验收表。

[上一篇 输出与后处理约定](/posts/hi3516-npu-convert-08.html) · [系列目录](/posts/hi3516-npu-convert-01.html) · [下一篇 板端最小推理闭环](/posts/hi3516-npu-convert-10.html)
