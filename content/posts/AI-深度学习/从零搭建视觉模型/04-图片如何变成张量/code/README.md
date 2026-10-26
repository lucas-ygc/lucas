# 图片如何变成张量

在本目录打开终端；如果下载了代码压缩包，先解压并进入解压目录。

```bash
python3 main.py
python3 main.py --resize 320 224
python3 main.py /你的图片路径/photo.jpg
```

`sample.ppm` 是一张宽 3、高 2 的 RGB 图片。默认实验只读取它，在 CPU 上输出 HWC → CHW → NCHW 的形状、数据类型与像素值，不训练模型，也不改写输入文件。

## 新环境安装

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python main.py
```

`requirements.txt` 提供 NumPy 与 Pillow。PyTorch 单独安装，方便以后选择合适的计算平台；以上是 Linux CPU 安装方式，参考 [官方安装说明](https://pytorch.org/get-started/locally/)。

本机验证环境为 Python 3.13.9、PyTorch 2.13.0+cu130、NumPy 2.3.5、Pillow 10.4.0，计算使用 CPU。实际输出见 [verification.md](verification.md)。

## 对照观察

1. `image.size` 为 `(宽, 高)`，NumPy 数组为 `(高, 宽, 通道)`。
2. 默认例子的最终形状为 `(1, 3, 2, 3)`。
3. `--resize 320 224` 的最终形状为 `(1, 3, 224, 320)`。
4. `pixels[0, 0]` 与 CHW 布局中的 `chw[:, 0, 0]` 对应同一个像素。

代码、输入数据、依赖说明都在当前目录，整份目录可独立移动和运行。
