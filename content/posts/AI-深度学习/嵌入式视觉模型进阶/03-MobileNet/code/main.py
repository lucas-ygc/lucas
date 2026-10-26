"""实现 MobileNetV1 与 V2 的代表模块，理解扩展、深度卷积和线性投影。"""

import torch
from torch import nn


class V1(nn.Sequential):
    def __init__(self, cin, cout):
        super().__init__(
            nn.Conv2d(cin, cin, 3, padding=1, groups=cin, bias=False),
            nn.BatchNorm2d(cin),
            nn.ReLU(),
            nn.Conv2d(cin, cout, 1, bias=False),
            nn.BatchNorm2d(cout),
            nn.ReLU(),
        )


class InvertedResidual(nn.Module):
    def __init__(self, cin, cout, stride=1, expand=6):
        super().__init__()
        hidden = cin * expand
        self.use_skip = stride == 1 and cin == cout
        self.layers = nn.Sequential(
            nn.Conv2d(cin, hidden, 1, bias=False),
            nn.BatchNorm2d(hidden),
            nn.ReLU6(),
            nn.Conv2d(hidden, hidden, 3, stride, 1, groups=hidden, bias=False),
            nn.BatchNorm2d(hidden),
            nn.ReLU6(),
            nn.Conv2d(hidden, cout, 1, bias=False),
            nn.BatchNorm2d(cout),
        )

    def forward(self, x):
        y = self.layers(x)
        return x + y if self.use_skip else y


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    x = torch.randn(2, 16, 24, 24)
    for net, shape in [
        (V1(16, 24), (2, 24, 24, 24)),
        (InvertedResidual(16, 16), (2, 16, 24, 24)),
        (InvertedResidual(16, 24, 2), (2, 24, 12, 12)),
    ]:
        y = net.eval()(x)
        assert tuple(y.shape) == shape
        y.square().mean().backward()
        print(
            type(net).__name__, list(y.shape), sum(p.numel() for p in net.parameters())
        )


if __name__ == "__main__":
    main()
