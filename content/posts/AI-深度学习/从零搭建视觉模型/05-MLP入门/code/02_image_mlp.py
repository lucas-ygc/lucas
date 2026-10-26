"""让图片经过未训练的 MLP，观察展平和逐层计算。仅使用 CPU。"""

import argparse
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageOps
from torch import nn


def image_to_batch(path):
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
    image = image.resize((32, 32), Image.Resampling.BILINEAR)
    pixels = np.array(image, dtype=np.uint8, copy=True)
    # 每一步单独命名，便于与上一章的转换过程对照。
    hwc = torch.from_numpy(pixels)
    chw = hwc.permute(2, 0, 1).contiguous()
    chw_float = chw.to(dtype=torch.float32)
    scaled_chw = chw_float / 255.0
    batch = scaled_chw.unsqueeze(0)
    return batch


class ImageMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten(start_dim=1)
        self.hidden = nn.Linear(3 * 32 * 32, 16)
        self.relu = nn.ReLU()
        self.output = nn.Linear(16, 2)

    def forward(self, images, trace=False):
        if trace:
            print(f"输入: {tuple(images.shape)}")
        features = self.flatten(images)
        if trace:
            print(f"展平: {tuple(features.shape)}")
        features = self.hidden(features)
        if trace:
            print(f"隐藏层: {tuple(features.shape)}")
        features = self.relu(features)
        if trace:
            print(f"ReLU: {tuple(features.shape)}")
        scores = self.output(features)
        if trace:
            print(f"输出分数: {tuple(scores.shape)}")
        return scores


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path,
                        default=Path(__file__).with_name("sample.ppm"))
    args = parser.parse_args()
    try:
        images = image_to_batch(args.image)
    except (OSError, ValueError) as error:
        parser.error(f"无法读取图片 {args.image}: {error}")

    torch.manual_seed(7)
    model = ImageMLP()
    model.eval()
    with torch.no_grad():
        scores = model(images, trace=True)
    print(f"输出类型: {scores.dtype}, 设备: {scores.device}")
    print(f"类别分数: {scores[0].tolist()}")
    # parameters() 依次给出权重、偏置等参数张量。
    # numel() 返回一个张量中有多少个数。
    parameter_count = 0
    for parameter in model.parameters():
        parameter_count = parameter_count + parameter.numel()
    print(f"参数总数: {parameter_count}")
    print("网络尚未训练；分数大小不代表已经具备识别能力。")


if __name__ == "__main__":
    main()
