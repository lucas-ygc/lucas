"""从输入契约、层级结构和输出语义出发，检查模型形状、参数与运行模式。"""

import torch
from torchvision.models import mobilenet_v2


def main():
    torch.manual_seed(7)
    torch.set_num_threads(2)
    model = mobilenet_v2(weights=None).eval()
    records, handles = [], []

    def hook(name):
        def record(module, args, output):
            records.append((name, list(args[0].shape), list(output.shape)))

        return record

    for name, module in model.named_modules():
        if name and not list(module.children()):
            handles.append(module.register_forward_hook(hook(name)))
    with torch.inference_mode():
        output = model(torch.zeros(1, 3, 64, 64))
    for handle in handles:
        handle.remove()
    assert output.shape == (1, 1000)
    for row in records[:4] + records[-4:]:
        print(row)
    print("parameters:", sum(p.numel() for p in model.parameters()))
    print("output:", list(output.shape), "random weights: structure check only")


if __name__ == "__main__":
    main()
