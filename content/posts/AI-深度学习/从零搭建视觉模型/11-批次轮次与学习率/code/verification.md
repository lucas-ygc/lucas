# 运行验证

2026-10-23，在 Python 3.13.9、CPU 环境实际执行：

```bash
python3 main.py
```

退出码 0，脚本内断言通过。

```text
batch sizes: [32, 32, 32, 7] updates: 12
样本加权损失: 0.8815533980582524 批次直接平均: 1.1
epoch 1 lr 0.1
epoch 2 lr 0.05
epoch 3 lr 0.025
```

依赖环境：PyTorch 2.13.0+cu130、Torchvision 0.28.0+cu130、ONNX 1.22.0、ONNX Runtime 1.28.0（仅涉及相应库的实验使用）。

本记录仅证明该教学输入的流程与断言通过；未下载真实数据或预训练权重，未进行摄像头与 NPU 板端验收。
