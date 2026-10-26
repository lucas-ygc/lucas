# 让模型开始学习

先运行一次参数更新，再学习完整训练循环。在本目录打开终端：

```bash
python3 01_one_update.py
python3 02_train_stripes.py
```

本章只依赖 PyTorch。已有前几章环境可直接运行；新环境使用：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
```

代码全部使用 CPU。第二个实验在内存生成 256 张训练图片与 64 张验证图片，不下载外部数据、不保存模型或图片。无需其他文章目录的辅助代码。

类别 0=横条纹，1=竖条纹；训练与验证使用不同随机种子生成。它们来自同一种简单生成规则，不代表真实世界泛化能力，也不能当作人脸遮挡模型。

建议先只读 `01_one_update.py`。理解一次更新后，再读 `02_train_stripes.py` 中 `main()` 的内层训练循环，最后回看数据生成和评估函数。使用普通循环，不需要列表推导式。

固定种子方便同环境复现，版本或硬件变化可能使数值不同。实验记录见 `verification.md`。CPU 安装参考 [官方说明](https://pytorch.org/get-started/locally/)。
