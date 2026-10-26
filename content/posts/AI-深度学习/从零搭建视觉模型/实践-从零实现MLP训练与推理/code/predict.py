"""独立进程加载已训练权重，处理单张图片并输出 JSON。"""
import argparse
import json
from pathlib import Path
import torch
from dataset import load_image
from train import DEFAULT_OUTPUT, load_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, nargs="?", default=DEFAULT_OUTPUT / "horizontal.png")
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_OUTPUT / "best.pt")
    args = parser.parse_args()
    torch.set_num_threads(1)
    try:
        model, data = load_model(args.checkpoint)
        images = load_image(args.image)
        with torch.no_grad():
            logits = model(images)
            probabilities = logits.softmax(1)
        index = logits.argmax(1).item()
        print(json.dumps({"class_id": index, "class_name": data["classes"][index],
                          "score": probabilities[0, index].item(),
                          "logits": logits[0].tolist()}, ensure_ascii=False))
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        parser.exit(2, f"推理失败：{error}\n请先运行 train.py，并检查图片和检查点路径。\n")


if __name__ == "__main__":
    main()
