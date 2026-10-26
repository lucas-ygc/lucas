# 导出 ONNX 并对照数值

在本目录运行，或将网页下载包解压后运行。输入均在脚本内构造，不依赖其他文章，不联网下载。

建议使用 Python 3.11+ 虚拟环境，安装依赖：

```bash
python3 -m pip install -r requirements.txt
```

```bash
python3 main.py
```

## 观察结果

通过 ONNX 检查，CPU Runtime 与 PyTorch 满足 rtol=1e-4、atol=1e-5；导出文件在临时目录。

## 动手修改

将输入种子改为 8，重新比较完整 logits，而不只比较 argmax。

先写下预测，再运行并记录差异。脚本中的断言用于核对原始配置；修改任务后需要按新的手算结果调整断言。
