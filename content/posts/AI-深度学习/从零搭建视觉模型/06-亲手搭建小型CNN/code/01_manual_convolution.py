"""用手写循环验证单通道卷积，全部在 CPU 上运行。"""

import torch
from torch import nn


def main():
    image = torch.tensor([
        [1, 2, 0, 1],
        [0, 1, 3, 2],
        [2, 1, 0, 1],
        [1, 0, 2, 3],
    ], dtype=torch.float32)
    kernel = torch.tensor([[1, 0], [0, -1]], dtype=torch.float32)
    manual = torch.empty((3, 3), dtype=torch.float32)
    for row in range(3):
        for column in range(3):
            patch = image[row:row + 2, column:column + 2]
            manual[row, column] = (patch * kernel).sum()

    conv = nn.Conv2d(1, 1, kernel_size=2, stride=1, padding=0, bias=False)
    with torch.no_grad():
        conv.weight.copy_(kernel.unsqueeze(0).unsqueeze(0))
        output = conv(image.unsqueeze(0).unsqueeze(0))
    print(f"输入 NCHW: {(1, 1, 4, 4)}")
    print(f"手算结果: {manual.tolist()}")
    print(f"Conv2d 输出: {tuple(output.shape)}")
    print(f"两种计算相同: {torch.allclose(manual, output[0, 0])}")
    print(f"ReLU 后: {nn.ReLU()(output)[0, 0].tolist()}")
    assert torch.allclose(manual, output[0, 0])


if __name__ == "__main__":
    main()
