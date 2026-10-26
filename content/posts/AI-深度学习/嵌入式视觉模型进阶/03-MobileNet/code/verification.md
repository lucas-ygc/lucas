# 实际运行记录

日期：2026-10-24。Python 3.13.9，Linux CPU 环境。将本包文件单独复制到临时目录执行，确认没有依赖其他文章目录。

```bash
python3 main.py
```

退出码 0，代码中的断言通过。

```text
V1 [2, 24, 24, 24] 608
InvertedResidual [2, 16, 24, 24] 4352
InvertedResidual [2, 24, 12, 12] 5136
```

## 验证范围

默认输入是构造数据或包内样例；只证明本课计算、接口和特定断言通过，不代表真实数据精度或板端性能。

## 环境版本

- torch: 2.13.0
- torchvision: 0.28.0
- numpy: 2.3.5
- onnx: 1.22.0
- onnxruntime: 1.28.0
- scipy: 1.16.3
- OpenCV (cv2): 5.0.0

上表记录可用环境，具体使用的库以 requirements.txt 为准；脚本均在 CPU 执行。
