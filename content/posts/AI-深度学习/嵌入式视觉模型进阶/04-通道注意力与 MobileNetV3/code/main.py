"""实现 SE 和 Hard-Swish，检查注意力广播以及激活的分段行为。"""

import torch
from torch import nn


class SE(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.gate = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(c, max(1, c // 4), 1),
            nn.ReLU(),
            nn.Conv2d(max(1, c // 4), c, 1),
            nn.Hardsigmoid(),
        )

    def forward(self, x):
        return x * self.gate(x)


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    x = torch.linspace(-6, 6, 25)
    manual = x * torch.clamp(x + 3, 0, 6) / 6
    torch.testing.assert_close(manual, nn.functional.hardswish(x))
    net = SE(16)
    features = torch.randn(2, 16, 8, 8)
    g = net.gate(features)
    assert g.shape == (2, 16, 1, 1) and bool(((g >= 0) & (g <= 1)).all())
    y = net(features)
    assert y.shape == features.shape
    print("gate shape", list(g.shape), "range", g.min().item(), g.max().item())
    print("h-swish equality passed; output", list(y.shape))


if __name__ == "__main__":
    main()
