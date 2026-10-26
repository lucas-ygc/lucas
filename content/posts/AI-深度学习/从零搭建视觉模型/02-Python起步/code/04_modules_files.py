"""导入自己的模块、定位文件、读取文本和 with 语句。"""

from pathlib import Path

from pixel_math import pixel_count


# __file__ 指当前脚本文件。路径相对于脚本定位，与终端所在目录无关。
lesson_dir = Path(__file__).resolve().parent
sample = lesson_dir / "sample.ppm"

# with 退出时会关闭文件；这里只读，不改写图片。
with sample.open("r", encoding="ascii") as file:
    text = file.read()

print("读取文件:", sample.name)
print("文件中的文本:")
print(text.strip())
print("3×2 图片的像素数:", pixel_count(3, 2))
