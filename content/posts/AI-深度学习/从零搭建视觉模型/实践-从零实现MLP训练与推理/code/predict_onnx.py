"""ONNX 独立推理：只依赖 NumPy、Pillow、ONNX Runtime，不导入 PyTorch。"""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
import onnxruntime as ort

DEFAULT_OUTPUT = Path(__file__).resolve().parent / "outputs"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, nargs="?", default=DEFAULT_OUTPUT / "vertical.png")
    parser.add_argument("--model", type=Path, default=DEFAULT_OUTPUT / "model.onnx")
    args = parser.parse_args()
    try:
        if not args.model.is_file():
            raise FileNotFoundError(f"找不到模型：{args.model}，请先运行 export_onnx.py")
        options = ort.SessionOptions()
        options.intra_op_num_threads = 1
        session = ort.InferenceSession(str(args.model), sess_options=options,
                                       providers=["CPUExecutionProvider"])
        metadata = session.get_modelmeta().custom_metadata_map
        classes = json.loads(metadata["classes"])
        preprocess = json.loads(metadata["preprocess"])
        if preprocess != {"mode": "L", "size": 16, "scale": 255, "layout": "NCHW"}:
            raise ValueError("预处理约定不匹配")
        if classes != ["横条纹", "竖条纹"]:
            raise ValueError("类别映射不匹配")
        input_info = session.get_inputs()[0]
        if input_info.name != "images" or input_info.shape != [1, 1, 16, 16] or input_info.type != "tensor(float)":
            raise ValueError("模型输入接口不匹配")
        with Image.open(args.image) as source:
            image = source.convert("L")
            if image.size != (16, 16):
                raise ValueError("本实验只接受 16×16 图片")
            images = np.asarray(image, dtype=np.float32).reshape(1, 1, 16, 16) / np.float32(255)
        logits = session.run(["logits"], {"images": images})[0]
        if logits.shape != (1, 2) or not np.isfinite(logits).all():
            raise ValueError("输出形状或数值异常")
        exp_scores = np.exp(logits[0] - logits[0].max())
        probabilities = exp_scores / exp_scores.sum()
        index = int(logits[0].argmax())
        print(json.dumps({"class_id": index, "class_name": classes[index],
                          "score": float(probabilities[index]),
                          "logits": logits[0].tolist()}, ensure_ascii=False))
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        parser.exit(2, f"ONNX 推理失败：{error}\n请检查模型、元数据与图片。\n")


if __name__ == "__main__":
    main()
