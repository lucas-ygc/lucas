"""读取图片，逐层观察一个未训练的小型 CNN。仅使用 CPU。"""

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
    chw = torch.from_numpy(pixels).permute(2, 0, 1).contiguous()
    return (chw.to(dtype=torch.float32) / 255.0).unsqueeze(0)


class TinyCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 8, kernel_size=3, stride=1, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.flatten = nn.Flatten(start_dim=1)
        self.classifier = nn.Linear(8 * 16 * 16, 2)

    def forward(self, images, trace=False):
        features = images
        if trace:
            print(f"输入: {tuple(features.shape)}")
        for name, layer in (
            ("卷积", self.conv),
            ("ReLU", self.relu),
            ("池化", self.pool),
            ("展平", self.flatten),
            ("输出分数", self.classifier),
        ):
            features = layer(features)
            if trace:
                print(f"{name}: {tuple(features.shape)}")
        return features


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
    model = TinyCNN()
    model.eval()
    with torch.no_grad():
        scores = model(images, trace=True)
    print(f"输出类型: {scores.dtype}, 设备: {scores.device}")
    print(f"类别分数: {scores[0].tolist()}")
    print(f"参数总数: {sum(parameter.numel() for parameter in model.parameters())}")
    print("网络尚未训练；两个分数没有可靠的分类意义。")


if __name__ == "__main__":
    main()
