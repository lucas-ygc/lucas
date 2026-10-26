# 运行验证

2026-10-23，在 Python 3.13.9、CPU 环境实际执行：

```bash
python3 main.py
```

退出码 0，脚本内断言通过。

```text
threshold: 0.5 matrix: [[2, 1], [1, 2]] precision: 0.6666666666666666 recall: 0.6666666666666666
threshold: 0.75 matrix: [[2, 1], [2, 1]] precision: 0.5 recall: 0.3333333333333333
```

依赖环境：PyTorch 2.13.0+cu130、Torchvision 0.28.0+cu130、ONNX 1.22.0、ONNX Runtime 1.28.0（仅涉及相应库的实验使用）。

本记录仅证明该教学输入的流程与断言通过；未下载真实数据或预训练权重，未进行摄像头与 NPU 板端验收。
