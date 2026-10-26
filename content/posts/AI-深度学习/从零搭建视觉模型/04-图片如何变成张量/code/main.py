"""读取图片，逐步观察 HWC → CHW → NCHW。仅使用 CPU。"""

import argparse
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageOps


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("尺寸必须是正整数")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "image", nargs="?", type=Path,
        default=Path(__file__).with_name("sample.ppm"),
        help="图片路径；默认使用同目录的 3×2 像素示例",
    )
    parser.add_argument(
        "--resize", nargs=2, type=positive_int, metavar=("WIDTH", "HEIGHT"),
        help="可选：缩放到指定宽、高，便于观察形状变化",
    )
    args = parser.parse_args()

    try:
        with Image.open(args.image) as source:
            print(f"原始图片: mode={source.mode}, size(W,H)={source.size}")
            image = ImageOps.exif_transpose(source).convert("RGB")
    except (OSError, ValueError) as error:
        parser.error(f"无法读取图片 {args.image}: {error}")

    if args.resize:
        image = image.resize(tuple(args.resize), Image.Resampling.BILINEAR)
    print(f"处理后图片: mode={image.mode}, size(W,H)={image.size}")

    # 每个像素存放 R、G、B 三个数，数组依次按行、列、通道索引。
    pixels = np.array(image, dtype=np.uint8, copy=True)
    print(f"NumPy HWC: shape={pixels.shape}, dtype={pixels.dtype}")
    print(f"左上角 RGB: {pixels[0, 0].tolist()}")

    # from_numpy 保留数组形状和类型，并与数组共享内存。
    hwc = torch.from_numpy(pixels)
    print(f"Tensor HWC: shape={tuple(hwc.shape)}, dtype={hwc.dtype}")

    # 交换维度的顺序，不交换 R、G、B 的含义。
    chw = hwc.permute(2, 0, 1).contiguous()
    print(f"Tensor CHW: shape={tuple(chw.shape)}, dtype={chw.dtype}")
    print(f"CHW 左上角 RGB: {chw[:, 0, 0].tolist()}")

    # 将 8 位像素转换为浮点数，并缩放到 [0, 1]。
    scaled = chw.to(dtype=torch.float32) / 255.0
    print(
        f"float CHW: shape={tuple(scaled.shape)}, dtype={scaled.dtype}, "
        f"range=[{scaled.min().item():.4f}, {scaled.max().item():.4f}]"
    )

    # 在最前面增加一维，表示这一批只有一张图片。
    batch = scaled.unsqueeze(0)
    print(
        f"模型输入 NCHW: shape={tuple(batch.shape)}, "
        f"dtype={batch.dtype}, device={batch.device}"
    )
    print(f"输入左上角 RGB: {batch[0, :, 0, 0].tolist()}")

    # 对小图打印所有数值，便于手工核对通道与坐标。
    if image.width * image.height <= 12:
        print("缩放前的 R 通道:")
        print(chw[0].numpy())
        print("缩放前的 G 通道:")
        print(chw[1].numpy())
        print("缩放前的 B 通道:")
        print(chw[2].numpy())


if __name__ == "__main__":
    main()
