# Hi3516CV610 YuNet 转换教学代码

配合博客第 12 章使用。把本目录文件复制到项目 `application/.temp/npu-handbook-tools/`，从项目根目录运行。代码不包含 SDK、厂商 PDF、模型权重或真实人脸图片。

## 环境

CPU 数据准备需要 Python、numpy、opencv-python、onnx、onnxruntime。2026-10-12 的实际验证版本为 numpy 2.3.5、OpenCV 5.0.0、onnx 1.22.0、onnxruntime 1.28.0。这是验证记录，不要求升级厂商转换容器的 Python 依赖。

ATC 脚本需要本项目 SVP_NNN_PC_V5.0.2.3 转换环境，目标 Hi3516CV610。PC 仿真和板端步骤还依赖项目 benchmark.cpp 与相应工具库，命令见博客第 09、10 章。

## 文件与边界

- audit_onnx.py：ONNX 格式与接口检查；外置权重需额外归档和哈希。
- prepare_yunet.py：仅面向指定 YuNet 2023mar 的 12 输出结构。固定 320，调整首层权重并用 ORT 比较全部输出。真实输入必须是预先选取的头 ROI。
- aipp_yunet.cfg：与变换后模型配套，BGR UINT8 planar，AIPP 除以 255。
- convert_yunet.sh：在项目转换容器运行，拒绝覆盖已有 om 目录。
- compare_outputs.py：读取项目 benchmark 描述日志，支持 type=0 FP32 固定形状，去 stride padding 后比较 NPZ。

## 最小 CPU 冒烟流程

以下命令从项目根目录执行，源模型需已存在，输出路径必须新建：

```bash
mkdir -p application/.temp/yunet320-logs
python3 application/.temp/npu-handbook-tools/prepare_yunet.py \
  --model SDK/Tools/Npu/YuNet/face_detection_yunet_2023mar.onnx \
  --output application/.temp/yunet320-smoke \
  --container-output /workspace/application/.temp/yunet320-smoke \
  --synthetic > application/.temp/yunet320-logs/smoke.log 2>&1
```

合成图只证明文件与数学变换可运行，不能作为正式量化校准或人脸准确率结论。正式流程用 `--images` 替换 `--synthetic`，在新目录保存有代表性的真实 ROI 集合。

CPU 基准使用原图 0～255 FLOAT；变换后图使用除以 255 的 FLOAT。板端和模拟器均接收生成的 input_N.bgr UINT8 原始字节，由 AIPP 完成归一化。

## 验证结果与后续步骤

指定源模型 SHA-256 为 8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4。合成输入下 12 输出浮点等价检查通过，最大绝对差约 1.103e-6。比较器另验证非平凡行 padding、数值差异门槛和错误文件拒绝。

本次未执行 ATC、功能仿真或板端推理。convert_yunet.sh 的 shell 语法已检查，实际转换需具备厂商环境；读取博客的完整命令和验收要求后再操作。比较器没有通用量化合格阈值，不传 --atol 时只报告差异。
