# 完整 YOLOv8 推理：从图片到原图目标框

固定 YOLOv8 检测导出契约，完成 letterbox、分类别 NMS 与坐标还原。

## 快速运行

使用 Python 3.11+，在本目录或下载包解压目录执行。建议使用独立虚拟环境。

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

默认实验使用代码内构造输入或包内样例，不自动下载模型和数据。每篇辅助文件都在本包内，无跨文章目录依赖。

## 学习与修改

具体推导、修改任务、参考结论和适用范围见正文。先预测原始输出，再运行；修改输入条件时同步调整对应断言，不能直接删除断言来掩盖错误。

## 实际验证

见 `verification.md`，其中记录执行命令、环境、输出和未验证项。依赖清单用于安装，验证记录中的版本是本次环境，不表示所有版本都等价。

## 本地真实模型

`python3 main.py --model model.onnx --image frame.jpg --classes 80`。仅支持静态 FP32、batch=1、nms=False 的 YOLOv8 检测导出，输出 `[1,4+C,A]`。必须自行提供匹配的本地模型与图片；类别数按模型填写。
