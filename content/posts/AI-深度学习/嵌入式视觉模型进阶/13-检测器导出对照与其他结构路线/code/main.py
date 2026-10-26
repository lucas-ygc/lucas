"""导出多输出检测头并逐张量对照，认识 SSD、DETR 与后处理边界。"""

from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import torch
from torch import nn
import onnx, onnxruntime as ort


class Head(nn.Module):
    def __init__(self):
        super().__init__()
        self.feature = nn.Conv2d(3, 8, 3, 4, 1)
        self.cls = nn.Conv2d(8, 2, 1)
        self.box = nn.Conv2d(8, 4, 1)

    def forward(self, x):
        x = torch.relu(self.feature(x))
        return self.cls(x), self.box(x)


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    net = Head().eval()
    with TemporaryDirectory() as d:
        path = Path(d) / "head.onnx"
        x = torch.rand(1, 3, 32, 32)
        torch.onnx.export(
            net,
            (x,),
            str(path),
            input_names=["images"],
            output_names=["classes", "boxes"],
            opset_version=17,
            dynamo=False,
        )
        onnx.checker.check_model(onnx.load(path))
        session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
        for seed in [7, 8, 9]:
            torch.manual_seed(seed)
            x = torch.rand(1, 3, 32, 32)
            with torch.inference_mode():
                expected = net(x)
            actual = session.run(None, {"images": x.numpy()})
            for name, a, b in zip(["classes", "boxes"], actual, expected):
                np.testing.assert_allclose(a, b.numpy(), rtol=1e-4, atol=1e-5)
                print(
                    seed, name, a.shape, "max error", float(np.abs(a - b.numpy()).max())
                )


if __name__ == "__main__":
    main()
