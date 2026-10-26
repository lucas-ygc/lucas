# 训练自己的检测器与错误分析

检查 YOLO 标注、按来源划分数据，并提供真实数据训练入口。

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

## 真实训练入口

先安装 `requirements-real.txt`，准备本地模型结构 YAML 和数据 YAML，然后执行 `python3 train_real.py --data dataset.yaml --model yolov8n.yaml --epochs 20`。模型随机初始化，未在本次制作中执行真实训练。安装后固定实际 Ultralytics 版本，再做数据路径与离线下载行为检查。
