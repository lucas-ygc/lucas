"""检查 ONNX 静态形状、算子和数值替换，建立真实编译报告的阅读方法。"""

from pathlib import Path
from tempfile import TemporaryDirectory
from collections import Counter
import torch
from torch import nn
import onnx


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 4, 3, padding=1)

    def forward(self, x):
        x = self.conv(x)
        return x * torch.clamp(x + 3, 0, 6) / 6


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    net = Net().eval()
    x = torch.rand(1, 3, 16, 16)
    z = net.conv(x)
    torch.testing.assert_close(net(x), nn.functional.hardswish(z))
    with TemporaryDirectory() as directory:
        path = Path(directory) / "graph.onnx"
        torch.onnx.export(
            net, (x,), str(path), opset_version=17, dynamo=False, input_names=["images"]
        )
        graph = onnx.shape_inference.infer_shapes(onnx.load(path))
        onnx.checker.check_model(graph)
        ops = Counter(node.op_type for node in graph.graph.node)
        example_allow = {"Conv", "Add", "Mul", "Constant", "Div"}
        print("ops", dict(ops))
        print("review against DEMO allowlist:", sorted(set(ops) - example_allow))
        dims = graph.graph.input[0].type.tensor_type.shape.dim
        assert all(d.HasField("dim_value") and d.dim_value > 0 for d in dims)
        print(
            "static input",
            [d.dim_value for d in dims],
            "not a device compatibility result",
        )


if __name__ == "__main__":
    main()
