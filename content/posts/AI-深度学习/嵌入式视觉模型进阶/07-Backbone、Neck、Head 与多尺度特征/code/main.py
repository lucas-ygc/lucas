"""从不同步长的特征图理解检测网络的分工与小目标信息。"""

import torch
from torch import nn


class Backbone(nn.Module):
    def __init__(self):
        super().__init__()
        channels = [3, 8, 16, 32, 64, 128]
        self.stages = nn.ModuleList(
            [
                nn.Sequential(nn.Conv2d(a, b, 3, 2, 1), nn.ReLU())
                for a, b in zip(channels, channels[1:])
            ]
        )

    def forward(self, x):
        result = []
        for i, stage in enumerate(self.stages):
            x = stage(x)
            if i >= 2:
                result.append(x)
        return result


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    net = Backbone()
    for size in [128, 130]:
        net.zero_grad()
        features = net(torch.randn(1, 3, size, size))
        sum(y.square().mean() for y in features).backward()
        assert all(p.grad is not None for p in net.parameters())
        print("input", size, [(list(y.shape), y.numel()) for y in features])
    assert [y.shape[-1] for y in features] == [17, 9, 5]


if __name__ == "__main__":
    main()
