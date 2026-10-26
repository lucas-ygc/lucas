# 运行验证

2026-10-23，在 Python 3.13.9、CPU 环境实际执行：

```bash
python3 train.py --smoke --epochs 1 --output /tmp/vision-course-smoke
```

退出码 0，脚本内断言通过。

```text
SMOKE: 随机图片，仅检查训练、验证和保存流程
1 0.7091806828975677 0.7034136652946472 0.5
保存并重新加载: /tmp/vision-course-smoke/best.pt best_epoch: 1
```

依赖环境：PyTorch 2.13.0+cu130、Torchvision 0.28.0+cu130、ONNX 1.22.0、ONNX Runtime 1.28.0（仅涉及相应库的实验使用）。

本记录仅证明该教学输入的流程与断言通过；未下载真实数据或预训练权重，未进行摄像头与 NPU 板端验收。
