---
title: 从零搭建视觉模型 · 综合实践：实现 MLP，从损失计算、训练到 ONNX 推理
date: 2026-10-23 00:00:00
categories: AI-深度学习
tags:
  - 从零搭建视觉模型
  - MLP
  - PyTorch
  - ONNX
  - 综合实践
description: 用自包含的条纹数据实现 MLP，核对交叉熵与梯度，完成训练、验证、保存、独立推理、ONNX 导出及数值一致性检查。
abbrlink: vision-mlp-practice
draft: false
cover: ../images/封面.svg
code:
  inline: true
  files:
    - .gitignore
    - model.py
    - dataset.py
    - loss_demo.py
    - train.py
    - predict.py
    - export_onnx.py
    - predict_onnx.py
    - requirements.txt
    - README.md
    - verification.md
  experiments:
    - id: loss
      title: 实验 01：显式计算损失并核对梯度
      file: loss_demo.py
      command: python3 loss_demo.py
    - id: train
      title: 实验 02：训练并保存 MLP
      file: train.py
      related_files:
        - model.py
        - dataset.py
      command: python3 train.py
    - id: predict
      title: 实验 03：独立加载模型并推理
      file: predict.py
      command: python3 predict.py
    - id: export
      title: 实验 04：导出 ONNX 并验证一致性
      file: export_onnx.py
      command: python3 export_onnx.py
    - id: onnx-predict
      title: 实验 05：不依赖 PyTorch 的 ONNX 推理
      file: predict_onnx.py
      command: python3 predict_onnx.py
---

这是一篇可以从头运行到最后的综合实践。我们自己定义 MLP 结构、编写数据与训练循环、显式计算损失，再保存模型，分别用 PyTorch 和 ONNX Runtime 完成独立推理。反向传播由 PyTorch 自动求导，本篇不手写每一层的反向传播引擎。

学完第 8 章就可以开始动手，遇到问题再查后面的理论章节；合集阅读顺序将本篇放在第 15 章之后。最后的 ONNX 部分提前串起第 22 章。实验全部在 CPU 上运行，不下载数据集或预训练权重，每个辅助模块都在本篇 `code/` 内。

## 先明确最终要交付什么

任务是判断一张 16×16 灰度图含有的是横条纹还是竖条纹。类别 0 为横条纹，类别 1 为竖条纹。输入有噪声，条纹的位置和宽度会变化。

```text
生成图片与标签 → MLP 输出 logits → 计算交叉熵 → 反向传播 → 更新参数
                                      ↓ 每轮验证
                                保存最佳 best.pt
                                      ↓
                      独立 PyTorch 推理 → 导出 model.onnx
                                               ↓
                                   数值对照 → ONNX 独立推理
```

最终得到 `best.pt`、`history.csv`、两张演示 PNG 和 `model.onnx`。这里的模型只学习合成条纹，不能用任意风景照、飞机照片来检验它是否“认识物体”。

## 第一步：准备环境并跑完整流程

下载本篇完整代码包并解压，在解压目录打开终端。不要只下载 `train.py`，它需要同目录的模型和数据模块。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python loss_demo.py
python train.py
python predict.py
python predict.py outputs/vertical.png
python export_onnx.py
python predict_onnx.py
python predict_onnx.py outputs/vertical.png
```

默认输出在脚本旁的 `outputs/`，不受启动时工作目录影响。上面带相对图片路径的命令应在代码目录运行。第一次先用默认参数跑通；训练完成后再运行依赖其产物的推理和导出步骤。

| 文件 | 负责什么 |
| --- | --- |
| `model.py` | 网络结构、图片尺寸与类别顺序 |
| `dataset.py` | 合成图片、保存 PNG、读取与预处理 |
| `loss_demo.py` | 交叉熵显式公式与梯度对照 |
| `train.py` | 训练、验证选优、最终测试、保存与加载检查 |
| `predict.py` | 从文件加载权重后进行单图预测 |
| `export_onnx.py` | 导出训练好的网络并验证数值一致性 |
| `predict_onnx.py` | 用 ONNX Runtime 读取图片并预测，不导入 PyTorch |

### 执行顺序由文件产物决定

| 脚本 | 运行前需要已有 | 运行后新增 |
| --- | --- | --- |
| `loss_demo.py` | 无 | 无，只打印对照结果 |
| `train.py` | 无 | `best.pt`、`history.csv`、`horizontal.png`、`vertical.png` |
| `predict.py` | `best.pt`，图片用 `outputs/horizontal.png` 或自己指定 | 无，只打印预测 JSON |
| `export_onnx.py` | `best.pt`，且 `train.py` 在同目录 | `model.onnx` |
| `predict_onnx.py` | `model.onnx`、图片 | 无，只打印预测 JSON |

这个顺序不是文档约定，而是脚本自身的硬约束：推理和导出脚本默认读取 `outputs/` 下的文件，先运行它们只会得到"找不到文件"。`export_onnx.py` 还 `from train import ...`，复用检查点加载与约定校验，所以 `train.py` 必须留在同目录；真正能单独拷走运行的只有 `predict_onnx.py`（见第十步）。用 `train.py --out` 改换产物目录时（练习 2 会这样做），下游脚本的默认路径就找不到文件，必须用 `--checkpoint`、`--model` 和图片参数逐个显式指向同一目录。

五张实验卡片遵循同一约束：卡片 01 任何时候都能运行；03 与 04 需要先运行 02；05 需要先运行 04。

依赖版本与实际输出见代码包的 `verification.md`。代码文件在文章实验卡片中可展开阅读，也可整体下载。

## 第二步：知道输入与标签长什么样

`make_dataset()` 在暗背景上加入一条亮色横带或竖带，再叠加随机噪声。数据先量化为 0～255 的整数像素，再除以 255，确保训练张量与后面保存为 PNG、重新读取的张量保持一致。

| 数据 | 形状或类型 | 含义 |
| --- | --- | --- |
| 一个批次图片 | `[N, 1, 16, 16]`，float32 | N 张单通道图片，值在 0～1 |
| 标签 | `[N]`，int64 | 每张图片一个整数类别编号 |
| 网络输出 | `[N, 2]`，float32 | 每张图片两个原始分数 |

训练集 512 张、验证集 128 张、测试集 128 张，分别使用随机种子 100、200、300。训练集打乱顺序；验证集与测试集不参与参数更新。生成器相同、随机采样独立，因此它们仍是同一个简单合成分布，不等于检验了真实场景泛化。

种子 400 生成两张用于推理的演示图片，种子 500 生成 ONNX 数值对照样本。它们都不参与训练和验证选优。

形状不清楚时回看[第 3 章：张量基础](/posts/vision-foundations-pixels-tensors.html)；不理解划分目的时看[第 9 章：数据与划分](/posts/vision-dataset-splits.html)。

## 第三步：自己定义 MLP

本篇不用卷积。将 16×16 的像素展平为 256 个输入数，经过 32 个隐藏单元，最后输出两类分数：

```text
[N,1,16,16] → Flatten → [N,256]
            → Linear(256,32) → ReLU → [N,32]
            → Linear(32,2) → [N,2]
```

核心计算为：

```python
x = self.flatten(images)
x = self.relu(self.hidden(x))
return self.output(x)
```

第一层包含 `256×32 + 32 = 8224` 个参数，第二层包含 `32×2 + 2 = 66` 个参数，共 8290 个。ReLU 不增加可训练参数。两个线性层之间加入非线性，避免整个网络退化为一个更大的线性变换。

最后不加 Softmax，因为后面的交叉熵直接接收 logits。需要展示概率时，在推理阶段再计算。`forward()` 定义如何用当前参数算输出，调用它本身不会训练网络。

如果想逐项看清一个输出怎样由输入和权重得到，回看[第 5 章：MLP 入门](/posts/vision-mlp-basics.html)。

## 第四步：把损失算明白

先运行 `loss_demo.py`，暂时不涉及图片或网络参数。输入两组 logits `[[2,1],[0,2]]`，两个正确标签都是 1。

单样本交叉熵为正确类别概率的负自然对数：

```text
L = -ln(p[y])
  = logsumexp(logits) - logits[y]
```

第一组正确类别概率约 0.2689，损失约 1.313262；第二组概率约 0.8808，损失约 0.126928。两样本取平均，得到约 0.720095。

脚本用 `torch.logsumexp` 写出稳定公式，再与 `F.cross_entropy` 核对。它还检查平均损失对 logits 的梯度：

```text
梯度 = (Softmax 概率 - 正确标签的 one-hot 向量) / 批次数 N
```

这里除以 N 是因为损失按样本取平均。真实训练中 logits 是 MLP 的计算结果，自动求导会沿计算图继续将梯度传回两层的权重和偏置。

本练习的显式公式只用于理解和对照，实际训练中调用 `CrossEntropyLoss`。不要先 Softmax 再将概率传给这个接口。损失不是百分比，也不是准确率。

概率的含义见[第 7 章](/posts/vision-class-prediction.html)，交叉熵和优化器见[第 10 章](/posts/vision-loss-optimizers.html)。

## 第五步：写完整训练循环

每批训练执行以下步骤：

```python
optimizer.zero_grad()
logits = model(images)
loss = loss_function(logits, labels)
loss.backward()
optimizer.step()
```

清理旧梯度后计算输出和损失，`backward()` 计算梯度，`step()` 用梯度更新参数。这里用 SGD，学习率默认 0.1，训练 30 轮，batch size 为 32。每轮 512/32=16 次更新，总共 480 次。

每轮训练开始时调用 `model.train()`。验证函数会切到 `eval()`，所以不能只在整个程序开始时调用一次 `train()`。这个 MLP 没有 Dropout 或 BatchNorm，两种模式暂时不改变输出，但仍保持完整的训练与推理写法。

每批损失默认是该批平均值。统计整轮时乘以当前批的样本数，最后除以总样本数，避免末尾小批次获得过大权重。训练损失是在参数不断更新期间累计的；验证损失是在该轮结束后的固定参数上计算，两者不能当成完全相同条件下的测量。

`train.py` 从头到尾的执行顺序是：加载三份数据后，先做一次验证，得到"训练前"的损失与准确率基线，然后才进入循环。每轮训练并验证后，只在验证损失更低时保存 `best.pt`，保存后立即回读、用同一批验证样本对照加载前后输出。循环结束后回读最佳权重评估测试集，最后生成两张演示 PNG。演示图片是训练结束时的副产品，不需要单独运行任何命令来生成。

如果参数没有更新，回看[第 8 章：训练循环](/posts/vision-training-basics.html)；轮数与学习率的问题见[第 11 章](/posts/vision-batch-epoch-lr.html)。

## 第六步：验证、选优，再做最终测试

验证阶段使用 `eval()` 与 `torch.no_grad()`，不执行 `backward()` 或 `step()`。每轮打印训练损失、验证损失与验证准确率，验证损失更低时才覆盖 `best.pt`。

训练结束后重新加载最佳权重，在测试集上评估一次。测试集不决定保存哪一轮，也不用于调学习率。若你反复根据测试结果调参，它就已经参与了开发决策，需要另外保留最终测试数据。

本篇每次保存时都用相同的验证输入比较加载前后输出，确认权重确实能够恢复。判断训练是否成功，应结合损失、准确率和独立推理检查，不能只看程序没有报错。

评价方法见[第 14 章：验证与错误分析](/posts/vision-evaluation.html)。若训练损失下降而验证损失变坏，结合[第 13 章：过拟合](/posts/vision-generalization.html)分析。

## 第七步：退出训练程序后独立推理

`predict.py` 在新进程中建立相同的 MLP，加载 `best.pt`，读取图片并执行预测。默认使用生成的横条纹 PNG，也可以显式指定另一张图片。

检查点保存以下信息：网络结构版本、参数、类别表、灰度、尺寸与缩放约定、最佳轮次和验证损失。加载时检查这些约定，防止把两个输出分数解释成错误的类别。

图片转换为灰度后必须是 16×16，本实验不静默缩放。像素转为 float32、除以 255，添加批次与通道维，得到 `[1,1,16,16]`。预测输出是 JSON，包含 `class_id`、`class_name`、`score`、`logits`。

`score` 为 Softmax 最大值，不能保证现实场景下的正确率。这里也没有自动拒绝未知图片的能力。

当前保存的是推理检查点，没有优化器历史与随机状态，不能声称支持精确恢复训练。相关概念见[第 15 章：保存与独立推理](/posts/vision-checkpoint-inference.html)。

## 第八步：将训练好的 MLP 导出为 ONNX

运行 `export_onnx.py`。它加载刚才保存的最佳权重，切换到推理模式，并导出 `outputs/model.onnx`。导出的不是另一个随机初始化的模型。

| 接口 | 约定 |
| --- | --- |
| 输入名称 | `images` |
| 输入形状与类型 | 固定 `[1,1,16,16]`，float32 |
| 输入范围 | 灰度值除以 255，0～1 |
| 输出名称 | `logits` |
| 输出形状 | `[1,2]`，原始类别分数 |
| 图外操作 | 读图、灰度转换、缩放与布局、Softmax、类别映射 |
| 导出设置 | opset 17，显式 `dynamo=False` |

本篇与第 22 章保持相同的传统导出路径，运行时可能出现弃用提示；这不代表推荐所有新项目都采用同一导出路径。此处没有启用动态 batch 或动态宽高，修改输入形状必须同步修改网络和接口检查。

ONNX 不只包含参数，还描述计算图。我们将类别表与预处理约定写入模型 metadata，供独立程序读取。ONNX 本身不会替我们读取 PNG 或自动返回中文类别名。

导出接口与工具兼容问题见[第 22 章：从训练模型到 ONNX](/posts/vision-onnx-export.html)。

## 第九步：确认导出前后计算一致

导出文件后先运行 `onnx.checker`，再创建 ONNX Runtime CPU 会话。检查器通过不等于计算结果已经正确，还要比较两个后端的输出。

本篇逐个比较种子 500 生成的 128 张新条纹图，以及四个特殊输入：全零、全一、0.5 常量，和种子 600 生成的随机噪声。对每个输入检查：

1. 输出形状都是 `[1,2]`。
2. 两个 logits 满足 `rtol=1e-4, atol=1e-5` 的数值容差。
3. 最大分数对应的类别一致。

特殊输入用于检查转换数值，不要求模型对它们给出有意义的分类。程序报告最大绝对误差与类别一致数量；实际运行记录见代码包。

只检查类别相同不够，因为分数可能已经产生偏差，却尚未翻转类别。数值不一致时应检查输入布局、缩放、模型权重和算子行为，不能先放宽容差掩盖问题。

## 第十步：不依赖 PyTorch 运行 ONNX

`predict_onnx.py` 只导入 NumPy、Pillow 和 ONNX Runtime。它从 ONNX metadata 读取类别及预处理约定，检查输入接口后读取图片，运行计算图，再在 NumPy 中执行稳定 Softmax。

可以把这一个脚本、`model.onnx` 和演示图片复制到另一个目录或环境：

```bash
python -m pip install numpy Pillow onnxruntime
python predict_onnx.py horizontal.png --model model.onnx
```

这里不需要 `model.py`、`train.py` 或 `best.pt`。这一步完成了训练框架之外的独立推理。ONNX Runtime CPU 能执行，并不代表某块 NPU 已经支持该模型；板端转换与运行属于后续部署课程。

## 本次实际运行结果

2026-10-23 在 CPU 上运行默认配置，得到以下结果。完整依赖版本与逐轮输出保存在 `verification.md`。

| 检查项 | 实际结果 |
| --- | --- |
| 训练前验证损失 / 准确率 | 0.6949 / 50.0% |
| 最佳轮次 | 第 30 轮 |
| 最佳验证损失 / 准确率 | 0.0046 / 100.0% |
| 最终测试损失 / 准确率 | 0.0049 / 100.0% |
| 两张演示图片 | 横、竖条纹均分类正确 |
| ONNX 数值比较 | 132 个输入通过容差检查 |
| ONNX 最大绝对误差 | 约 1.67×10⁻⁶ |
| 两后端类别一致 | 132/132 |

这是一个故意设计得容易学习的任务，用来检查整条代码流程。不同依赖版本的具体数值可能变化，也不能把这里的 100% 推广到真实图片任务。

## 遇到问题从这里查

| 现象 | 本篇先检查 | 对应理论 |
| --- | --- | --- |
| 矩阵形状不匹配 | 图片是否 16×16、Flatten 后是否 256 | [第 5 章](/posts/vision-mlp-basics.html) |
| 损失输入报错 | logits 是否 `[N,2]`，标签是否整数 `[N]` | [第 10 章](/posts/vision-loss-optimizers.html) |
| 有梯度但参数没更新 | 是否执行 step、学习率是否合理 | [第 8 章](/posts/vision-training-basics.html) |
| 训练好、验证差 | 数据划分、样本规模与过拟合 | [第 9 章](/posts/vision-dataset-splits.html)、[第 13 章](/posts/vision-generalization.html) |
| 换进程后预测变化 | 是否加载最佳权重、预处理和类别映射是否一致 | [第 15 章](/posts/vision-checkpoint-inference.html) |
| 找不到模型或示例图片 | 是否先运行 train.py，自定义路径是否配套指定 | 本篇第一步与 README |
| ONNX 输入形状错误 | 本篇只导出 batch=1 的固定输入 | [第 22 章](/posts/vision-onnx-export.html) |
| ONNX 与 PyTorch 数值不一致 | 是否对同一张量、同一权重进行比较 | [第 22 章](/posts/vision-onnx-export.html) |

## 用三个练习检查自己能否独立完成

1. 将隐藏层改为 16 个单元，重新训练、保存、导出并推理。说明哪些文件或结构标识需要同步修改，为什么旧权重不能直接加载。
2. 用不同学习率各训练一次，将产物保存到不同 `--out` 目录，比较验证损失曲线。选好配置前不要根据测试集结果挑参数。
3. 把 ONNX 推理脚本与模型复制到独立目录，分别预测两张演示图片，与 PyTorch 的类别和 logits 对照。

完成标准不是记住命令，而是能解释输入形状、损失来源、哪一步更新了参数、为什么选这份权重，以及 ONNX 导出前后怎样判断计算是否一致。

---

[完整阅读目录](/series/vision-learning/) · [上一篇：保存与独立推理](/posts/vision-checkpoint-inference.html) · [下一篇：ResNet](/posts/vision-resnet.html)
