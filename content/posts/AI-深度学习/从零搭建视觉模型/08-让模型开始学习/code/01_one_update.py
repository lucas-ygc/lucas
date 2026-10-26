"""一个参数、一次梯度更新。只用 CPU。"""
import torch


def main():
    x = torch.tensor(2.0)
    target = torch.tensor(4.0)
    weight = torch.tensor(0.0, requires_grad=True)
    learning_rate = 0.1

    prediction = weight * x
    loss = (prediction - target) ** 2
    loss.backward()
    print(f"更新前权重: {weight.item():.4f}")
    print(f"更新前预测: {prediction.item():.4f}")
    print(f"更新前损失: {loss.item():.4f}")
    print(f"权重梯度: {weight.grad.item():.4f}")

    # 更新不属于此次求导过程，因此放在 no_grad 中。
    with torch.no_grad():
        weight -= learning_rate * weight.grad
        new_prediction = weight * x
        new_loss = (new_prediction - target) ** 2
    print(f"更新后权重: {weight.item():.4f}")
    print(f"更新后预测: {new_prediction.item():.4f}")
    print(f"更新后损失: {new_loss.item():.4f}")
    assert abs(weight.item() - 1.6) < 1e-6
    assert new_loss.item() < loss.item()


if __name__ == "__main__":
    main()
