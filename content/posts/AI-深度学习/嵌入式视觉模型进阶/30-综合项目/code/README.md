# 综合项目：检测、跟踪与云台跟随验收

交付可回放的跟踪控制程序、真实视频入口和分层验收报告，完成课程闭环。

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

## 回放与真实视频

默认读取本包 `sequence.json`，报告写入 `runs/report.json`。

```bash
python3 main.py --output runs
python3 video.py --model model.onnx --video recording.mp4 --classes 80 --output runs-video
```

访问摄像头需显式改用 `--camera 0`。程序只记录控制意图，不连接电机。真实视频与板端性能不包含在默认回放验证中。
