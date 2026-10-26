"""通过通道编号追踪 shuffle 的作用，观察分组之间的信息交换与复制成本。"""

import torch
from torch import nn


def shuffle(x, groups):
    n, c, h, w = x.shape
    if c % groups:
        raise ValueError("channels must be divisible by groups")
    return (
        x.reshape(n, groups, c // groups, h, w)
        .transpose(1, 2)
        .contiguous()
        .reshape(n, c, h, w)
    )


class SplitBlock(nn.Module):
    def __init__(self, c):
        super().__init__()
        if c % 2:
            raise ValueError("even channels required")
        half = c // 2
        self.branch = nn.Sequential(
            nn.Conv2d(half, half, 1),
            nn.ReLU(),
            nn.Conv2d(half, half, 3, padding=1, groups=half),
            nn.Conv2d(half, half, 1),
            nn.ReLU(),
        )

    def forward(self, x):
        a, b = x.chunk(2, dim=1)
        return shuffle(torch.cat([a, self.branch(b)], 1), 2)


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    ids = torch.arange(8).reshape(1, 8, 1, 1)
    assert shuffle(ids, 2).flatten().tolist() == [0, 4, 1, 5, 2, 6, 3, 7]
    print(
        "groups2:",
        shuffle(ids, 2).flatten().tolist(),
        "groups4:",
        shuffle(ids, 4).flatten().tolist(),
    )
    x = torch.randn(1, 8, 16, 16)
    y = SplitBlock(8)(x)
    assert y.shape == x.shape
    print("output", list(y.shape))


if __name__ == "__main__":
    main()
