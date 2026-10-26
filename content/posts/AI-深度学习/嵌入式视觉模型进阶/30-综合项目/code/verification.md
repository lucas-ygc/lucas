# 实际运行记录

日期：2026-10-24。Python 3.13.9，Linux CPU 环境。将本包文件单独复制到临时目录执行，确认没有依赖其他文章目录。

```bash
python3 main.py
```

退出码 0，代码中的断言通过。

```text
frames 8 checks passed lost/stale stops 3
report: runs/report.json
```

## 验证范围

默认输入是构造数据或包内样例；只证明本课计算、接口和特定断言通过，不代表真实数据精度或板端性能。综合项目的 8 帧构造检测回放通过；真实录像、摄像头、NPU 和电机未执行。video.py 已检查语法与 --help，另见下方构造 ONNX 和录像的接口集成检查。

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

另使用本地构造的固定输出 ONNX 图执行了真实 ONNX Runtime 调用。输入 3 帧本地构造录像，检查日志、连续 ID 与结束零速度命令。

图的输出为常量，不是训练好的检测模型；此项只验证文件读取、运行库调用和接口串联，不证明真实检测效果。
