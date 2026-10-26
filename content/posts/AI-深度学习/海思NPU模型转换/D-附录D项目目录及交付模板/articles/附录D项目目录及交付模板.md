---
title: 海思NPU模型转换 D 附录D项目目录及交付模板
date: 2026-08-16 00:00:00
categories: AI-深度学习
tags:
  - Hi3516CV610
  - 模型转换
  - ONNX
  - NPU
description: 提供转换目录、manifest、接口与验收表，以及发布回滚维护规则。
abbrlink: hi3516-npu-convert-d
cover: ../images/封面.png
draft: false
---

> 系列编排日期为 2026 年 8 月；技术基线核对与教学代码 CPU 验证日期为 2026-10-12。适用 Hi3516CV610 与本系列注明的 SDK/工具版本，实测范围见第 12 章。

[返回系列目录](/posts/hi3516-npu-convert-01.html) · 本篇属于 12 章与 4 份附录。

一份可交接的转换成果，应让另一位工程师知道文件从何而来、如何运行、如何验收，以及失败时回到哪个已验证版本。以下目录和模板可直接用于项目整理。

## 建议目录

```text
model-release/
  README.md
  manifest.json
  source/
    model.onnx
    external-data-if-any
    source.sha256
  scripts/
    export.py
    prepare-input.py
    convert.sh
    compare.py
  config/
    aipp.cfg
    model-interface.json
    labels-or-landmark-metadata.json
  calibration/
    list.txt
    samples-index.json
  artifacts/
    model.om
    model_original.om
    artifacts.sha256
  evidence/
    tool-version.txt
    environment.txt
    convert.log
    cpu-report.json
    simulation-report.json
    board-report.json
    task-metrics.json
  rollback/
    previous-release.json
```

目录表示信息类别，不要求每个模型都同时有所有文件。没有使用的外置权重和元数据明确标为不适用。受限样本保留内部索引，不在公开博客或公共发布包内分发。

## manifest 模板

下面是需填写的模板，`null` 表示尚未记录，不等于验收通过。正式发布时应补齐必要字段。

```json
{
  "target_soc": "Hi3516CV610",
  "sdk": "Hi3516C V610R001C01SPC020",
  "tool_bundle": "SVP_NNN_PC_V5.0.2.3",
  "atc_version": null,
  "source_sha256": null,
  "compiled_sha256": null,
  "input": {
    "name": "input",
    "shape": [1, 3, 320, 320],
    "external_type": "UINT8",
    "external_layout": "BGR_PLANAR",
    "geometry": "head ROI, bilinear, top-left black padding"
  },
  "conversion": {
    "compile_mode": 1,
    "quant_mode": 0,
    "output_reorder": 0,
    "output_type": "FP32",
    "aipp_sha256": null,
    "calibration_manifest_sha256": null
  },
  "postprocess_version": null,
  "validation": {
    "cpu_equivalence": null,
    "simulation": null,
    "board_parity": null,
    "task_accuracy": null,
    "latency_memory": null
  },
  "previous_release": null
}
```

这份模板以 YuNet 为例；换模型后要重新填写输入、量化、输出和几何。字段名字一致便于管理，字段值不能机械复制。

## 模型接口模板

输入记录名称、shape、dtype、layout、颜色、归一化、ROI 来源、插值、取整和填边。输出逐个记录名称、索引、shape、dtype、语义、是否激活、是否解码和是否 NMS。运行时 buffer 大小和 stride 记录在设备描述证据中，不把某次设备返回值误写成所有版本恒定值。

后处理还需要阈值、标签或点位顺序、坐标逆变换及最大候选数。World 词表与 OM 必须绑定；PIPNet 的点位和邻居定义应随程序版本追溯；分类标签顺序改变同样属于接口变更。

## 验收表模板

| 项目 | 输入与环境 | 判定标准 | 实测值 | 结果 |
| --- | --- | --- | --- | --- |
| 导出等价性 | 固定真实图与原框架 | 预先设定逐输出误差 | 待填写 | 待执行 |
| 改图等价性 | 原 ONNX 与变体 | 逐输出数值和解码一致 | 待填写 | 待执行 |
| 量化精度 | CPU 与功能仿真 | 张量指标及任务要求 | 待填写 | 待执行 |
| 设备一致性 | 同哈希模型与输入 | 仿真与板端输出对照 | 待填写 | 待执行 |
| 任务准确率 | 独立标注集 | 召回或任务专用指标 | 待填写 | 待执行 |
| 性能 | 实板、负载、重复次数 | execute 与端到端时延 | 待填写 | 待执行 |
| 内存与稳定性 | 多模型和长时间循环 | 峰值、剩余量、无持续泄漏 | 待填写 | 待执行 |

阈值在看最终测试结果前制定，性能与准确率分别判定。测试日期、设备、软件版本和样本集合必须与实测值在一起，不能只保留一个孤立数字。

## 发布和回滚顺序

先在独立目录加载新模型，完成同图检查，再生成包含新模型和配套配置的发布包。确认实际运行路径与打包脚本读取路径一致，通过设备日志核对加载文件。需要修改后处理的变更，应与程序一起发布。

保留上一版模型、配置、程序和元数据的配套关系；回滚时恢复整套约定。仅把旧 OM 复制回来，却继续使用新解码或词表，不能视为可靠回滚。发布过程是否重启、如何切换文件和如何恢复业务，按项目实际部署机制执行。

## 文档升级维护

工具、模型、校准数据、AIPP、后处理任何一项改变，都应记录变更原因并重新执行相关验证。模型重导出后，即使文件名没有变化，也应生成新的哈希和报告。

本系列的文档、项目脚本和教学源模型哈希保存在博客 `docs/海思NPU转换系列-基线.json`；文章日期采用 2026 年 8 月编排，技术核对与本次 CPU 验证日期为 2026-10-12。两类日期分别保留，避免把文章日期误当作实测时间。

[上一篇 附录C错误现象与排查表](/posts/hi3516-npu-convert-c.html) · [系列目录](/posts/hi3516-npu-convert-01.html)
