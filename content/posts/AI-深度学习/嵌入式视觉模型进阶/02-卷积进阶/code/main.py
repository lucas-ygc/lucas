"""通过真实算子运行区分连接关系、感受野和理论计算量。"""

import statistics, time
import torch
from torch import nn


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    ops = {
        "regular": nn.Conv2d(16, 32, 3, padding=1, bias=False),
        "groups4": nn.Conv2d(16, 32, 3, padding=1, groups=4, bias=False),
        "depthwise": nn.Conv2d(16, 16, 3, padding=1, groups=16, bias=False),
        "separable": nn.Sequential(
            nn.Conv2d(16, 16, 3, padding=1, groups=16, bias=False),
            nn.Conv2d(16, 32, 1, bias=False),
        ),
        "dilation2": nn.Conv2d(16, 32, 3, padding=2, dilation=2, bias=False),
    }
    x = torch.rand(1, 16, 32, 32)
    with torch.inference_mode():
        for name, op in ops.items():
            op.eval()
            for _ in range(5):
                op(x)
            elapsed = []
            for _ in range(30):
                start = time.perf_counter_ns()
                y = op(x)
                elapsed.append((time.perf_counter_ns() - start) / 1e6)
            assert y.shape[-2:] == (32, 32)
            print(
                name,
                "parameters",
                sum(p.numel() for p in op.parameters()),
                "shape",
                list(y.shape),
                "CPU median ms",
                round(statistics.median(elapsed), 4),
            )
    assert sum(p.numel() for p in ops["regular"].parameters()) == 4608


if __name__ == "__main__":
    main()
