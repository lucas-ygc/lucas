# 亲手搭建一个小型 CNN

在本目录打开终端，依次运行：

```bash
python3 01_manual_convolution.py
python3 02_tiny_cnn.py
python3 02_tiny_cnn.py /你的图片路径/photo.jpg
```

第一个实验对照手写循环与固定权重的单通道卷积。第二个实验将图片统一为 32×32 RGB，观察未训练 CNN 的逐层形状与输出。全部使用 CPU，不下载数据集，不训练、不保存模型、不修改输入图片。

`sample.ppm` 随本目录提供。路径相对于脚本定位，代码目录可以独立移动；不依赖其他文章或 playground。

## 新环境

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
```

已有上一章的环境可以直接使用。NumPy、Pillow 由 requirements.txt 提供，PyTorch 单独安装；CPU 安装方式见 [官方说明](https://pytorch.org/get-started/locally/)。

`02_tiny_cnn.py` 中 `TinyCNN` 固定接收空间尺寸为 32×32 的三通道张量，批次数可以变化。不要直接输入其他高宽，否则展平后的长度可能与 Linear 层不匹配。

运行记录见 [verification.md](verification.md)。固定随机种子方便同环境对照，跨 PyTorch 版本或平台不保证得到完全相同的分数。
