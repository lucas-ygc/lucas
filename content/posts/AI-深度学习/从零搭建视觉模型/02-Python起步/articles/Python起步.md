---
title: 从零搭建视觉模型 02：Python 起步，写给 C/C++ 开发者
date: 2026-09-23 00:00:00
categories: AI-深度学习
tags:
  - 从零搭建视觉模型
  - Python
  - 学习笔记
description: 用 C/C++ 的已有经验理解 Python，从变量、容器和函数开始，逐步读懂图片加载与像素访问代码。
abbrlink: vision-02-python-basics
cover: ../images/封面.png
draft: false
code:
  inline: true
  files:
    - .gitignore
    - 01_variables.py
    - 02_containers.py
    - 03_flow_functions.py
    - 04_modules_files.py
    - 05_classes.py
    - 06_read_pixels.py
    - README.md
    - pixel_math.py
    - requirements.txt
    - sample.ppm
    - verification.md
  experiments:
    - id: variables
      title: 实验 01：变量与输出
      file: 01_variables.py
      command: python3 01_variables.py
    - id: containers
      title: 实验 02：容器与切片
      file: 02_containers.py
      command: python3 02_containers.py
    - id: flow
      title: 实验 03：循环与函数
      file: 03_flow_functions.py
      command: python3 03_flow_functions.py
    - id: modules
      title: 实验 04：模块与文件
      file: 04_modules_files.py
      related_files: [pixel_math.py, sample.ppm]
      command: python3 04_modules_files.py
    - id: classes
      title: 实验 05：类与实例
      file: 05_classes.py
      command: python3 05_classes.py
    - id: pixels
      title: 实验 06：读取图片像素
      file: 06_read_pixels.py
      command: python3 06_read_pixels.py
---

> “从零搭建视觉模型”系列的 Python 入门篇。先完成变量、容器和函数三个小实验，再逐步回到图片读取。文末提供 6 道动手练习，按顺序完成即可。

## 这一课要解决的问题

已经会 C、C++ 和 Shell，理解分支、循环和函数。接下来需要把这些概念对应到 Python，读懂视觉实验里的代码。

本课目标很具体：能独立运行一个 `.py` 文件，修改变量、写一个函数，最后读出一张图片的尺寸和一个像素。

配套目录为 `content/posts/AI-深度学习/从零搭建视觉模型/02-Python起步/code/`。各节实验中的完整代码默认折叠，点击文件名即可在正文展开；也可以下载代码或复制运行命令。前 5 个实验使用标准库，第 6 个才需要 Pillow 和 NumPy。所有代码都在本机终端运行。

## 1. 先运行一个 Python 文件

```experiment
variables
```

在博客项目根目录执行：

```bash
python3 content/posts/AI-深度学习/从零搭建视觉模型/02-Python起步/code/01_variables.py
```

和运行 Shell 脚本类似，这里把脚本路径交给解释器。源文件的后缀是 `.py`。直接执行 `python3` 会进入交互模式，看到 `>>>` 后可以逐行输入代码，用 `exit()` 退出。

打开第一个示例，找到这些代码：

```python
width = 3
height = 2
name = "sample.ppm"
print(f"宽={width}, 高={height}, 像素数={width * height}")
```

与 C++ 相比，赋值前不用声明 `int` 或 `std::string`，行末通常也不写分号。`f"...{表达式}..."` 是格式化字符串，花括号中的表达式会先计算，再插入文字。

对象仍然有类型，`type(width)` 可以查看。一个名字可以先绑定整数，再重新绑定字符串，但字符串 `"255"` 和整数 `255` 不是同一种东西，显式转换可写 `int("255")`。

**动手：把宽改为 10、高改为 4，先猜输出，再运行。**

## 2. 先留意几个语法差异

| C/C++ 中熟悉的写法 | Python 对应写法或区别 |
| --- | --- |
| `{ ... }` 表示代码块 | 冒号后换行，用一致的缩进表示代码块，示例采用 4 个空格 |
| `//` 行注释 | `#` 行注释；Python 的 `//` 是向下取整除法 |
| `true`、`false` | `True`、`False` |
| `&&`、`\|\|`、`!` | `and`、`or`、`not` |
| `nullptr` 表示空指针 | `None` 常用于表示没有值；它不是 C++ 空指针 |
| `i++` | `i += 1` |
| 两个整数相除，结果是整数 | Python 的 `/` 做普通除法，`5 / 2` 得到 `2.5` |

`5 // 2` 得到 `2`，但 `-5 // 2` 得到 `-3`：它向负无穷取整，与 C++ 整数除法朝零截断的行为不同。数字、字符串和基本索引的说明可查阅 [Python 入门文档](https://docs.python.org/3/tutorial/introduction.html)。

## 3. 列表、元组、字典：先认识这三种容器

```experiment
containers
```

运行 `02_containers.py`，观察下列三种数据：

```python
rgb = [255, 128, 0]
size = (3, 2)
info = {"width": 3, "height": 2, "mode": "RGB"}
```

| 类型 | 本课用途 | 与 C++ 的类比及边界 |
| --- | --- | --- |
| 列表 `list` | 保存一组像素通道值 | 可以像动态数组一样索引和追加，但不能当作固定元素类型的连续数值缓冲区 |
| 元组 `tuple` | 表达尺寸这样的组合 | 用来组合多个值；元组中的元素位置不能重新赋值 |
| 字典 `dict` | 根据名称查找宽、高、模式 | 类似键值映射，使用 `info["width"]` 取值 |

下标从 0 开始。`rgb[0]` 是红通道，`rgb[-1]` 是最后一个通道。`rgb[:2]` 是切片，取下标 0、1，不包含下标 2。这里对列表切片会得到一个新列表。

元组还可以解包：

```python
width, height = size
```

相当于把两个位置的值分别绑定到两个名字。元组自身不可变，但它包含的可变对象本身仍可以变化。本例只放整数，暂时不用处理嵌套对象。

### 列表赋值不会自动复制

C++ 中 `std::vector<int> copied = original;` 通常得到独立的一份元素副本。Python 的下面两行则不同：

```python
alias = rgb
alias[0] = 100
```

`alias` 和 `rgb` 指向同一个列表，因此通过 `rgb[0]` 也会看到 100。可以用 `alias is rgb` 判断是不是同一个对象；`==` 比较值，二者不要混用。

```python
copied = rgb.copy()
copied[0] = 50
```

这里建立了一个新的外层列表，修改其中的整数项不会改变 `rgb`。`copy()` 是浅拷贝，内部如果还放着列表，那些内部对象仍然共享。示例最后几行专门演示了这个区别。[容器文档](https://docs.python.org/3/tutorial/datastructures.html)、[对象别名说明](https://docs.python.org/3/tutorial/classes.html)

## 4. 把熟悉的循环和函数换一种写法

```experiment
flow
```

C++ 的这段循环：

```cpp
for (int i = 0; i < 3; ++i) {
    std::cout << i << '\n';
}
```

在 Python 中可以写成：

```python
for i in range(3):
    print(i)
```

`range(3)` 依次产生 0、1、2。也可以直接遍历列表的值：

```python
values = [0, 128, 255]
for value in values:
    print(value)
```

函数由 `def` 定义，参数名后不要求写类型。本课这个函数把一个数除以最大值：

```python
def scale_pixel(value, maximum=255):
    if maximum <= 0:
        raise ValueError("maximum 必须大于 0")
    return value / maximum
```

`maximum=255` 是默认参数。`scale_pixel(128)` 使用默认值；`scale_pixel(value=128, maximum=255)` 按参数名传参；`return` 返回结果。这里用数字作为默认值，后续遇到列表默认参数时，要注意这个默认对象在多次调用之间会被共享。

`raise` 抛出异常，`try` / `except` 负责捕获。读错误信息时，通常先看最后一行的异常类型和说明，再沿着调用栈定位文件和行号。`03_flow_functions.py` 演示了一次故意触发并捕获的错误。[控制流与函数文档](https://docs.python.org/3/tutorial/controlflow.html)

**先到这里停一下：自己写一个 `pixel_count(width, height)` 函数，返回总像素数。**

## 5. import、模块和文件路径

```experiment
modules
```

继续运行 `04_modules_files.py`，其中有：

```python
from pathlib import Path
from pixel_math import pixel_count
```

`pathlib` 是 Python 标准库，`pixel_math.py` 是本课自己写的模块。`import` 导入模块，`from ... import ...` 把其中指定的名字引入当前作用域。与 C/C++ 的文本式 `#include` 不同，Python 导入模块时会执行模块顶层代码，并通常在当前进程中缓存模块。

`pixel_math.py` 结尾使用：

```python
if __name__ == "__main__":
    main()
```

直接运行这个文件时会调用 `main()`；作为模块导入时不进入这个条件。Python 不要求必须定义名为 `main` 的函数，这只是组织代码的习惯。[模块文档](https://docs.python.org/3/tutorial/modules.html)

文件路径可以写成：

```python
lesson_dir = Path(__file__).resolve().parent
sample = lesson_dir / "sample.ppm"
```

`__file__` 是当前模块的文件路径，`resolve()` 得到解析后的绝对路径，`.parent` 取父目录。这里 `/` 被 `Path` 定义为路径拼接操作，和数字相除不是一回事。

示例接着用 `with sample.open(...) as file:` 读取文本，退出代码块时会关闭文件，可以把它类比成 C++ 的资源作用域管理（RAII）。此时读取的是 PPM 文件文本，尚未调用图片解码库。

## 6. self 对应 this，但写法不同

```experiment
classes
```

运行 `05_classes.py`。核心类的定义如下：

```python
class ImageInfo:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def pixel_count(self):
        return self.width * self.height

image = ImageInfo(3, 2)
print(image.pixel_count())
```

`self` 表示当前实例，对理解 C++ 的 `this` 有帮助，但 Python 实例方法会显式写出这个参数，调用时由绑定方法传入。它是惯用参数名，不是指针语法。

`__init__` 在实例创建后做初始化，可以先类比构造函数里的初始化工作；严格说对象创建还涉及 `__new__`，本课不需要实现它。`RGBImageInfo(ImageInfo)` 表示继承，示例通过 `super().__init__(...)` 复用父类的初始化逻辑。本课只使用简单的单继承。[类文档](https://docs.python.org/3/tutorial/classes.html)

这里的类只保存图片尺寸信息，还不是真正的图片或神经网络。

## 7. 安装包和导入模块是两件事

前面的实验不需要安装第三方包。第 6 个实验使用 NumPy 和 Pillow：

```python
import numpy as np
from PIL import Image
```

`as np` 给模块起别名。安装时包名叫 `Pillow`，导入时使用 `PIL`，安装名与导入名可能不同。

本机已经有这些依赖。如果以后在新环境安装，可在项目根目录执行：

```bash
cd content/posts/AI-深度学习/从零搭建视觉模型/02-Python起步/code
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

`venv` 为项目建立独立的包环境，`python -m pip` 使用当前 Python 对应的包管理工具。退出环境执行 `deactivate`。虚拟环境不是 Docker；默认也不会自动带入系统里已有的第三方包。[虚拟环境文档](https://docs.python.org/3/tutorial/venv.html)

这些命令用于新环境安装依赖；本课前 5 个实验只用标准库，现在可以先跳过。

## 8. 最后读出一个像素

```experiment
pixels
```

在项目根目录执行：

```bash
python3 content/posts/AI-深度学习/从零搭建视觉模型/02-Python起步/code/06_read_pixels.py
```

脚本的主要操作是：

```python
with Image.open(sample) as source:
    image = source.convert("RGB")

pixels = np.array(image, dtype=np.uint8, copy=True)
print(pixels.shape)
print(pixels[0, 0])
```

`pixels` 是 NumPy 数组，有统一的数据类型，可以进行多维索引。示例图片宽 3、高 2，输出形状是 `(2, 3, 3)`，对应高、宽、通道；左上角是 `[255, 0, 0]`。

`pixels[0, 0]` 选择第 0 行、第 0 列，保留通道；`pixels[:, :, 0]` 中的两个冒号分别保留全部行、列，最后的 0 选择红通道。普通嵌套 Python 列表访问一般写作 `rows[0][0]`，不能直接照搬 NumPy 的多维索引语法。

配套实验的实际输出保存在 `code/verification.md`。完成本课后，先阅读[《视觉模型入门：从像素到张量的基础概念》](/posts/vision-foundations-pixels-tensors.html)，理解维度、类型和数值缩放，再继续《图片如何变成张量》的 PyTorch 实验。

## 课后练习

下面 6 道练习由易到难。各题的参考答案与易错点放在题目下方，点击后才展开，建议独立完成后再查看。请在本篇 `code/` 目录中新建 `practice_01.py` 到 `practice_06.py`，分别完成；已有示例文件保留，方便对照。

前 5 题只用 Python 标准库，第 6 题使用已经安装的 Pillow 和 NumPy。每题写完后，在文件末尾调用自己的函数、打印结果，再运行检查。例如：

```bash
python3 practice_01.py
```

### 练习 1：计算图片的信息

编写函数 `image_info(width, height, channels=3)`，返回一个字典，包含以下键：

- `width`、`height`、`channels`：传入的尺寸和通道数。
- `pixels`：图片的像素总数。
- `bytes`：像素数据的字节数，假设每个通道占 1 字节，不计算文件头和压缩。

调用示例与预期结果：

```python
image_info(3, 2)
# {"width": 3, "height": 2, "channels": 3, "pixels": 6, "bytes": 18}

image_info(4, 5, channels=1)
# {"width": 4, "height": 5, "channels": 1, "pixels": 20, "bytes": 20}
```

字典的显示顺序不作要求，键和值正确即可。用 f-string 再打印一句：`宽=3, 高=2, 像素数=6, 字节数=18`。

<details class="exercise-answer">
<summary>点击查看第一题参考答案与本次易错点</summary>

**参考答案**

本题假定传入正整数，每个通道占 1 字节：

```python
def image_info(width, height, channels=3):
    pixels = width * height
    return {
        "width": width,
        "height": height,
        "channels": channels,
        "pixels": pixels,
        "bytes": pixels * channels,
    }


def main():
    image = image_info(3, 2)
    print(image)
    print(
        f"宽={image['width']}, 高={image['height']}, "
        f"像素数={image['pixels']}, 字节数={image['bytes']}"
    )
    print(image_info(4, 5, channels=1))


if __name__ == "__main__":
    main()
```

预期输出：

```text
{'width': 3, 'height': 2, 'channels': 3, 'pixels': 6, 'bytes': 18}
宽=3, 高=2, 像素数=6, 字节数=18
{'width': 4, 'height': 5, 'channels': 1, 'pixels': 20, 'bytes': 20}
```

括号中的两段 f-string 会自动拼接成一个字符串。查看字典可以直接 `print(image)`，不必手动转义双引号来拼出每一个字段。

**本次练习中的问题与补充**

这次提交的函数已经正确计算了像素数和字节数；需要修正的是输出遗漏，以及笔记中不够准确的表述。

1. **中文输出漏了像素数。** 原输出只有宽、高和字节数，按题目要求还应加入 `像素数={image['pixels']}`。
2. **“像素和通道没关系”应改成“像素数量与通道数无关”。** 像素数是 `width * height`；每个像素可以包含多个通道。比如 3 × 2 的 RGB 图片有 6 个像素，每个像素有 R、G、B 三个通道，一共有 18 个通道值。
3. **“字节数等于像素乘以通道”有前提。** 对紧密排列的未压缩像素数据，计算公式是 `像素数 × 通道数 × 每个通道的字节数`。本题按 `uint8` 计算，每个通道占 1 字节；若改为 `float32`，每个通道就占 4 字节。这个结果不等于 PNG、JPEG 或文本 PPM 文件在磁盘上的大小。
4. **容器笔记补全。** 字典如 `{"width": 3}`，用键取值：`image["width"]`；列表如 `[3, 2]`，可以修改元素；元组如 `(3, 2)`，不能重新赋值其中的元素。单元素元组写作 `(3,)`，逗号不可省略；空字典是 `{}`，空集合要写 `set()`。
5. **额外校验的提示要与实际检查一致。** 原代码用 `<= 0` 排除了非正数，但这并没有检查是否为整数，例如 `3.5` 仍会通过。因此报错信息中的“positive integers”比实际检查更严格。本题没有要求参数校验，可以先采用上面的基础版本。
6. **缩进统一为 4 个空格。** 原来的 `main()` 调用缩进了 8 个空格，在当前结构下合法，但统一为 4 个空格更便于阅读。

</details>

### 练习 2：修正越界的通道值

编写函数 `clip_channels(values)`，接收一个整数列表，返回修正后的新列表：小于 0 的数改为 0，大于 255 的数改为 255，其余保持原值。

要求使用循环和条件判断，不能修改传入的列表。

```python
values = [-20, 0, 128, 255, 300]
result = clip_channels(values)
print(result)
print(values)
```

预期输出：

```text
[0, 0, 128, 255, 255]
[-20, 0, 128, 255, 300]
```

再检查两个边界情况：空列表返回 `[]`；`[10, 20, 30]` 返回数值相同的新列表。修改返回列表的第一个元素后，原列表应保持不变。

<details class="exercise-answer">
<summary>点击查看第二题参考答案与本次练习总结</summary>

**参考答案**

保留本次实现中“先复制，再修改副本”的思路：

```python
def clip_channels(values):
    new_values = values.copy()
    for i in range(len(values)):
        if values[i] < 0:
            new_values[i] = 0
        elif values[i] > 255:
            new_values[i] = 255
    return new_values


def main():
    values = [-20, 0, 128, 255, 300]
    result = clip_channels(values)
    print(result)
    print(values)

    result[0] = 100
    print(result)
    print(values)

    print(clip_channels([]))
    normal = [10, 20, 30]
    copied = clip_channels(normal)
    print(copied)
    print(copied is normal)


if __name__ == "__main__":
    main()
```

预期输出：

```text
[0, 0, 128, 255, 255]
[-20, 0, 128, 255, 300]
[100, 0, 128, 255, 255]
[-20, 0, 128, 255, 300]
[]
[10, 20, 30]
False
```

`copied is normal` 判断两个变量是否指向同一个对象；这里是 `False`，说明返回了新列表。比较元素是否相等则使用 `==`。

**本次练习总结**

本次提交没有逻辑错误：越界值正确修正，0 和 255 保持不变，空列表也能处理。代码还主动检查了修改返回列表后，原列表是否保持不变。

- **可以去掉重复初始化。** 原来的 `new_values = []` 紧接着被 `new_values = values.copy()` 覆盖，直接保留后者即可。
- **空列表不需要单独返回。** `values` 为空时，`range(len(values))` 就是 `range(0)`，循环执行零次，最后自然返回复制得到的空列表。
- **每层缩进统一为 4 个空格。** 原来的缩进能运行，但统一风格更易读。
- **复制与赋值要区分。** `new_values = values` 只会让两个变量指向同一个列表，修改其中的元素也会影响原列表；`values.copy()` 会创建一个新列表。与 C++ 的 `std::vector` 拷贝赋值不同，Python 的普通赋值不会自动复制容器。
- **这里用浅拷贝就足够。** `list.copy()` 是浅拷贝，本题元素是不可变整数，代码只替换新列表中的元素，所以原列表不变。如果元素是嵌套列表，浅拷贝仍会共享内层列表，修改内层内容就可能影响原数据。

</details>

### 练习 3：筛选符合尺寸要求的图片

给定以下数据：

```python
images = [
    {"name": "a.ppm", "width": 3, "height": 2},
    {"name": "b.ppm", "width": 2, "height": 2},
    {"name": "c.ppm", "width": 4, "height": 3},
]
```

编写函数 `select_images(images, min_pixels=6)`，返回像素数**大于或等于** `min_pixels` 的图片名称列表，顺序与输入一致。

```python
select_images(images)
# ["a.ppm", "c.ppm"]

select_images(images, min_pixels=12)
# ["c.ppm"]

select_images(images, min_pixels=13)
# []

select_images([], min_pixels=6)
# []
```

这题练习列表遍历、字典取值、默认参数和向列表追加元素。输入数据保持不变。

<details class="exercise-answer">
<summary>点击查看第三题参考答案与本次练习总结</summary>

**参考答案**

沿用本次提交的循环和条件判断，并保留对 `None` 的额外处理：

```python
def select_images(images, min_pixels=6):
    if images is None:
        return []

    new_images = []
    for image in images:
        if image["width"] * image["height"] >= min_pixels:
            new_images.append(image["name"])
    return new_images


def main():
    images = [
        {"name": "a.ppm", "width": 3, "height": 2},
        {"name": "b.ppm", "width": 2, "height": 2},
        {"name": "c.ppm", "width": 4, "height": 3},
    ]

    print(select_images(images))
    print(select_images(images, min_pixels=12))
    print(select_images(images, min_pixels=13))
    print(select_images([], min_pixels=6))


if __name__ == "__main__":
    main()
```

预期输出：

```text
['a.ppm', 'c.ppm']
['c.ppm']
[]
[]
```

**本次练习总结**

本次提交没有逻辑错误，题目中的四组调用结果全部正确，输入列表及其中的字典也保持不变。

- **阈值边界处理正确。** 题目要求“大于或等于”，因此使用 `>=`；像素数恰好为 6 或 12 的图片会在对应阈值下入选。
- **结果顺序正确。** 按输入顺序遍历，符合条件时用 `append()` 追加名称，结果自然保留原顺序。
- **`None` 与空列表不同。** `None` 表示没有值，`[]` 是一个存在但没有元素的列表。`if images is None` 是额外支持，题目并未要求；空列表不会进入这个分支，而是跳过循环，最后返回新建的空列表。
- **这里不需要复制输入。** 函数只读取原字典中的宽、高和名称，将名称加入新列表，没有修改原列表或字典。第二题复制列表是为了修改副本中的元素，本题直接创建结果列表即可。
- **统一书写格式。** 每层缩进使用 4 个空格，参数逗号后加空格：`def select_images(images, min_pixels=6):`。

</details>

### 练习 4：从文件中读出图片信息

用 `pathlib` 和普通文本读取，处理本篇 `code/sample.ppm`。这题先不使用 Pillow 或 NumPy。

这个示例文件的内容没有注释：第一个字段是 `P3`，接着是宽、高和通道最大值，后面每三个整数表示一个 RGB 像素。可以使用字符串的 `split()` 按空白拆分，再用 `int()` 转换数字；不需要实现通用 PPM 解码器。

要求从文件内容算出并打印：

```text
格式: P3
宽: 3
高: 2
通道最大值: 255
像素数: 6
最后一个像素: [255, 128, 0]
```

尺寸、像素数和最后一个像素都必须来自实际文件内容，不能把预期结果直接写进输出。

文件路径应根据脚本位置确定，换一个终端工作目录也能读取。再把路径临时改成一个不存在的文件，捕获 `FileNotFoundError`，输出 `图片文件不存在`，然后恢复原路径。

<details class="exercise-answer">
<summary>点击查看第四题参考答案与本次遇到的问题</summary>

**参考答案**

保留本次尝试中的 `PPMFileInfo` 类结构。将以下代码保存为本篇 `code/practice_04.py`，与 `sample.ppm` 放在同一目录。这个实现只处理题目给定的、没有注释的 P3 示例文件。

```python
from pathlib import Path


class PPMFileInfo:
    def __init__(self, path):
        self.path = path

    def find(self):
        content = self.path.read_text(encoding="ascii")
        parts = content.split()

        self.typeinfo = parts[0]
        self.width = int(parts[1])
        self.height = int(parts[2])
        self.maxval = int(parts[3])

        # 前四项是文件头，剩余项是通道值
        values = []
        for value in parts[4:]:
            values.append(int(value))

        pixel_count = len(values) // 3
        last_pixel = values[-3:]

        print(f"格式: {self.typeinfo}")
        print(f"宽: {self.width}")
        print(f"高: {self.height}")
        print(f"通道最大值: {self.maxval}")
        print(f"像素数: {pixel_count}")
        print(f"最后一个像素: {last_pixel}")


def main():
    path = Path(__file__).resolve().parent / "sample.ppm"
    try:
        info = PPMFileInfo(path)
        info.find()
    except FileNotFoundError:
        print("图片文件不存在")


if __name__ == "__main__":
    main()
```

预期输出：

```text
格式: P3
宽: 3
高: 2
通道最大值: 255
像素数: 6
最后一个像素: [255, 128, 0]
```

如果继续在项目的 `playground/test.py` 中练习，将 `main()` 中的路径赋值替换为下面这段，读取文章中的同一份图片：

```python
project_dir = Path(__file__).resolve().parent.parent
path = (
    project_dir
    / "content"
    / "posts"
    / "AI-深度学习"
    / "从零搭建视觉模型"
    / "02-Python起步"
    / "code"
    / "sample.ppm"
)
```

**本次遇到的问题**

原代码已经正确使用了 `Path(__file__)` 定位脚本、用 `with` 读取文本，并捕获 `FileNotFoundError`。卡住的主要是读取后如何拆分字符串，以及图片的实际路径。

1. **按行拆分后，宽高仍在同一个字符串中。** `content.splitlines()` 得到的开头是 `["P3", "3 2", "255", ...]`。原来注释中的 `int(content.splitlines()[1])` 如果执行，会尝试转换 `"3 2"`，触发 `ValueError`。本题直接用 `content.split()`，可以同时按空格和换行拆分，得到 `["P3", "3", "2", "255", ...]`，再分别转换宽、高。
2. **切片与索引的返回值不同。** `content.splitlines()[:1]` 得到列表 `["P3"]`；`content.splitlines()[0]` 才得到字符串 `"P3"`。同样，答案中的 `parts[0]` 用于取格式字段。
3. **路径写法正确，但必须对应文件位置。** 原来的 `.parent / "sample.ppm"` 指向脚本旁的文件；脚本在 `playground/` 时，就会寻找 `playground/sample.ppm`。文章中的示例图片实际在本篇 `code/` 下，因此需要移动脚本到同一目录，或使用上面的项目相对路径。`__file__` 根据脚本位置定位，不依赖终端当前目录。
4. **剩余字符串需要转换成整数。** `parts[4:]` 跳过四个文件头字段，循环中用 `int(value)` 将 `"255"` 转成 `255`。每三个通道值组成一个 RGB 像素，因此 `len(values) // 3` 得到像素数，`values[-3:]` 取得最后一个像素的三个通道值。`//` 表示向下取整除法，这里用于正整数计数。
5. **文件不存在时可以直接捕获读取异常。** 提前调用 `exists()` 再手动抛异常并非错误，但不是必需的；`read_text()` 或 `open()` 会自动抛出 `FileNotFoundError`。原来的 `with ... open(...)` 写法也正确，答案使用 `read_text()` 只是简化读取步骤。

验证异常处理时，把文件名临时改为 `missing-sample.ppm`，应输出 `图片文件不存在`，随后恢复。理解这题的关键顺序是：读取文本 → 按空白拆分 → 按下标取字段 → 转换数字 → 计算像素信息。

</details>

### 练习 5：写一个能更新尺寸的类

编写 `ImageInfo` 类，只管理尺寸信息，不加载或修改真实图片。

要求提供：

- `__init__(self, width, height, channels=3)`：保存宽、高、通道数。
- `pixel_count(self)`：返回像素数。
- `value_count(self)`：返回所有通道的数值总数。
- `resize(self, width, height)`：更新当前实例的宽、高，通道数保持不变；本题不要求返回值。

用下面这段调用检查：

```python
first = ImageInfo(3, 2)
second = ImageInfo(2, 2, channels=1)

print(first.pixel_count(), first.value_count())
first.resize(5, 4)
print(first.pixel_count(), first.value_count())
print(second.pixel_count(), second.value_count())
```

预期输出：

```text
6 18
20 60
4 4
```

再加一个小要求：初始化或更新尺寸时，宽或高小于等于 0 就抛出 `ValueError`。更新失败时保留原来的尺寸；例如 `first.resize(0, 4)` 被捕获后，`first.pixel_count()` 仍然应为 20。假设尺寸和通道数的输入类型均为整数，通道数为正整数。

<details class="exercise-answer">
<summary>点击查看第五题参考答案与本次练习总结</summary>

**参考答案**

沿用本次实现，并加入非法初始化、更新失败后保留尺寸的演示。按照题目约定，输入类型均为整数；这里的校验只检查数值是否为正。

```python
class ImageInfo:
    def __init__(self, width, height, channels=3):
        if width <= 0 or height <= 0 or channels <= 0:
            raise ValueError("尺寸和通道数必须为正数")
        self.width = width
        self.height = height
        self.channels = channels

    def pixel_count(self):
        return self.width * self.height

    def value_count(self):
        return self.pixel_count() * self.channels

    def resize(self, width, height):
        if width <= 0 or height <= 0:
            raise ValueError("新尺寸必须为正数")
        self.width = width
        self.height = height


def main():
    first = ImageInfo(3, 2)
    second = ImageInfo(2, 2, channels=1)

    print(first.pixel_count(), first.value_count())
    first.resize(5, 4)
    print(first.pixel_count(), first.value_count())
    print(second.pixel_count(), second.value_count())

    try:
        first.resize(0, 4)
    except ValueError as e:
        print(f"更新失败: {e}")
    print(f"更新失败后的像素数: {first.pixel_count()}")

    try:
        ImageInfo(-1, 2)
    except ValueError as e:
        print(f"初始化失败: {e}")


if __name__ == "__main__":
    main()
```

预期输出：

```text
6 18
20 60
4 4
更新失败: 新尺寸必须为正数
更新失败后的像素数: 20
初始化失败: 尺寸和通道数必须为正数
```

**本次练习总结**

基础功能和附加要求均实现正确：像素数与通道值数量计算正确，更新尺寸不改变通道数，两个实例互不影响。初始化或更新时传入非正尺寸会抛出 `ValueError`，失败后原尺寸保留。

- **先校验，再赋值。** 本次代码先检查宽高，全部合法才写入 `self.width` 和 `self.height`，避免“宽已修改，高不合法”的部分更新。`raise` 会立即中断当前方法，后面的赋值不会执行。
- **`self` 指向当前实例。** 可以借助 C++ 的 `this` 来理解：`first` 与 `second` 各自保存自己的属性，所以修改 `first` 不会改变 `second`。
- **复用已有方法。** `value_count()` 调用 `self.pixel_count()` 后再乘以通道数，避免重复写宽乘高的计算。
- **异常分支也要主动运行。** 原来的 `main()` 虽然有 `try/except`，但调用的参数全都合法，并没有触发异常。参考答案分别加入非法初始化和非法更新，并在捕获更新异常后打印像素数，确认仍然是 20。检查状态的语句放在 `except` 之后，才能在异常被捕获后继续执行。
- **参数名称影响关键字调用。** 原来的 `resize(self, new_width, new_height)` 支持 `resize(5, 4)`，但不支持题目接口对应的 `resize(width=5, height=4)`。整理后统一使用 `width, height`。
- **整理格式和导入。** 删除未使用的 `import os`，每层缩进统一为 4 个空格，参数逗号后添加空格。`resize()` 不需要显式返回值，没有 `return` 时默认返回 `None`。

</details>

### 练习 6：取像素、取通道、修改副本

使用 Pillow 读取同目录的 `sample.ppm`，转换为 RGB，再用 NumPy 建立数组 `pixels`。

完成以下操作：

1. 打印数组形状，应为 `(2, 3, 3)`。
2. 取第二行、第三列像素，下标从 0 开始计数，打印结果应为 `[255, 128, 0]`。
3. 提取整张图的 G 通道，结果应为下方矩阵。
4. 创建数组副本，把副本中所有像素的 B 通道设为 0，原数组保持不变。

G 通道预期结果：

```text
[[  0 255   0]
 [255   0 128]]
```

最后打印原数组和副本中第一行、第三列的像素。它原本是蓝色，预期分别为：

```text
原数组: [0, 0, 255]
副本: [0, 0, 0]
```

只修改内存中的数组，不需要保存图片，也不要覆盖 `sample.ppm`。

<details class="exercise-answer">
<summary>点击查看第六题参考答案与本次练习总结</summary>

**参考答案**

保留本次实现，补上原数组与副本的对照输出，以及原数组未改变的检查。将代码保存为本篇 `code/practice_06.py`，与 `sample.ppm` 放在同一目录；在 `playground/test.py` 中运行时，也需要让 `playground/sample.ppm` 存在。

```python
from pathlib import Path

import numpy as np
from PIL import Image


def main():
    path = Path(__file__).resolve().parent / "sample.ppm"
    with Image.open(path) as source:
        image = source.convert("RGB")
    pixels = np.array(image, dtype=np.uint8, copy=True)

    print(pixels.shape)
    print(f"第二行、第三列像素: {pixels[1, 2].tolist()}")
    print("G 通道:")
    print(pixels[:, :, 1])

    original = pixels.copy()
    new_pixels = pixels.copy()
    new_pixels[:, :, 2] = 0

    print(f"原数组: {pixels[0, 2].tolist()}")
    print(f"副本: {new_pixels[0, 2].tolist()}")
    print(f"原数组未改变: {np.array_equal(pixels, original)}")
    print(f"副本 B 通道全部为零: {np.all(new_pixels[:, :, 2] == 0)}")


if __name__ == "__main__":
    main()
```

预期输出：

```text
(2, 3, 3)
第二行、第三列像素: [255, 128, 0]
G 通道:
[[  0 255   0]
 [255   0 128]]
原数组: [0, 0, 255]
副本: [0, 0, 0]
原数组未改变: True
副本 B 通道全部为零: True
```

**本次练习总结**

本次提交的核心操作全部正确：数组形状、像素索引和 G 通道提取符合预期，修改副本的 B 通道也没有影响原数组。原代码打印了整个副本；整理后的答案补上题目要求的蓝色像素对照输出，便于直接观察修改前后的区别。

- **形状按“行、列、通道”理解。** `(2, 3, 3)` 表示 2 行、3 列、每个像素 3 个通道。这里行对应高度，列对应宽度。
- **下标从 0 开始。** 第二行、第三列写作 `pixels[1, 2, :]`，其中 `:` 保留全部通道；也可以简写为 `pixels[1, 2]`，结果相同。
- **通道顺序来自 RGB。** 转换为 RGB 后，下标 0、1、2 分别对应 R、G、B。因此 `pixels[:, :, 1]` 提取所有行列的 G 通道，`new_pixels[:, :, 2] = 0` 将副本全部像素的 B 通道清零。
- **先复制，再修改。** 本次使用 `pixels.copy()` 创建独立的数组数据，做法正确。如果只写 `new_pixels = pixels`，两个变量会指向同一个数组，修改时原数组也会变化。对本题的 `uint8` 数组，复制后修改通道值不会影响原数组。
- **验证整个原数组，而不只看一个像素。** `original` 保存修改前的数据，`np.array_equal(pixels, original)` 比较形状及全部元素是否相等；输出 `True` 表示原数组保持不变。`np.all(...)` 则检查副本的 B 通道是否全部为零。
- **显示格式不影响数值。** NumPy 直接打印像素时通常显示为 `[255 128   0]`，没有逗号；`.tolist()` 转为 Python 列表后显示为 `[255, 128, 0]`。原来的打印方式没有数值错误。
- **统一代码格式。** 每层缩进使用 4 个空格，逗号和赋值符号周围适当留空格，例如 `new_pixels[:, :, 2] = 0`。

</details>
