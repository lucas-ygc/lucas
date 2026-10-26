"""衔接下一课：读取图片，查看 NumPy 数组；需要 Pillow 和 NumPy。"""

from pathlib import Path

import numpy as np
from PIL import Image

sample = Path(__file__).with_name("sample.ppm")
with Image.open(sample) as source:
    image = source.convert("RGB")

pixels = np.array(image, dtype=np.uint8, copy=True)
print("Pillow size(W,H):", image.size)
print("NumPy shape(H,W,C):", pixels.shape)
print("数据类型:", pixels.dtype)
print("左上角 RGB:", pixels[0, 0].tolist())
print("第一行的 RGB:", pixels[0].tolist())
print("R 通道:\n", pixels[:, :, 0])
print("缩放到 [0,1] 后的左上角:", (pixels[0, 0] / 255.0).tolist())
