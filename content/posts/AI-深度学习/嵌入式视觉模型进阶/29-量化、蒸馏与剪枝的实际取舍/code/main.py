"""运行逐通道量化误差、教师学生训练和通道裁剪对照，理解三种方法的不同作用。"""

import copy
import torch
from torch import nn
import torch.nn.functional as F


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    w = torch.randn(4, 8)
    scale = w.abs().amax(1, keepdim=True).clamp_min(1e-8) / 127
    q = torch.round(w / scale).clamp(-127, 127)
    restored = q * scale
    assert bool(((w - restored).abs() <= scale / 2 + 1e-6).all())
    print("per-channel simulated weight max error", float((w - restored).abs().max()))
    x = torch.randn(128, 4)
    y = (x[:, 0] + x[:, 1] > 0).long()
    teacher = nn.Sequential(nn.Linear(4, 16), nn.ReLU(), nn.Linear(16, 2))
    opt = torch.optim.Adam(teacher.parameters(), lr=0.03)
    for _ in range(60):
        opt.zero_grad()
        loss = F.cross_entropy(teacher(x), y)
        loss.backward()
        opt.step()
    teacher.eval()
    with torch.no_grad():
        soft = (teacher(x) / 2).softmax(1)
    student = nn.Sequential(nn.Linear(4, 4), nn.ReLU(), nn.Linear(4, 2))
    baseline = copy.deepcopy(student)
    opt = torch.optim.Adam(student.parameters(), lr=0.03)
    plain = torch.optim.Adam(baseline.parameters(), lr=0.03)
    initial = float(F.cross_entropy(student(x), y).detach())
    for _ in range(80):
        logits = student(x)
        loss = 0.5 * F.cross_entropy(logits, y) + 0.5 * 4 * F.kl_div(
            (logits / 2).log_softmax(1), soft, reduction="batchmean"
        )
        opt.zero_grad()
        loss.backward()
        opt.step()
        plain.zero_grad()
        F.cross_entropy(baseline(x), y).backward()
        plain.step()
    final = float(F.cross_entropy(student(x), y).detach())
    assert final < initial
    test = torch.randn(256, 4)
    truth = (test[:, 0] + test[:, 1] > 0).long()
    with torch.no_grad():
        print(
            "synthetic held-out accuracy teacher/student/hard-only",
            *[
                float((m(test).argmax(1) == truth).float().mean())
                for m in [teacher, student, baseline]
            ]
        )
    first = nn.Linear(4, 6)
    last = nn.Linear(6, 2)
    keep = torch.tensor([0, 2, 5])
    small_first = nn.Linear(4, 3)
    small_last = nn.Linear(3, 2)
    with torch.no_grad():
        small_first.weight.copy_(first.weight[keep])
        small_first.bias.copy_(first.bias[keep])
        small_last.weight.copy_(last.weight[:, keep])
        small_last.bias.copy_(last.bias)
        hidden = torch.relu(first(x))
        mask = torch.zeros(6)
        mask[keep] = 1
        reference = last(hidden * mask)
        actual = small_last(torch.relu(small_first(x)))
        torch.testing.assert_close(actual, reference, atol=1e-6, rtol=1e-5)
    print(
        "distillation train CE",
        initial,
        final,
        "channel-pruning index equivalence passed",
    )


if __name__ == "__main__":
    main()
