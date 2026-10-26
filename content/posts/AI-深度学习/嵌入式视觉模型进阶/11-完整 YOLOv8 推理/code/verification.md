# 实际运行记录

日期：2026-10-24。Python 3.13.9，Linux CPU 环境。将本包文件单独复制到临时目录执行，确认没有依赖其他文章目录。

```bash
python3 main.py
```

退出码 0，代码中的断言通过。

```text
constructed output smoke check; no trained weights
[
  {
    "box": [
      100.0,
      50.0,
      200.0,
      150.0
    ],
    "score": 0.8999999761581421,
    "class_id": 0
  }
]
```

## 验证范围

默认输入是构造数据或包内样例；只证明本课计算、接口和特定断言通过，不代表真实数据精度或板端性能。真实 YOLO 权重与图片推理未执行；默认构造输出已验证前后处理。

## 环境版本

- torch: 2.13.0
- torchvision: 0.28.0
- numpy: 2.3.5
- onnx: 1.22.0
- onnxruntime: 1.28.0
- scipy: 1.16.3
- OpenCV (cv2): 5.0.0

上表记录可用环境，具体使用的库以 requirements.txt 为准；脚本均在 CPU 执行。

## ONNX 接口集成检查

另使用本地构造的固定输出 ONNX 图执行了真实 ONNX Runtime 调用。输入构造 PNG，检查原图坐标为 [100,50,200,150]。

图的输出为常量，不是训练好的检测模型；此项只验证文件读取、运行库调用和接口串联，不证明真实检测效果。
