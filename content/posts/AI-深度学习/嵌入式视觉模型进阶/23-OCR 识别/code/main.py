"""把图像宽度变为时间轴，运行小型 CNN-GRU-CTC 训练步并验证解码顺序。"""

import torch
from torch import nn


def greedy(ids, alphabet):
    result = []
    previous = None
    for index in ids:
        if index != previous and index != 0:
            result.append(alphabet[index])
        previous = index
    return "".join(result)


class CRNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2)
        )
        self.rnn = nn.GRU(8, 12, batch_first=True, bidirectional=True)
        self.head = nn.Linear(24, 4)

    def forward(self, x):
        features = self.cnn(x).mean(2).transpose(1, 2)
        sequence, _ = self.rnn(features)
        return self.head(sequence).log_softmax(-1).transpose(0, 1)


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    net = CRNN()
    output = net(torch.rand(2, 1, 16, 32))
    targets = torch.tensor([1, 2, 1, 1])
    loss = nn.CTCLoss(blank=0)(
        output, targets, torch.tensor([16, 16]), torch.tensor([2, 2])
    )
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    assert torch.isfinite(loss) and all(
        p.grad is not None and torch.isfinite(p.grad).all() for p in net.parameters()
    )
    result = greedy([1, 1, 0, 1, 2, 2], ["", "A", "B", "C"])
    assert result == "AAB"
    print("output TNC", list(output.shape), "loss", loss.item(), "greedy", result)


if __name__ == "__main__":
    main()
