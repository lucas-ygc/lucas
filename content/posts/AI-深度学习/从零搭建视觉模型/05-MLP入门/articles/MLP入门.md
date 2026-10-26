---
title: 从零搭建视觉模型 05：MLP 入门，从手算到图片输入
date: 2026-10-06 00:00:00
categories: AI-深度学习
tags:
  - 从零搭建视觉模型
  - PyTorch
  - MLP
description: 用可以手算的 2→3→2 小网络理解权重、偏置、全连接层和 ReLU，再把图片展平后送入 MLP，为学习 CNN 做准备。
abbrlink: vision-mlp-basics
cover: ../images/封面.png
draft: false
code:
  inline: true
  files:
    - .gitignore
    - 01_manual_mlp.py
    - 02_image_mlp.py
    - sample.ppm
    - requirements.txt
    - README.md
    - verification.md
  experiments:
    - id: manual-mlp
      title: 实验 01：手算一个 2→3→2 网络
      file: 01_manual_mlp.py
      command: python3 01_manual_mlp.py
    - id: image-mlp
      title: 实验 02：让图片经过 MLP
      file: 02_image_mlp.py
      related_files: [sample.ppm]
      command: python3 02_image_mlp.py
---

> 本篇于 2026-10-06 发布，位于图片转张量之后、CNN 之前。配套实验只在 CPU 上做前向计算。2026-10-12 已补齐四道练习的折叠参考答案。第一题保留实际练习记录，第二至四题作为复习参考；本阶段概念学习告一段落，接下来学习 CNN。

在[《图片如何变成张量》](/posts/vision-04-image-tensor.html)中，我们已经把图片变成 `float32 NCHW`。接下来先学习一个能手算的小网络，把“参数怎样参与计算”弄清楚，再进入卷积网络。

本篇不要求先学完线性代数。先用乘法、加法和数组理解计算，再把重复的运算写成矩阵形式。梯度、损失函数和反向传播放到训练章节。

## MLP 是什么

MLP 是多层感知机（Multilayer Perceptron）。本篇使用两个全连接层，中间接一个非线性激活函数：

```text
输入 → 全连接层 → ReLU → 全连接层 → 输出分数
```

“全连接”表示这一层的每个输出单元都连接到上一层的全部输入。连接有各自的权重，决定输入怎样参与计算。

先用两个数做输入，不急着接入整张图片：

| 阶段 | 形状 | 含义 |
| --- | --- | --- |
| 输入 | `(1, 2)` | 一份样本，每份有两个特征 |
| 隐藏层 | `(1, 3)` | 每份样本算出三个中间值 |
| ReLU | `(1, 3)` | 逐元素处理三个中间值 |
| 输出层 | `(1, 2)` | 每份样本得到两个分数 |

这里第二维表示特征数，不是图片宽度。`(1, 2)` 中的 1 是批次数；输入的两个特征与输出的两个分数恰好数量相同，含义不同。

隐藏层是输入和最终输出之间的中间计算层。“隐藏”不代表不能查看，实验里会把它的数值打印出来。

## 一个神经元：加权求和，再加偏置

先看一个输出单元的计算：

```text
z = w1 × x1 + w2 × x2 + b
```

- `x1`、`x2`：这一次输入的数据。
- `w1`、`w2`：权重，是模型保存的参数。
- `b`：偏置，也是参数，用来给结果增加一个可调整的偏移。
- `z`：加权求和并加上偏置后的结果；随后可以再接激活函数。

例如输入为 `[2, -1]`，权重为 `[1, 2]`，偏置为 1：

```text
z = 1×2 + 2×(-1) + 1 = 1
```

可以借用 C/C++ 来理解：输入是函数参数，权重和偏置是对象中保存的数据。前向计算读取它们来算结果；训练才会根据样本调整模型参数。

同一个网络处理不同样本时使用同一套参数。并不是每来一张新图片，就重新随机生成一套权重。

## 三个神经元怎样组成一层

现在让三个输出单元同时读取 `[2, -1]`，各用一套权重与偏置：

| 单元 | `w1` | `w2` | `b` | 计算结果 |
| --- | --- | --- | --- | --- |
| 第 0 个 | 1 | 2 | 1 | `1×2 + 2×(-1) + 1 = 1` |
| 第 1 个 | -1 | 1 | 0 | `-1×2 + 1×(-1) + 0 = -3` |
| 第 2 个 | 0.5 | -1 | -1 | `0.5×2 + (-1)×(-1) - 1 = 1` |

这一层的输出是 `[1, -3, 1]`。它有 `3×2=6` 个权重和 3 个偏置，共 9 个参数。

在 PyTorch 中用 `nn.Linear(2, 3)` 表示这层：每份输入有 2 个特征，输出 3 个特征。权重形状为 `(3, 2)`，每一行对应一个输出单元；偏置形状为 `(3,)`。[Linear 官方说明](https://docs.pytorch.org/docs/stable/generated/torch.nn.Linear.html)

注意：`nn.Linear(2, 3)` 的 2 不是批次数，3 也不是网络层数。它只定义一层的输入与输出特征数。

### 先用两层普通循环实现

先不用列表推导式和 `zip`。你可以把下面的函数看成 C/C++ 中“外层遍历输出单元，内层遍历输入数组”的两层循环。

先对照参数的含义：

```python
inputs = [2.0, -1.0]
weights = [
    [1.0, 2.0],     # 第 0 个输出单元使用的两个权重
    [-1.0, 1.0],    # 第 1 个输出单元使用的两个权重
    [0.5, -1.0],    # 第 2 个输出单元使用的两个权重
]
biases = [1.0, 0.0, -1.0]  # 三个输出单元各有一个偏置
```

`weights[输出下标][输入下标]` 表示“某个输出单元给某个输入分配的权重”。例如 `weights[1][0]` 为 -1，是第 1 个输出单元用于第 0 个输入的权重。

完整函数如下，与配套实验中的实现一致：

```python
def linear_by_hand(inputs, weights, biases):
    # 保存这一层所有输出单元的计算结果。
    outputs = []

    # 外层循环：依次计算每个输出单元。
    for output_index in range(len(weights)):
        total = 0.0

        # 内层循环：把所有输入与各自的权重相乘，再累加。
        for input_index in range(len(inputs)):
            input_value = inputs[input_index]
            weight = weights[output_index][input_index]
            total = total + input_value * weight

        # 一个输出单元的乘加完成后，加上它自己的偏置。
        total = total + biases[output_index]
        outputs.append(total)

    return outputs
```

这几个 Python 写法可以直接对应到 C/C++ 的写法：

| 写法 | 含义 |
| --- | --- |
| `len(inputs)` | 输入列表的元素个数，本例为 2 |
| `range(2)` | 依次产生下标 0、1，不包括 2 |
| `for input_index in range(len(inputs))` | 类似 `for (int i = 0; i < n; ++i)` |
| `outputs = []` | 创建一个空列表，用来逐个存放结果 |
| `outputs.append(total)` | 在列表末尾添加结果，类似 `vector.push_back(total)` |

跟着第 0 次外层循环走一遍：

| 当前步骤 | 计算 | `total` |
| --- | --- | --- |
| 开始第 0 个输出单元 | 初始化 | 0 |
| 处理第 0 个输入 | `0 + 2×1` | 2 |
| 处理第 1 个输入 | `2 + (-1)×2` | 0 |
| 加第 0 个偏置 | `0 + 1` | 1 |
| 保存结果 | `outputs.append(1)` | 列表成为 `[1]` |

随后外层循环计算第 1、2 个单元，得到最终列表 `[1, -3, 1]`。`total` 必须在每次外层循环开始时重新设为 0；`append` 放在内层循环结束之后，因为一个输出单元只产生一个结果。

本课传入的列表已经保证尺寸匹配：每行权重的数量等于输入数量，偏置数量等于输出单元数量。这个教学函数暂不实现通用的输入校验。

原来的紧凑写法把两层循环、乘加和结果收集压在一条表达式里，计算含义相同。当前先掌握上面展开后的版本，不需要同时学习列表推导式和生成器表达式。

### 再认识矩阵写法

下面是相同计算的数学简写。第一次阅读可以先跳到 ReLU，等实验 01 跑通后再回来对照。

把三个单元的权重按行摆在一起，就得到一个矩阵：

```text
W = [ 1    2 ]
    [-1    1 ]
    [ 0.5 -1 ]
```

本篇把每份输入放在一行，批量输入 `X` 的形状为 `(N, 2)`，于是可以写成：

```text
Z = X @ W.T + b
(N, 2) @ (2, 3) → (N, 3)
```

`@` 表示矩阵乘法，按对应项相乘再求和；对于这里的二维矩阵，`.T` 交换行列。`b` 的三个偏置会加到每份样本对应的三个结果上，这里用到了广播。

先掌握“每行输入依次与每行权重做乘加”即可，不用把所有矩阵运算一次学完。`nn.Linear` 已经替你完成这段重复计算。

## 为什么不能只叠加全连接层

先看两个线性加偏置的步骤：

```text
y = 2x + 1
z = 3y - 4
代入以后：z = 6x - 1
```

叠两步仍然能合并成一步；矩阵形式的线性加偏置变换也有这个性质。严格说带偏置的变换叫仿射变换，PyTorch 仍把这类层命名为 `Linear`。

如果希望网络表达更丰富的输入输出关系，需要加入非线性。这里使用 ReLU：

```text
ReLU(x) = max(0, x)
[1, -3, 1] → [1, 0, 1]
```

用普通循环表达这个规则：

```python
hidden_active = []
for value in hidden_raw:
    if value < 0.0:
        hidden_active.append(0.0)
    else:
        hidden_active.append(value)
```

这里 `hidden_raw` 是第一层的计算结果 `[1, -3, 1]`，`hidden_active` 是经过 ReLU 的结果 `[1, 0, 1]`。每次处理一个数，并向新列表添加一个数。

ReLU 逐元素保留正数，把负数变成 0，不改变形状，也没有需要训练的参数。这不是因为负数算错了，而是我们选择了这样一种非线性变换。

可以想象它在 0 处改变了变化规则：负数区间输出一直为 0，正数区间输出随输入变化。因此不能再把整套网络简单合并成一个全连接层。ReLU 也不会限制上界，大于 1 的值仍可保留。

## 第二层：从三个中间值计算两个分数

将 `[1, 0, 1]` 送进第二个全连接层 `nn.Linear(3, 2)`：

| 输出 | 三个权重 | 偏置 | 结果 |
| --- | --- | --- | --- |
| 第 0 个分数 | `[1, -1, 2]` | 0 | `1×1 + (-1)×0 + 2×1 = 3` |
| 第 1 个分数 | `[-2, 1, 1]` | 0.5 | `(-2)×1 + 1×0 + 1×1 + 0.5 = -0.5` |

完整计算链为：

```text
[2, -1] → [1, -3, 1] → [1, 0, 1] → [3, -0.5]
 输入      第一层结果     ReLU 结果      输出分数
```

第二层有 `2×3+2=8` 个参数，加上第一层的 9 个，共 17 个。输入数据本身不是模型参数，ReLU 也没有参数。

最终分数可以为负，也不必相加为 1。在分类任务中，这种未转成概率的原始分数常叫 logits。本例没有规定真实类别，也没有训练；即使第 0 个分数较大，也不能据此声称模型会识别某类东西。

### 实验 01：手算与框架逐层对照

```experiment
manual-mlp
```

完整代码先用列表和普通循环完成计算，再把完全相同的参数写进两个 `nn.Linear`，逐层比较结果。建议分两遍读：先看 `manual_scores` 的打印，确认自己能跟着算出结果；再读创建 PyTorch 层和核对结果的部分。

代码把激活层的创建与调用分开：`relu = nn.ReLU()` 创建对象，`torch_active = relu(torch_hidden)` 再让它处理数据。

`torch.tensor([inputs])` 比 `torch.tensor(inputs)` 多一层方括号，因此得到 `(1, 2)`，表示一份含两个特征的样本。这里 `Linear` 也支持一维输入，但本课统一保留批次轴。

预期输出：

```text
输入形状: (1, 2)
隐藏层加权和: [1.0, -3.0, 1.0]
ReLU 后: [1.0, 0.0, 1.0]
手算分数: [3.0, -0.5]
PyTorch 分数: [[3.0, -0.5]]
输出形状: (1, 2)
逐层对照: 全部一致
```

参数通过 `.weight.copy_()` 和 `.bias.copy_()` 写入，末尾的 `_` 表示原地操作。`with torch.no_grad():` 让这一段参数赋值与前向计算不记录梯度。本篇先用它完成数值观察，梯度机制留到训练章节。

`assert torch.allclose(...)` 检查两份浮点张量是否在容差内相等；检查失败会抛出 `AssertionError`。它没有进行训练，只是在核对计算。

## 把图片接进 MLP

手算例子只有两个输入特征，图片却有很多通道值。一张 32×32 RGB 图片包含：

```text
3 × 32 × 32 = 3072 个通道值
```

用 `nn.Flatten(start_dim=1)` 保留第 0 维 N，合并后面的 C、H、W：

```text
(N, 3, 32, 32) → (N, 3072)
```

展平没有求和，也没有压缩成较少的数，只是把每份输入的 3072 个值排列成向量。对于本篇的 CHW 数据，顺序是 R 平面、G 平面、B 平面各自按行展开。

像素数值仍然存在，已知原形状时也能重新恢复形状；但普通全连接层没有直接采用“邻近像素组成局部区域”的结构约束，也不会自动共享不同位置的权重。这一点将引出下一章的 CNN。

本篇图片网络为：

| 操作 | 输出形状 | 参数数量 |
| --- | --- | --- |
| 输入 | `(N, 3, 32, 32)` | 0 |
| `Flatten(start_dim=1)` | `(N, 3072)` | 0 |
| `Linear(3072, 16)` | `(N, 16)` | `3072×16+16=49168` |
| `ReLU()` | `(N, 16)` | 0 |
| `Linear(16, 2)` | `(N, 2)` | `16×2+2=34` |

总参数数量为 `49202`。隐藏层的 16 是我们选择的宽度，属于网络结构设置；每个权重的具体数值才是训练时更新的参数。批次数 N 不影响参数数量，同一套参数被用于每份输入。

## 用 Python 类保存网络

配套代码中的核心结构是：

```python
class ImageMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten(start_dim=1)
        self.hidden = nn.Linear(3 * 32 * 32, 16)
        self.relu = nn.ReLU()
        self.output = nn.Linear(16, 2)
```

可以借用 C++ 来理解：这个类继承 `nn.Module`，各层保存在对象成员中。`super().__init__()` 先初始化基类，PyTorch 才能正常管理子模块与参数。

`__init__` 创建并保存各层，`forward` 写输入的计算顺序。平时通过 `model(images)` 执行，而不是直接调用 `model.forward(images)`，让框架的模块调用机制正常参与。[Module 官方说明](https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html)

不要在每次 `forward` 中重新创建全连接层，否则就会不断产生新参数。`features = self.hidden(features)` 中的调用没有为你重新训练这一层，而是用对象当前保存的参数计算输出。

### 实验 02：图片前向计算

```experiment
image-mlp
```

在博客项目根目录依次运行：

```bash
python3 content/posts/AI-深度学习/从零搭建视觉模型/05-MLP入门/code/01_manual_mlp.py
python3 content/posts/AI-深度学习/从零搭建视觉模型/05-MLP入门/code/02_image_mlp.py
```

依赖与安装步骤见本篇 `code/README.md`，如果已经搭好上一章的环境，可以直接运行。代码目录自带 `sample.ppm`，不依赖其他文章的文件。

第二个实验把熟悉的六色示例统一为 32×32，转换为 RGB、浮点数和 NCHW，然后送入网络。这里只是借这张图观察计算，放大六个像素不会创造真实细节。

形状输出为：

```text
输入: (1, 3, 32, 32)
展平: (1, 3072)
隐藏层: (1, 16)
ReLU: (1, 16)
输出分数: (1, 2)
输出类型: torch.float32, 设备: cpu
```

代码还会打印分数和参数总数 `49202`。参数计数也使用普通循环：

```python
parameter_count = 0
for parameter in model.parameters():
    parameter_count = parameter_count + parameter.numel()
```

`model.parameters()` 逐个给出参数张量；`parameter.numel()` 是该张量包含的数字个数。累加的是权重和偏置的元素数量，不是层数。

与手算实验不同，这个网络的参数由框架随机初始化，没有手工写成特定数值。

`torch.manual_seed(7)` 方便同环境复现初始化，跨平台或不同版本下，不保证分数完全一致。`model.eval()` 设置评估模式，`torch.no_grad()` 关闭梯度记录；两者都不等于“训练完成”。本例没有 Dropout 或 BatchNorm，`eval()` 不改变这些层的计算规则。

第一层要求每份输入有 3072 个特征，因此读图函数统一使用 32×32。若改成 16×16，就需要相应调整第一层输入长度。改变批次数则不需要重新定义网络。

## 为什么后面还要学 CNN

MLP 可以处理图片，但直接连接所有像素会带来较多参数。图片变大，第一层输入长度也会变大；不同空间位置还使用各自的连接权重。

CNN 通过局部区域与空间上的权重共享，引入适合图像的结构。学完本篇，再看卷积时就能具体比较：什么在计算、哪些权重被重复使用、为什么通道数会变化。

这里不是说 MLP 完全不能学习像素关系，而是它没有像卷积那样直接利用这种结构。先掌握本篇的全连接层、激活与前向计算，就能更专注地学习卷积。

## 课后练习

下面四题按顺序完成。四道参考答案均放在对应题目下方，默认折叠。第二至四题于 2026-10-12 补充为复习参考，不代表逐题提交的个人作业记录。可以在 `playground/test.py` 练习，确认后再整理回文章。

### 练习 1：换一个输入，手算完整网络

保持实验 01 的两层权重与偏置不变，把输入改成 `[1, 2]`：

1. 算出隐藏层三个加权和。
2. 写出 ReLU 后的三个值。
3. 算出最后两个分数。
4. 写出每一步带批次轴的形状，再运行代码验证。

请列出乘加过程，不只写最终分数。

<details class="exercise-answer">
<summary>点击查看第一题参考答案与本次练习总结</summary>

**参考答案：每个输出单元分别计算**

输入改为 `[1, 2]`，两层的权重和偏置不变。题目中的“三个加权和”指三个隐藏单元各自的加权求和并加上偏置，分别保留三个结果：

```text
第 0 个单元：1×1 + 2×2 + 1       = 6
第 1 个单元：(-1)×1 + 1×2 + 0   = 1
第 2 个单元：0.5×1 + (-1)×2 - 1 = -2.5
```

因此 `hidden_raw` 为 `[6, 1, -2.5]`。经过 ReLU，负数变为 0，得到 `hidden_active = [6, 1, 0]`。

第二层读取这三个值，分别计算两个输出分数：

```text
第 0 个分数：1×6 + (-1)×1 + 2×0       = 5
第 1 个分数：(-2)×6 + 1×1 + 1×0 + 0.5 = -10.5
```

| 阶段 | 一份样本的数值 | 带批次轴的形状 |
| --- | --- | --- |
| 输入 | `[1, 2]` | `(1, 2)` |
| 隐藏层加权和加偏置 | `[6, 1, -2.5]` | `(1, 3)` |
| ReLU | `[6, 1, 0]` | `(1, 3)` |
| 输出分数 | `[5, -10.5]` | `(1, 2)` |

手写计算使用的是一维 Python 列表；表中的形状对应将一份样本放入批次后的 PyTorch 张量。不要把列表长度 3 理解成三维张量。

**代码修改与验证**

沿用实验 01 的完整代码，只需要将输入改为：

```python
inputs = [1.0, 2.0]
```

继续保留逐元素的 ReLU 处理，不需要额外求和：

```python
hidden_active = []
for value in hidden_raw:
    if value < 0.0:
        hidden_active.append(0.0)
    else:
        hidden_active.append(value)
```

运行结果：

```text
输入形状: (1, 2)
隐藏层加权和: [6.0, 1.0, -2.5]
ReLU 后: [6.0, 1.0, 0.0]
手算分数: [5.0, -10.5]
PyTorch 分数: [[5.0, -10.5]]
输出形状: (1, 2)
逐层对照: 全部一致
```

**本次遇到的问题（2026-10-06）**

本次已正确把输入改为 `[1.0, 2.0]`，但在 ReLU 循环中增加了 `Weighted_sum += value`，并在后面打印这个变量，运行时出现 `UnboundLocalError`：变量还没有赋初值，就读取它进行累加。

普通累加确实需要先初始化，不过这里应直接去掉这条累加语句和对应的打印语句。原因是 `hidden_raw` 已经分别保存三个单元的计算结果；再把它们相加，只会得到一个总数，不能代表这一层的三个输出。这里的问题既有变量未初始化，也有把“每个单元内部求和”误解为“再把所有单元的结果求和”。

`linear_by_hand()` 的内层循环累加一个单元的各项乘积，外层循环把各个单元的结果分别加入 `outputs`。进入下一个输出单元时，`total` 重新从 0 开始。移除额外的两行后，已验证手写计算与 PyTorch 逐层一致；复核时没有改写 `playground/test.py`。

**实际项目也要自己手算吗？**

不需要逐个手算，也通常不需要手写本篇的乘加循环。实际使用时定义好 `nn.Linear`、激活层和 `forward`，调用模型，由框架完成这些计算。本篇把过程展开，是为了理解每个输出怎样由输入、权重和偏置得到，并能在出现问题时检查形状和少量数值。

本例还人为指定了权重，便于对照；实际训练通常由框架初始化参数，再通过训练更新，推理时加载训练好的参数。需要自己确定的是输入特征、网络结构以及训练和验证方式，而不是逐个算出所有神经元的结果。

</details>

### 练习 2：改变隐藏层宽度

把实验 02 的隐藏层从 16 个单元改成 8 个：

1. 修改两处相关的 `Linear` 设置，让网络运行成功。
2. 写出展平、隐藏层和输出的形状。
3. 手算两层参数数量与总数，再用 `model.parameters()` 验证。
4. 如果一次输入两张图，参数数量会不会翻倍？说明理由。

<details class="exercise-answer">
<summary>点击查看第二题参考答案与要点</summary>

**参考答案**

两处需要一起改：`Linear(3072, 8)` 产生 8 个特征，下一层就必须是 `Linear(8, 2)`。如果只改第一处，第二层仍然等待 16 个输入，会发生形状不匹配。

| 阶段 | 一张图 | 两张图 |
| --- | --- | --- |
| 展平 | `(1, 3072)` | `(2, 3072)` |
| 隐藏层与 ReLU | `(1, 8)` | `(2, 8)` |
| 输出 | `(1, 2)` | `(2, 2)` |

隐藏层参数为 `3072×8+8=24584`，输出层参数为 `8×2+2=18`，总数为 `24602`。输入两张图时参数不翻倍，因为两份数据使用同一套层对象和参数；变化的是本次计算的数据量。

**可独立运行的验证代码**

```python
import torch
from torch import nn


class ImageMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten(start_dim=1)
        self.hidden = nn.Linear(3 * 32 * 32, 8)
        self.relu = nn.ReLU()
        self.output = nn.Linear(8, 2)

    def forward(self, images):
        features = self.flatten(images)
        print(f"展平: {tuple(features.shape)}")
        features = self.hidden(features)
        print(f"隐藏层: {tuple(features.shape)}")
        features = self.relu(features)
        scores = self.output(features)
        print(f"输出: {tuple(scores.shape)}")
        return scores


def count_parameters(layer):
    count = 0
    for parameter in layer.parameters():
        count = count + parameter.numel()
    return count


model = ImageMLP()
model.eval()
# 全零输入只用于检查形状；实际图片仍沿用实验 02 的读取函数。
with torch.no_grad():
    images = torch.zeros((1, 3, 32, 32), dtype=torch.float32)
    scores = model(images)
    assert scores.shape == (1, 2)

print(f"隐藏层参数: {count_parameters(model.hidden)}")
print(f"输出层参数: {count_parameters(model.output)}")
print(f"总参数: {count_parameters(model)}")
assert count_parameters(model) == 24602

with torch.no_grad():
    two_images = torch.zeros((2, 3, 32, 32), dtype=torch.float32)
    two_scores = model(two_images)
    assert two_scores.shape == (2, 2)
print(f"两张图片时总参数: {count_parameters(model)}")
```

预期输出：

```text
展平: (1, 3072)
隐藏层: (1, 8)
输出: (1, 2)
隐藏层参数: 24584
输出层参数: 18
总参数: 24602
展平: (2, 3072)
隐藏层: (2, 8)
输出: (2, 2)
两张图片时总参数: 24602
```

</details>

### 练习 3：观察去掉 ReLU 的结果

使用实验 01 的原输入 `[2, -1]` 和固定参数，让第一层输出直接进入第二层：

1. 手算并打印没有 ReLU 时的两个分数。
2. 对比原网络的 `[3, -0.5]`，说明哪里发生了变化。
3. 两层的形状、参数数量是否改变？为什么即使形状相同，计算也不一样？

<details class="exercise-answer">
<summary>点击查看第三题参考答案与要点</summary>

**参考答案**

原输入 `[2, -1]` 经第一层后得到 `[1, -3, 1]`。去掉 ReLU，负数 -3 直接进入第二层：

```text
第 0 个分数：1×1 + (-1)×(-3) + 2×1       = 6
第 1 个分数：(-2)×1 + 1×(-3) + 1×1 + 0.5 = -3.5
```

保留 ReLU 时，第二个隐藏值从 -3 变成 0，输出是 `[3, -0.5]`。两种网络的隐藏层形状都为 `(1, 3)`、输出都为 `(1, 2)`，参数也都是 `9+8=17` 个，因为 ReLU 不改变形状且没有可训练参数。

形状相同只说明数值的组织方式相同，不能说明执行了相同计算。这个例子中，是否将负值截为 0，会直接改变下一层收到的数据。

**可独立运行的验证代码**

```python
import torch
from torch import nn

hidden_layer = nn.Linear(2, 3)
output_layer = nn.Linear(3, 2)
relu = nn.ReLU()

# 使用实验 01 的固定参数，便于手算对照。
with torch.no_grad():
    hidden_layer.weight.copy_(torch.tensor([
        [1.0, 2.0], [-1.0, 1.0], [0.5, -1.0]
    ]))
    hidden_layer.bias.copy_(torch.tensor([1.0, 0.0, -1.0]))
    output_layer.weight.copy_(torch.tensor([
        [1.0, -1.0, 2.0], [-2.0, 1.0, 1.0]
    ]))
    output_layer.bias.copy_(torch.tensor([0.0, 0.5]))

inputs = torch.tensor([[2.0, -1.0]])
with torch.no_grad():
    hidden_raw = hidden_layer(inputs)
    scores_without_relu = output_layer(hidden_raw)
    hidden_active = relu(hidden_raw)
    scores_with_relu = output_layer(hidden_active)

print(f"隐藏层原值: {hidden_raw.tolist()}")
print(f"不经过 ReLU: {scores_without_relu.tolist()}")
print(f"经过 ReLU: {scores_with_relu.tolist()}")
print(f"隐藏层形状: {tuple(hidden_raw.shape)}")
print(f"输出形状: {tuple(scores_without_relu.shape)}")
assert torch.allclose(scores_without_relu, torch.tensor([[6.0, -3.5]]))
assert torch.allclose(scores_with_relu, torch.tensor([[3.0, -0.5]]))
```

预期输出：

```text
隐藏层原值: [[1.0, -3.0, 1.0]]
不经过 ReLU: [[6.0, -3.5]]
经过 ReLU: [[3.0, -0.5]]
隐藏层形状: (1, 3)
输出形状: (1, 2)
```

</details>

### 练习 4：两份样本，共用一套参数

使用实验 01 的固定参数，组成形状为 `(2, 2)` 的输入：

```text
[[ 2, -1],
 [ 1,  2]]
```

1. 保留 ReLU，一次计算两份样本，打印中间形状与最终结果。
2. 使用同一套层对象分别计算两份样本，比较结果是否与批量计算一致。
3. 解释输出 `(2, 2)` 的两个轴各表示什么。
4. 某个分数最大，是否能证明这个模型已经学会真实分类？

<details class="exercise-answer">
<summary>点击查看第四题参考答案与要点</summary>

**参考答案**

输出形状 `(2, 2)` 的第一个 2 表示两份样本，第二个 2 表示每份样本的两个输出分数。第一行对应输入 `[2, -1]`，第二行对应 `[1, 2]`。

批量计算与分别计算使用完全相同的 `hidden_layer` 和 `output_layer`，每行独立经过这两层及 ReLU，因此结果一致。`batch[0:1]` 使用切片保留批次轴；`torch.cat(..., dim=0)` 沿已有批次轴把两行接起来。

分数最大的那个位置只是当前参数下得分最高的输出。本例参数由人为指定，没有用真实数据训练和评估，不能据此认定模型具备真实分类能力。

**可独立运行的验证代码**

```python
import torch
from torch import nn

hidden_layer = nn.Linear(2, 3)
output_layer = nn.Linear(3, 2)
relu = nn.ReLU()

# 使用实验 01 的固定参数，便于手算对照。
with torch.no_grad():
    hidden_layer.weight.copy_(torch.tensor([
        [1.0, 2.0], [-1.0, 1.0], [0.5, -1.0]
    ]))
    hidden_layer.bias.copy_(torch.tensor([1.0, 0.0, -1.0]))
    output_layer.weight.copy_(torch.tensor([
        [1.0, -1.0, 2.0], [-2.0, 1.0, 1.0]
    ]))
    output_layer.bias.copy_(torch.tensor([0.0, 0.5]))

batch = torch.tensor([[2.0, -1.0], [1.0, 2.0]])
with torch.no_grad():
    hidden_raw = hidden_layer(batch)
    hidden_active = relu(hidden_raw)
    batch_scores = output_layer(hidden_active)

    # 切片保留批次轴，每份输入的形状都是 (1, 2)。
    first_input = batch[0:1]
    second_input = batch[1:2]
    first_hidden = hidden_layer(first_input)
    first_active = relu(first_hidden)
    first_scores = output_layer(first_active)
    second_hidden = hidden_layer(second_input)
    second_active = relu(second_hidden)
    second_scores = output_layer(second_active)
    separate_scores = torch.cat([first_scores, second_scores], dim=0)

print(f"输入: {tuple(batch.shape)}")
print(f"隐藏层: {tuple(hidden_raw.shape)}")
print(f"ReLU: {tuple(hidden_active.shape)}")
print(f"输出: {tuple(batch_scores.shape)}")
print(f"批量结果: {batch_scores.tolist()}")
print(f"分别计算: {separate_scores.tolist()}")
print(f"结果一致: {torch.allclose(batch_scores, separate_scores)}")
assert torch.allclose(batch_scores, torch.tensor([[3.0, -0.5], [5.0, -10.5]]))
assert torch.allclose(batch_scores, separate_scores)
```

预期输出：

```text
输入: (2, 2)
隐藏层: (2, 3)
ReLU: (2, 3)
输出: (2, 2)
批量结果: [[3.0, -0.5], [5.0, -10.5]]
分别计算: [[3.0, -0.5], [5.0, -10.5]]
结果一致: True
```

</details>

## 学完本篇之后

接下来学习《亲手搭建一个小型 CNN》，把已经熟悉的全连接层与激活保留下来，再增加卷积和池化。完成前向计算后，才进入标签、损失、梯度和参数更新的训练阶段。

## 综合实践

想把这些知识接成一套可运行的代码，可以进入[实现 MLP：从损失计算、训练到 ONNX 推理](/posts/vision-mlp-practice.html)。实践包含自生成数据、训练与验证、模型保存、独立推理、ONNX 导出和数值对照；遇到问题可按实践中的索引返回对应理论章节。
