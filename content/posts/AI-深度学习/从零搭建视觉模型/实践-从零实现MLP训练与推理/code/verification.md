# MLP 综合实践运行记录

2026-10-23，在 CPU 上实际运行。构造条纹数据的成绩不能解释为真实图片识别能力。

Python 3.13.9；torch 2.13.0；Pillow 10.4.0；numpy 2.3.5；onnx 1.22.0；onnxruntime 1.28.0。

## loss_demo.py 

```text
逐样本损失: [1.313262, 0.126928]
平均损失: 0.720095
logits 梯度: [[0.36552929878234863, -0.36552929878234863], [0.05960145592689514, -0.05960148572921753]]
显式公式、框架交叉熵与梯度对照通过。
```

## train.py 

```text
训练前 val_loss=0.6949, val_accuracy=50.0%
epoch 01: train_loss=0.6187, val_loss=0.5155, val_accuracy=98.4%
epoch 02: train_loss=0.4120, val_loss=0.2986, val_accuracy=96.9%
epoch 03: train_loss=0.2319, val_loss=0.1698, val_accuracy=100.0%
epoch 04: train_loss=0.1346, val_loss=0.1040, val_accuracy=100.0%
epoch 05: train_loss=0.0860, val_loss=0.0706, val_accuracy=100.0%
epoch 06: train_loss=0.0592, val_loss=0.0516, val_accuracy=100.0%
epoch 07: train_loss=0.0442, val_loss=0.0397, val_accuracy=100.0%
epoch 08: train_loss=0.0342, val_loss=0.0317, val_accuracy=100.0%
epoch 09: train_loss=0.0275, val_loss=0.0264, val_accuracy=100.0%
epoch 10: train_loss=0.0230, val_loss=0.0221, val_accuracy=100.0%
epoch 11: train_loss=0.0195, val_loss=0.0191, val_accuracy=100.0%
epoch 12: train_loss=0.0168, val_loss=0.0167, val_accuracy=100.0%
epoch 13: train_loss=0.0147, val_loss=0.0148, val_accuracy=100.0%
epoch 14: train_loss=0.0131, val_loss=0.0132, val_accuracy=100.0%
epoch 15: train_loss=0.0117, val_loss=0.0120, val_accuracy=100.0%
epoch 16: train_loss=0.0106, val_loss=0.0110, val_accuracy=100.0%
epoch 17: train_loss=0.0097, val_loss=0.0100, val_accuracy=100.0%
epoch 18: train_loss=0.0089, val_loss=0.0092, val_accuracy=100.0%
epoch 19: train_loss=0.0082, val_loss=0.0086, val_accuracy=100.0%
epoch 20: train_loss=0.0076, val_loss=0.0080, val_accuracy=100.0%
epoch 21: train_loss=0.0070, val_loss=0.0075, val_accuracy=100.0%
epoch 22: train_loss=0.0066, val_loss=0.0070, val_accuracy=100.0%
epoch 23: train_loss=0.0062, val_loss=0.0066, val_accuracy=100.0%
epoch 24: train_loss=0.0058, val_loss=0.0062, val_accuracy=100.0%
epoch 25: train_loss=0.0055, val_loss=0.0059, val_accuracy=100.0%
epoch 26: train_loss=0.0052, val_loss=0.0056, val_accuracy=100.0%
epoch 27: train_loss=0.0049, val_loss=0.0053, val_accuracy=100.0%
epoch 28: train_loss=0.0047, val_loss=0.0051, val_accuracy=100.0%
epoch 29: train_loss=0.0045, val_loss=0.0048, val_accuracy=100.0%
epoch 30: train_loss=0.0042, val_loss=0.0046, val_accuracy=100.0%
最佳 epoch=30, test_loss=0.0049, test_accuracy=100.0%
保存至 /tmp/mlp-practice-verification；只验证合成条纹，不代表真实图片识别能力。
```

## predict.py 

```text
{"class_id": 0, "class_name": "横条纹", "score": 0.9998817443847656, "logits": [4.632380485534668, -4.410283088684082]}
```

## predict.py vertical.png

```text
{"class_id": 1, "class_name": "竖条纹", "score": 0.9997431635856628, "logits": [-4.2264556884765625, 4.040530681610107]}
```

## export_onnx.py 

```text
ONNX 校验通过；输入=images [1,1,16,16] float32，输出=logits [1,2]
数值对照 132 个输入，max_abs_error=1.6689301e-06，类别一致=132/132
导出至 /tmp/mlp-practice-verification/model.onnx；验证范围为 ONNX Runtime CPU。
```

## predict_onnx.py 

```text
{"class_id": 0, "class_name": "横条纹", "score": 0.9998817443847656, "logits": [4.63238000869751, -4.410282135009766]}
```

## predict_onnx.py vertical.png

```text
{"class_id": 1, "class_name": "竖条纹", "score": 0.9997431635856628, "logits": [-4.2264556884765625, 4.040530681610107]}
```

所有入口均从 `/tmp` 工作目录执行，并显式指定独立产物目录。ONNX 导出器打印传统导出路径弃用提示，但 checker、数值与类别对照通过。训练保存时逐次检查加载前后同一输入的输出一致。

## 补充检查

- PNG 保存与读取后张量逐元素完全一致。
- 17 个样本分别按 batch=6、17 评估，损失与准确率一致，覆盖末尾小批次。
- 验证前后模型参数完全一致。
- 两个推理程序拒绝错误尺寸；ONNX 推理拒绝缺失模型；训练拒绝零轮次，均返回退出码 2。
- 将 ONNX 脚本、模型和图片复制到独立目录，主动阻止 torch 导入后仍可正确预测横条纹。
