# MLP 入门

在本目录运行，先手算，再接图片：

```bash
python3 01_manual_mlp.py
python3 02_image_mlp.py
python3 02_image_mlp.py /你的图片路径/photo.jpg
```

实验 01 使用固定权重，逐层比较 Python 列表计算和 PyTorch 的结果。实验 02 使用随机初始化的图片 MLP，统一读取为 32×32 RGB。两个实验只做 CPU 前向计算，不下载数据集、不训练、不修改图片。

已有上一章的 Python 环境可以直接运行。新环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
```

依赖安装参考 [PyTorch 官方说明](https://pytorch.org/get-started/locally/)。输入图片随本目录提供，路径根据脚本位置定位，不依赖其他文章目录或 playground。整份目录可独立移动运行。

`ImageMLP` 按 `(N, 3, 32, 32)` 输入设计；改变图片大小时也需要修改第一层输入特征数。实验 01 的 `linear_by_hand` 使用普通下标循环，每行权重数量应等于输入数量，偏置数量应等于输出单元数量。它只用于本例尺寸已经匹配的列表，暂不做通用维度检查。

建议先阅读手算部分直到 `manual_scores`，再看 PyTorch 对照部分。正文提供循环逐步执行表，以及 Python 下标循环与 C/C++ 的对应解释。

运行记录见 [verification.md](verification.md)。随机种子方便在同环境复现，但跨版本或平台不保证分数完全相同。
