"""搭建细节与上下文双分支，理解空洞卷积、掩码插值和实例身份。"""

import cv2, numpy as np
import torch
from torch import nn
import torch.nn.functional as F


class Segmenter(nn.Module):
    def __init__(self):
        super().__init__()
        self.detail = nn.Sequential(nn.Conv2d(3, 8, 3, 2, 1), nn.ReLU())
        self.context = nn.Sequential(
            nn.Conv2d(3, 8, 3, 4, 1),
            nn.ReLU(),
            nn.Conv2d(8, 8, 3, padding=2, dilation=2),
            nn.ReLU(),
        )
        self.head = nn.Conv2d(16, 2, 1)

    def forward(self, x):
        detail = self.detail(x)
        context = F.interpolate(
            self.context(x),
            size=detail.shape[-2:],
            mode="bilinear",
            align_corners=False,
        )
        return F.interpolate(
            self.head(torch.cat([detail, context], 1)),
            size=x.shape[-2:],
            mode="bilinear",
            align_corners=False,
        )


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    mask = torch.zeros(1, 31, 29, dtype=torch.long)
    mask[:, 5:15, 4:12] = 1
    mask[:, 20:25, 18:24] = 1
    image = mask[:, None].repeat(1, 3, 1, 1).float() + torch.rand(1, 3, 31, 29) * 0.1
    net = Segmenter()
    opt = torch.optim.Adam(net.parameters(), lr=0.001)
    logits = net(image)
    assert logits.shape == (1, 2, 31, 29)
    loss = F.cross_entropy(logits, mask)
    opt.zero_grad()
    loss.backward()
    opt.step()
    pred = logits.argmax(1)
    for c in [0, 1]:
        inter = ((pred == c) & (mask == c)).sum().item()
        union = ((pred == c) | (mask == c)).sum().item()
        print("class", c, "IoU", inter / union if union else None)
    count, _ = cv2.connectedComponents(mask[0].numpy().astype(np.uint8))
    assert count - 1 == 2
    print("constructed disconnected instances", count - 1, "loss", loss.item())


if __name__ == "__main__":
    main()
