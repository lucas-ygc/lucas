"""导出已训练模型，并对 132 个输入逐个检查 PyTorch/ONNX 一致性。"""
import argparse
import json
from pathlib import Path
import numpy as np
import onnx
import onnxruntime as ort
import torch
from dataset import make_dataset
from train import DEFAULT_OUTPUT, load_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_OUTPUT / "best.pt")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT / "model.onnx")
    args = parser.parse_args()
    torch.set_num_threads(1)
    model, data = load_model(args.checkpoint)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    example = torch.zeros(1, 1, 16, 16)
    # 显式选择传统导出路径，与本系列第 22 章保持一致；固定单图输入。
    torch.onnx.export(model, (example,), str(args.out), input_names=["images"],
                      output_names=["logits"], opset_version=17, dynamo=False)
    graph = onnx.load(str(args.out))
    onnx.helper.set_model_props(graph, {
        "classes": json.dumps(data["classes"], ensure_ascii=False),
        "preprocess": json.dumps(data["preprocess"]),
    })
    onnx.checker.check_model(graph)
    onnx.save(graph, str(args.out))
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    session = ort.InferenceSession(str(args.out), sess_options=options,
                                   providers=["CPUExecutionProvider"])
    samples = make_dataset(128, 500).tensors[0]
    generator = torch.Generator().manual_seed(600)
    special = torch.cat([torch.zeros_like(example), torch.ones_like(example),
                         torch.full_like(example, 0.5), torch.rand(example.shape, generator=generator)])
    inputs = torch.cat([samples, special])
    max_error = 0.0
    same_class = 0
    for image in inputs:
        batch = image.unsqueeze(0)
        with torch.no_grad():
            expected = model(batch).numpy()
        actual = session.run(["logits"], {"images": batch.numpy()})[0]
        assert actual.shape == expected.shape == (1, 2)
        np.testing.assert_allclose(actual, expected, rtol=1e-4, atol=1e-5)
        max_error = max(max_error, float(np.max(np.abs(actual - expected))))
        same_class += int(actual.argmax(1)[0] == expected.argmax(1)[0])
    assert same_class == len(inputs)
    print(f"ONNX 校验通过；输入=images [1,1,16,16] float32，输出=logits [1,2]")
    print(f"数值对照 {len(inputs)} 个输入，max_abs_error={max_error:.8g}，类别一致={same_class}/{len(inputs)}")
    print(f"导出至 {args.out.resolve()}；验证范围为 ONNX Runtime CPU。")


if __name__ == "__main__":
    main()
