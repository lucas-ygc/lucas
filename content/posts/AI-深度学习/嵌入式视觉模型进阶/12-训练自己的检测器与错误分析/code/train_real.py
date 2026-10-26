"""显式使用本地数据与模型结构；此入口没有在课程制作时执行真实训练。"""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--output", default="runs")
    args = parser.parse_args()
    if args.epochs < 1:
        parser.error("epochs must be positive")
    if not args.data.is_file() or not args.model.is_file():
        parser.error("local data YAML and model YAML required")
    if args.model.suffix not in [".yaml", ".yml"]:
        parser.error("use local model architecture YAML, not checkpoint weights")
    import yaml

    config = yaml.safe_load(args.data.read_text())
    if not isinstance(config, dict) or any(
        k not in config for k in ["train", "val", "names"]
    ):
        parser.error("data YAML requires train, val, names")
    if "download" in config:
        parser.error("remove download field; prepare dataset locally")
    from ultralytics import YOLO

    model = YOLO(str(args.model))
    model.train(
        data=str(args.data.resolve()),
        epochs=args.epochs,
        imgsz=640,
        batch=4,
        device=args.device,
        seed=7,
        workers=0,
        pretrained=False,
        amp=False,
        project=args.output,
        name="baseline",
    )


if __name__ == "__main__":
    main()
