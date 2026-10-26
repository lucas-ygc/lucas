# 实际运行记录

日期：2026-10-24。Python 3.13.9，Linux CPU 环境。将本包文件单独复制到临时目录执行，确认没有依赖其他文章目录。

```bash
python3 main.py
```

退出码 0，代码中的断言通过。

```text
('features.0.0', [1, 3, 64, 64], [1, 32, 32, 32])
('features.0.1', [1, 32, 32, 32], [1, 32, 32, 32])
('features.0.2', [1, 32, 32, 32], [1, 32, 32, 32])
('features.1.conv.0.0', [1, 32, 32, 32], [1, 32, 32, 32])
('features.18.1', [1, 1280, 2, 2], [1, 1280, 2, 2])
('features.18.2', [1, 1280, 2, 2], [1, 1280, 2, 2])
('classifier.0', [1, 1280], [1, 1280])
('classifier.1', [1, 1280], [1, 1000])
parameters: 3504872
output: [1, 1000] random weights: structure check only
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
