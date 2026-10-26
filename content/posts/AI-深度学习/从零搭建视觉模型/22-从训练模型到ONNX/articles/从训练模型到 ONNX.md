---
title: 从零搭建视觉模型 22：从训练模型到 ONNX
date: 2026-10-18 00:00:00
categories: AI-深度学习
tags:
  - 从零搭建视觉模型
  - 学习草稿
description: 固定模型输入输出约定，导出最小 CNN 到 ONNX，在相同输入上比较 PyTorch 与 ONNX Runtime 数值，并认识导出和部署兼容的边界。
abbrlink: vision-onnx-export
draft: false
cover: ../images/封面.png
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
      title: 实验：导出 ONNX 并对照数值
      file: main.py
      command: python3 main.py
---

> **学习初稿 · 第 22 课。** 本篇已开放网页阅读，用于先建立完整认识。文中手算值和示意记录不代表真实训练成绩；真实数据训练、预训练权重和板端测试以本篇具体说明为准，本篇已附代码练习，实际验证范围见文末与包内记录。

## 为什么训练文件不能直接交给所有设备

PyTorch 参数文件需要对应结构和执行环境才能运行。ONNX 用标准化计算图与张量表示模型，方便在支持它的运行时与转换工具间交换。但“导出了 ONNX”只说明得到一种表示，不等于任意 NPU 都支持其中全部运算。

本课先验证一个小模型从 PyTorch 到 ONNX Runtime CPU 的一致性。它不依赖前文训练产物，也不需要外部数据；之后才能把相同方法应用到真实训练模型。

## 导出前写清接口

明确输入名称、形状、类型、通道顺序和数值范围，以及输出是 logits、概率还是已经后处理的结果。第一版采用固定 `[1,3,32,32]`、float32、RGB、0～1 输入，输出 `[1,2]` logits。

固定形状便于发现问题。动态 batch、动态宽高是后续需求，不应该因为工具提供选项就全部开启。支持动态导出也不代表厂商转换器和设备执行支持相同的动态范围。

模型先切换到 `eval()`，确保导出的是推理行为。预处理位于图内还是图外也要固定，避免图外除 255、图内再除一次。类别表通常作为独立元数据保存，不能期望 ONNX 输出自动携带中文类别名。

## 一个自包含的导出与对照实验

依赖 PyTorch、ONNX、ONNX Runtime、NumPy。这里显式使用传统导出路径 `dynamo=False` 与 opset 17，便于小型固定图实验；这不是宣称它永远是推荐默认路径。官方当前文档还介绍了基于 `torch.export` 的导出方式，实际项目应固定版本并核对目标工具支持的 opset。[PyTorch ONNX 导出教程](https://docs.pytorch.org/tutorials/beginner/onnx/export_simple_model_to_onnx_tutorial.html)

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import torch
from torch import nn
import onnx
import onnxruntime as ort

torch.manual_seed(7)
torch.set_num_threads(2)
model = nn.Sequential(
    nn.Conv2d(3, 4, 3, padding=1), nn.ReLU(),
    nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(4, 2),
).eval()
x = torch.rand(1, 3, 32, 32)
with torch.no_grad():
    expected = model(x).numpy()

with TemporaryDirectory() as directory:
    path = Path(directory) / 'tiny.onnx'
    torch.onnx.export(model, (x,), str(path),
                      input_names=['images'], output_names=['logits'],
                      opset_version=17, dynamo=False)
    onnx.checker.check_model(onnx.load(str(path)))
    session = ort.InferenceSession(str(path), providers=['CPUExecutionProvider'])
    actual = session.run(['logits'], {'images': x.numpy()})[0]
    np.testing.assert_allclose(actual, expected, rtol=1e-4, atol=1e-5)
    print('max_abs_error:', float(np.max(np.abs(actual - expected))))
```

脚本使用临时目录，不把导出文件混进文章发布目录。随机权重用于验证转换链路，不能把输出类别当作识别效果。正式模型需改为从可信检查点加载，并保存输入与输出参考样例。

## 为什么只看 top-1 一致不够

两个实现可能都选汽车，但 logits 已经偏差很大，边界样本会更容易翻转。应先比较输出形状，再比较最大绝对误差、适当的相对误差和任务指标。

接近零的参考值使相对误差容易变大，所以需要绝对容差。容差也不能无限放宽到“能过就行”；若误差异常，应定位最早出现偏差的层，检查布局、插值、算子语义与精度。

单个随机输入是最小冒烟检查。完整数值验收还需要全零、典型样本、不同纹理和真实验证集等输入。对于检测模型，还要区分网络输出误差与后处理差异，确保比较的对象相同。

## 导出失败与设备转换失败不是一回事

导出失败通常涉及 Python 控制流、符号形状或算子映射；ONNX 校验失败说明图可能不符合相应规范；ONNX Runtime 无法执行可能是运行时缺少实现；NPU 转换失败则还涉及厂商支持范围与参数限制。

逐段保存证据，比看到一个报错就修改模型结构更可靠。等价改写需要重新做数值对照；改变运算含义可能需要重新训练，不应为了转换成功而忽略精度。

## 练习

1. CPU 上 ONNX Runtime 能运行，能否证明 NPU 也能执行？
2. 为什么导出前需要 `eval()`？
3. 两个后端类别一致但分数差很大，是否足够验收？

<details class="exercise-answer">
<summary>参考答案</summary>

不能，两者支持范围不同。它选择 Dropout、BatchNorm 等模块的推理行为。类别一致只是一个离散结果，仍需检查数值误差及代表性数据上的任务指标，尤其关注边界样本。

</details>

下一课在浮点基线正确的前提下讨论量化；若浮点转换本来就错，不能靠量化掩盖。


## 综合实践

想把这些知识接成一套可运行的代码，可以进入[实现 MLP：从损失计算、训练到 ONNX 推理](/posts/vision-mlp-practice.html)。实践包含自生成数据、训练与验证、模型保存、独立推理、ONNX 导出和数值对照；遇到问题可按实践中的索引返回对应理论章节。

## 配套代码练习

```experiment
practice
```

本篇已附独立实验包，在代码卡片中查看源码、下载或复制运行命令。解压后执行 `python3 main.py`；依赖安装见包内 `README.md`。

**观察目标：** 通过 ONNX 检查，CPU Runtime 与 PyTorch 满足 rtol=1e-4、atol=1e-5；导出文件在临时目录。

**动手修改：** 将输入种子改为 8，重新比较完整 logits，而不只比较 argmax。

所有输入均在本篇代码中构造；运行范围和验证记录见包内 `verification.md`。

---

[完整阅读目录](/series/vision-learning/) · [上一篇](/posts/vision-attention-vit.html) · [下一篇](/posts/vision-quantization.html)
