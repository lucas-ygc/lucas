# Python 起步，写给 C/C++ 开发者

目标：能读懂并修改下一课的图片读取代码。先学前 3 个实验，每次只运行一个文件，改一个参数，再解释输出。

前 5 个实验仅使用 Python 标准库，无需安装 PyTorch、无需 GPU。第 6 个使用 Pillow 和 NumPy，把基础语法接回图片实验。

## 从这里开始

先在本篇文章的 `code/` 目录打开终端；下载压缩包的读者进入解压目录。然后运行：

```bash
python3 01_variables.py
```

打开 `01_variables.py`，把 `width` 改成 `10`、`height` 改成 `4`，先猜输出，再运行。完成这一项再继续。

## 实验顺序

| 文件 | 学习内容 | 动手改一处 |
| --- | --- | --- |
| `01_variables.py` | 类型、输出、f-string、除法、类型转换 | 比较 `5 / 2`、`5 // 2`、`-5 // 2` |
| `02_containers.py` | 列表、元组、字典、索引、切片、共享对象 | 猜测修改 `alias` 和 `copied` 的区别 |
| `03_flow_functions.py` | 缩进、分支、循环、函数、异常 | 将 `values` 改为 `[0, 64, 128, 255]`，并把 `range(3)` 改为 `range(len(values))` |
| `04_modules_files.py` | `import`、自定义模块、文件路径、`with` | 直接运行 `pixel_math.py`，比较它被导入时的行为 |
| `05_classes.py` | 类、`self`、`__init__`、继承、`super` | 将图片尺寸改为宽 5、高 4，算出像素数与通道数值总数 |
| `06_read_pixels.py` | NumPy 数组、形状和多维切片 | 把 `pixels[:, :, 0]` 改成 `pixels[:, :, 1]` |

例如，学习到第二个实验时执行：

```bash
python3 02_containers.py
```

其余文件同样替换文件名运行。每个示例的实际输出保存在 [verification.md](verification.md)，先自己猜测，再对照。

## 安装依赖与运行位置

代码在本机终端运行。博客 Docker 容器用于网站预览。

- 标准库：例如 `pathlib`，随 Python 提供，直接 `import`。
- 第三方包：例如 Pillow、NumPy，需要安装到当前 Python 环境。
- `import` 负责导入模块；`python -m pip install ...` 负责安装包。
- 安装名和导入名可能不同：安装 `Pillow`，代码写 `from PIL import Image`。

本机已有第 6 个实验的依赖。新环境在当前目录安装：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python 06_read_pixels.py
```

依赖说明、辅助模块 `pixel_math.py` 和示例图片 `sample.ppm` 都在当前目录，整份目录可独立移动和运行。本课暂不需要安装 PyTorch。

## 课后练习

文章末尾有 6 道具体编程题，每题提供输入、要求与预期结果：

1. 计算图片信息并返回字典。
2. 修正越界通道值，保留原列表。
3. 按像素数筛选图片。
4. 读取 `sample.ppm` 中的字段和像素。
5. 编写能更新尺寸的 `ImageInfo` 类。
6. 读取像素与通道，并修改数组副本。

在当前目录新建 `practice_01.py` 到 `practice_06.py` 自己完成，例如运行 `python3 practice_01.py`。练习不附实现答案。

文章标题：《Python 起步：写给 C/C++ 开发者》。下一课：《图片如何变成张量》。

[Python 官方教程](https://docs.python.org/3/tutorial/index.html)
