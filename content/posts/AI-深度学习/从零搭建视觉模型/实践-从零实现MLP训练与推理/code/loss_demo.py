"""用稳定公式计算交叉熵，并核对自动求导的 logits 梯度。"""
import torch
from torch.nn import functional as F


def main():
    logits = torch.tensor([[2., 1.], [0., 2.]], requires_grad=True)
    labels = torch.tensor([1, 1])
    # -log softmax(z)[y] = logsumexp(z) - z[y]，避免先求极小概率再取 log。
    print(f"{torch.arange(2)}")
    per_sample = torch.logsumexp(logits, dim=1) - logits[torch.arange(2), labels]
    manual_loss = per_sample.mean()
    loss = F.cross_entropy(logits, labels)
    torch.testing.assert_close(manual_loss, loss)
    loss.backward()
    expected_gradient = (logits.detach().softmax(1) - F.one_hot(labels, 2)) / 2
    torch.testing.assert_close(logits.grad, expected_gradient)
    print("逐样本损失:", [round(x, 6) for x in per_sample.tolist()])
    print(f"平均损失: {loss.item():.6f}")
    print("logits 梯度:", logits.grad.tolist())
    print("显式公式、框架交叉熵与梯度对照通过。")


if __name__ == "__main__":
    main()
