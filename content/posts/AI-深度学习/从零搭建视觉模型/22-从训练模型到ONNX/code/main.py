"""导出 ONNX 并对照数值。运行方式与练习见 README.md。"""
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import torch
from torch import nn
import onnx
import onnxruntime as ort

torch.manual_seed(7)
torch.set_num_threads(2)
model = nn.Sequential(
    nn.Conv2d(3, 4, 3, padding=1), nn.ReLU(),
    nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(4, 2),
).eval()
x = torch.rand(1, 3, 32, 32)
with torch.no_grad():
    expected = model(x).numpy()

with TemporaryDirectory() as directory:
    path = Path(directory) / 'tiny.onnx'
    torch.onnx.export(model, (x,), str(path),
                      input_names=['images'], output_names=['logits'],
                      opset_version=17, dynamo=False)
    onnx.checker.check_model(onnx.load(str(path)))
    session = ort.InferenceSession(str(path), providers=['CPUExecutionProvider'])
    actual = session.run(['logits'], {'images': x.numpy()})[0]
    np.testing.assert_allclose(actual, expected, rtol=1e-4, atol=1e-5)
    print('max_abs_error:', float(np.max(np.abs(actual - expected))))
