# MLP：训练、损失和独立推理

Python 3，依赖 PyTorch 与 Pillow。仅 CPU，不下载数据；全部输入由本目录代码生成。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python loss_demo.py
python train.py
python predict.py
python predict.py outputs/vertical.png
```

在代码目录执行以上命令。也可以在任意工作目录以脚本绝对路径运行；默认产物相对于脚本存放在 `outputs/`。

- `model.py`：256 → 32 → 2 的 MLP，无卷积，隐藏层使用 ReLU。
- `dataset.py`：16×16 灰度条纹，像素量化后除以 255；生成、存图、读图契约一致。
- `loss_demo.py`：显式交叉熵公式与 PyTorch 对照，包括 logits 梯度。
- `train.py`：训练集 512、验证集 128、测试集 128，分别用种子 100/200/300 生成。按验证损失保存最佳权重，最后测试一次。
- `predict.py`：独立加载 `best.pt`，不触发训练，输出候选类别、分数和原始 logits。

`outputs/` 包含最佳推理权重 `best.pt`、训练记录 `history.csv` 和两张新生成的演示图。重复运行会覆盖同一输出目录，保留实验可指定新目录：

```bash
python train.py --epochs 30 --lr 0.1 --batch-size 32 --out outputs/run2
python predict.py outputs/run2/vertical.png --checkpoint outputs/run2/best.pt
```

只加载自己生成或可信来源的权重。检查点保存结构版本、类别顺序、预处理和最佳轮次，但未保存优化器或随机状态，不支持精确恢复训练。

图片必须为 16×16；彩色图片转灰度，不自动缩放。这里仅学习合成条纹，任意照片的输出没有可靠分类含义。分数不是经过校准的现实正确率。

完整运行记录见 verification.md。固定种子帮助同环境重现，跨版本不保证数值完全一致。

## 导出 ONNX 并独立推理

先运行训练，再执行：

```bash
python export_onnx.py
python predict_onnx.py
python predict_onnx.py outputs/vertical.png
```

导出器显式采用 `dynamo=False`、opset 17，与第 22 章一致。可能打印传统导出器弃用提示；本实验未验证其他导出路径。输入固定为 float32 `[1,1,16,16]`，输出为 `[1,2]` logits，预处理与 Softmax 在图外。类别与预处理约定写入 ONNX metadata。

导出后运行 ONNX checker，并在 128 个新条纹样本和全零、全一、常量、噪声四个输入上比较输出，容差 `rtol=1e-4, atol=1e-5`，同时检查类别一致。特殊输入仅检查转换一致性，不判断分类是否有意义。

自定义目录时：

```bash
python export_onnx.py --checkpoint outputs/run2/best.pt --out outputs/run2/model.onnx
python predict_onnx.py outputs/run2/vertical.png --model outputs/run2/model.onnx
```

`predict_onnx.py` 可单独复制到另一个环境，携带 `model.onnx` 和输入图片，只需安装 `numpy Pillow onnxruntime`。脚本不导入本目录其他模块或 PyTorch。ONNX Runtime CPU 验证不代表 NPU 转换与板端验证已经完成。
