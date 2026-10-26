# CIFAR-10 飞机与汽车分类基线

在本目录使用 Python 3.11+ 及匹配的 PyTorch/Torchvision 环境：

```bash
python3 -m pip install -r requirements.txt
python3 train.py --smoke --epochs 1
```

离线检查使用脚本内构造的 80 张随机图片，验证训练、验证、最佳权重保存和加载，不证明分类效果。检查点记录 `smoke: true`，不可作为真实模型使用。

已有本地 CIFAR-10 时：

```bash
python3 train.py --data data --epochs 5
```

首次需要下载时显式运行 `python3 train.py --download --epochs 5`。数据与代码输出分别在 `data/`、`runs/`，不会打包发布。可用 `--output` 更换输出目录。官方测试集不参与选择轮次。

每类固定随机选 1000 张训练、200 张验证；每轮输出训练损失、验证损失与准确率，按验证损失保存 `best.pt`。脚本只依赖本篇代码，检查点含类别、预处理、划分索引。

## 动手修改

将每类训练数减为 100，保持验证集索引不变，比较训练/验证曲线。注意应只修改 `ids[:1000]`，保留验证区间 `ids[1000:1200]`。记录 seed、环境与耗时。不要以 smoke 准确率评价模型。
