"""搭建自顶向下与自底向上的融合路径，检查相加、拼接和空间对齐。"""

import torch
from torch import nn
import torch.nn.functional as F


class Pyramid(nn.Module):
    def __init__(self):
        super().__init__()
        self.lateral = nn.ModuleList([nn.Conv2d(c, 24, 1) for c in [32, 64, 128]])
        self.down = nn.ModuleList([nn.Conv2d(24, 24, 3, 2, 1) for _ in range(2)])

    def forward(self, features):
        p = [layer(x) for layer, x in zip(self.lateral, features)]
        for i in [1, 0]:
            p[i] = p[i] + F.interpolate(p[i + 1], size=p[i].shape[-2:], mode="nearest")
        out = [p[0]]
        for i in [0, 1]:
            down = self.down[i](out[-1])
            assert down.shape == p[i + 1].shape
            out.append(p[i + 1] + down)
        return out


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    xs = [
        torch.randn(1, c, s, s, requires_grad=True)
        for c, s in [(32, 17), (64, 9), (128, 5)]
    ]
    ys = Pyramid()(xs)
    sum(y.square().mean() for y in ys).backward()
    assert all(x.grad is not None and torch.isfinite(x.grad).all() for x in xs)
    print("outputs", [list(y.shape) for y in ys])


if __name__ == "__main__":
    main()
