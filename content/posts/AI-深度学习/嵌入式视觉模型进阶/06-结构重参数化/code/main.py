"""推导 Conv-BN 融合，并验证三分支结构与单卷积的数值一致性。"""

import torch
from torch import nn
import torch.nn.functional as F


def fuse(conv, bn):
    scale = bn.weight / torch.sqrt(bn.running_var + bn.eps)
    bias = conv.bias if conv.bias is not None else torch.zeros_like(scale)
    return (
        conv.weight * scale[:, None, None, None],
        bn.bias + (bias - bn.running_mean) * scale,
    )


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    c = 4
    c3 = nn.Conv2d(c, c, 3, padding=1, bias=False)
    b3 = nn.BatchNorm2d(c)
    c1 = nn.Conv2d(c, c, 1, bias=False)
    b1 = nn.BatchNorm2d(c)
    bi = nn.BatchNorm2d(c)
    for _ in range(5):
        x = torch.randn(4, c, 12, 12)
        b3(c3(x))
        b1(c1(x))
        bi(x)
    for b in (b3, b1, bi):
        b.eval()
    identity = nn.Conv2d(c, c, 1, bias=False)
    with torch.no_grad():
        identity.weight.copy_(torch.eye(c).reshape(c, c, 1, 1))
    w3, p3 = fuse(c3, b3)
    w1, p1 = fuse(c1, b1)
    wi, pi = fuse(identity, bi)
    merged = nn.Conv2d(c, c, 3, padding=1)
    with torch.no_grad():
        merged.weight.copy_(w3 + F.pad(w1, (1, 1, 1, 1)) + F.pad(wi, (1, 1, 1, 1)))
        merged.bias.copy_(p3 + p1 + pi)
    for size in [12, 17, 23]:
        x = torch.randn(2, c, size, size)
        expected = torch.relu(b3(c3(x)) + b1(c1(x)) + bi(x))
        actual = torch.relu(merged(x))
        torch.testing.assert_close(actual, expected, rtol=1e-5, atol=2e-6)
        print(size, "max error", float((actual - expected).abs().max().detach()))


if __name__ == "__main__":
    main()
