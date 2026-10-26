"""用固定参数手算 2 → 3 → 2 网络，并与 PyTorch 对照。"""

import torch
from torch import nn


def linear_by_hand(inputs, weights, biases):
    # 保存这一层所有输出单元的计算结果。
    outputs = []

    # 外层循环：依次计算每个输出单元。
    for output_index in range(len(weights)):
        total = 0.0

        # 内层循环：把所有输入与各自的权重相乘，再累加。
        for input_index in range(len(inputs)):
            input_value = inputs[input_index]
            weight = weights[output_index][input_index]
            total = total + input_value * weight

        # 一个输出单元的乘加完成后，加上它自己的偏置。
        total = total + biases[output_index]
        outputs.append(total)

    return outputs


def main():
    inputs = [2.0, -1.0]
    hidden_weights = [[1.0, 2.0], [-1.0, 1.0], [0.5, -1.0]]
    hidden_biases = [1.0, 0.0, -1.0]
    output_weights = [[1.0, -1.0, 2.0], [-2.0, 1.0, 1.0]]
    output_biases = [0.0, 0.5]

    hidden_raw = linear_by_hand(inputs, hidden_weights, hidden_biases)
    # 手写 ReLU：逐个处理，负数变成 0，其他值保持原样。
    hidden_active = []
    for value in hidden_raw:
        if value < 0.0:
            hidden_active.append(0.0)
        else:
            hidden_active.append(value)
    manual_scores = linear_by_hand(hidden_active, output_weights, output_biases)

    hidden_layer = nn.Linear(2, 3)
    output_layer = nn.Linear(3, 2)
    relu = nn.ReLU()
    with torch.no_grad():
        hidden_layer.weight.copy_(torch.tensor(hidden_weights))
        hidden_layer.bias.copy_(torch.tensor(hidden_biases))
        output_layer.weight.copy_(torch.tensor(output_weights))
        output_layer.bias.copy_(torch.tensor(output_biases))
        batch = torch.tensor([inputs], dtype=torch.float32)
        torch_hidden = hidden_layer(batch)
        torch_active = relu(torch_hidden)
        torch_scores = output_layer(torch_active)

    assert torch.allclose(torch_hidden, torch.tensor([hidden_raw]))
    assert torch.allclose(torch_active, torch.tensor([hidden_active]))
    assert torch.allclose(torch_scores, torch.tensor([manual_scores]))
    print(f"输入形状: {tuple(batch.shape)}")
    print(f"隐藏层加权和: {hidden_raw}")
    print(f"ReLU 后: {hidden_active}")
    print(f"手算分数: {manual_scores}")
    print(f"PyTorch 分数: {torch_scores.tolist()}")
    print(f"输出形状: {tuple(torch_scores.shape)}")
    print("逐层对照: 全部一致")


if __name__ == "__main__":
    main()
