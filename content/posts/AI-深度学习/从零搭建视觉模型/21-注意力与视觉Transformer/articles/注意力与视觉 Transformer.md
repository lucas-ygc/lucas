---
title: 从零搭建视觉模型 21：注意力与视觉 Transformer
date: 2026-10-18 00:00:00
categories: AI-深度学习
tags:
  - 从零搭建视觉模型
  - 学习草稿
description: 把图片划成 patch，手算小型注意力并跟踪 token 形状，搭建教学 ViT 前向实验，区分结构验证与训练效果。
abbrlink: vision-attention-vit
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
      title: 实验：Patch、token 与 ViT 前向计算
      file: main.py
      command: python3 main.py
---

> **学习初稿 · 第 21 课。** 本篇已开放网页阅读，用于先建立完整认识。文中手算值和示意记录不代表真实训练成绩；真实数据训练、预训练权重和板端测试以本篇具体说明为准，本篇已附代码练习，实际验证范围见文末与包内记录。

## 不同图像区域怎样交流信息

卷积在局部窗口中计算，多层堆叠扩大信息范围。视觉 Transformer 的一条代表路线是把图片切成块，把每块表示成向量，再让块之间通过自注意力交换信息。它不是把图片变成中文句子，只是用一组向量作为处理单位。[ViT 原论文](https://arxiv.org/abs/2010.11929)

本课以 32×32 RGB 图片、8×8 patch 为例，共有 4×4=16 个块。每个块原始包含 8×8×3=192 个数，经过可学习映射得到长度 D 的向量。于是图片变成 `[N,16,D]`。

## Q、K、V 是三个计算角色

可以先将 Q 理解为当前位置用于查询的表示，K 用于比较相关性，V 是待汇总的信息。它们通常来自输入的不同线性变换，不是人为编写的关键词。

点积注意力先计算 `QKᵀ / sqrt(d)`，沿候选位置做 Softmax，再与 V 相乘。Softmax 应对每个查询的候选位置归一化，而不是把整个批次揉在一起。

用 d=1 的两位置例子：Q 为 `[[1],[0]]`，K 为 `[[1],[0]]`，V 为 `[[10],[20]]`。第一个查询分数 `[1,0]`，权重约 `[0.7311,0.2689]`，输出约 12.689；第二个查询的两个分数相同，均匀权重得到 15。这个例子说明输出是内容相关的加权汇总，不是简单选中一个位置。

## 为什么还要位置信息

只有 token 内容的交互不足以自动表达它来自图像左上角还是右下角，通常需要位置编码或相关结构设计。不同模型的处理方式可以不同，不能把一种位置表当成所有视觉 Transformer 的固定要求。

多头注意力将表示分成多个子空间进行交互，再组合结果。头数不是“同时处理几张图片”，也不是越多越好；实现中隐藏维度通常需要能被头数整除。

## 一个完整的形状实验

下面脚本只依赖 PyTorch，不下载权重。用步长等于 patch 大小的卷积实现 patch 映射，再加入位置参数，通过一个编码层并做平均池化分类。它省略了原始 ViT 的一些设计，属于教学网络。

```python
import torch
from torch import nn

torch.manual_seed(7)
torch.set_num_threads(2)

class TinyViT(nn.Module):
    def __init__(self):
        super().__init__()
        self.patch = nn.Conv2d(3, 32, kernel_size=8, stride=8)
        self.position = nn.Parameter(torch.zeros(1, 16, 32))
        self.encoder = nn.TransformerEncoderLayer(
            d_model=32, nhead=4, dim_feedforward=64,
            dropout=0.0, batch_first=True,
        )
        self.head = nn.Linear(32, 2)

    def forward(self, x):
        if x.shape[-2:] != (32, 32):
            raise ValueError('This teaching model requires 32x32 input')
        tokens = self.patch(x).flatten(2).transpose(1, 2)
        tokens = self.encoder(tokens + self.position)
        return self.head(tokens.mean(dim=1))

model = TinyViT().eval()
with torch.no_grad():
    output = model(torch.rand(2, 3, 32, 32))
assert output.shape == (2, 2)
print(tuple(output.shape))
```

中间依次是 `[2,32,4,4]`、`[2,32,16]`、`[2,16,32]`，最后得到 `[2,2]`。位置参数长度与 token 数匹配，因此不能任意更换输入尺寸而不处理位置和 patch 约定。

## 理论上能连接，不代表已经理解语义

随机权重的网络能运行注意力，也能输出类别分数，但不代表它认识图片。注意力图本身也不是完整的因果解释，不应只看一张漂亮热力图就断言模型为何判断。

全注意力的 token 对关系数量随 token 数平方增长。32×32 图片、8×8 patch 时是 16 个 token；若宽高翻倍且 patch 不变，就变为 64 个 token，关系矩阵元素数量从 256 增加到 4096。实际计算还包括投影与前馈等部分，内存优化实现也会改变存储方式，但 token 增长的成本仍值得关注。

CNN 与 ViT 谁更适合，取决于数据、预训练、规模和设备支持。本课不使用小样本随机训练结果给整个结构家族排名。后续可以在相同划分上比较教学 CNN 与教学 ViT，并清楚限定结论范围。

## 练习

1. 64×64 图片使用 8×8 patch，有几个 token？
2. 隐藏维度 30、头数 4，是否适合上面标准等分实现？
3. 为什么改变图片尺寸后，位置参数也需要考虑？

<details class="exercise-answer">
<summary>参考答案</summary>

有 64 个 token。30 不能被 4 整除，不符合该实现的分头约定。尺寸变化会改变 patch 网格与 token 数，固定位置表需要匹配或使用明确的插值、重建等方案，不能依赖隐式广播猜测。

</details>

接下来回到共同的工程出口：不管主干是 CNN 还是 Transformer，都要明确输入输出并验证模型导出。

## 配套代码练习

```experiment
practice
```

本篇已附独立实验包，在代码卡片中查看源码、下载或复制运行命令。解压后执行 `python3 main.py`；依赖安装见包内 `README.md`。

**观察目标：** 输入 [2,3,32,32] 被划为 16 个 patch，输出 [2,2]；随机权重只验证结构。

**动手修改：** 将输入改成 64×64，解释报错；若支持此尺寸，位置参数的 token 数需要怎样变化？

所有输入均在本篇代码中构造；运行范围和验证记录见包内 `verification.md`。

---

[完整阅读目录](/series/vision-learning/) · [上一篇](/posts/vision-segmentation-unet.html) · [下一篇](/posts/vision-onnx-export.html)
