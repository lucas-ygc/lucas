"""完成一个明确的中心分配与分类框回归训练步，理解正样本和损失掩码。"""

import torch
from torch import nn
import torch.nn.functional as F


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    net = nn.Sequential(
        nn.Conv2d(3, 16, 3, padding=1),
        nn.ReLU(),
        nn.AdaptiveAvgPool2d(4),
        nn.Conv2d(16, 7, 1),
    )
    x = torch.rand(1, 3, 32, 32)
    box = torch.tensor([[0.2, 0.3, 0.6, 0.8]])
    label = torch.tensor([1])
    center = (box[0, :2] + box[0, 2:]) / 2
    gx, gy = (center * 4).long().tolist()
    logits = net(x)
    target = torch.zeros_like(logits[:, 0])
    target[0, gy, gx] = 1
    loss_obj = F.binary_cross_entropy_with_logits(
        logits[:, 0], target, pos_weight=torch.tensor(15.0)
    )
    loss_cls = F.cross_entropy(logits[:, 1:3, gy, gx], label)
    loss_box = F.smooth_l1_loss(logits[:, 3:7, gy, gx].sigmoid(), box)
    loss = loss_obj + loss_cls + 5 * loss_box
    opt = torch.optim.SGD(net.parameters(), lr=0.01)
    opt.zero_grad()
    loss.backward()
    assert all(
        p.grad is not None and torch.isfinite(p.grad).all() for p in net.parameters()
    )
    opt.step()
    print(
        "positive (x,y):",
        gx,
        gy,
        "object/class/box:",
        *[round(v.item(), 5) for v in [loss_obj, loss_cls, loss_box]]
    )


if __name__ == "__main__":
    main()
