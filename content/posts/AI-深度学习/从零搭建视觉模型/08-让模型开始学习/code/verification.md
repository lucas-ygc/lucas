# 训练实验验证

2026-10-12，Python 3.13.9，PyTorch 2.13.0+cu130，全部使用 CPU。记录为配套示例运行结果，不是个人作业记录。

## 01_one_update.py

```text
更新前权重: 0.0000
更新前预测: 0.0000
更新前损失: 16.0000
权重梯度: -16.0000
更新后权重: 1.6000
更新后预测: 3.2000
更新后损失: 0.6400
```

## 02_train_stripes.py

```text
训练前验证: loss=0.7008, accuracy=42.2%
epoch 01: train_loss=0.6376, val_loss=0.5385, val_accuracy=89.1%
epoch 02: train_loss=0.4364, val_loss=0.2787, val_accuracy=96.9%
epoch 03: train_loss=0.2051, val_loss=0.1356, val_accuracy=98.4%
epoch 04: train_loss=0.0993, val_loss=0.0925, val_accuracy=98.4%
epoch 05: train_loss=0.0562, val_loss=0.0625, val_accuracy=98.4%
epoch 06: train_loss=0.0379, val_loss=0.0560, val_accuracy=98.4%
epoch 07: train_loss=0.0272, val_loss=0.0548, val_accuracy=98.4%
epoch 08: train_loss=0.0210, val_loss=0.0498, val_accuracy=98.4%
epoch 09: train_loss=0.0169, val_loss=0.0449, val_accuracy=98.4%
epoch 10: train_loss=0.0139, val_loss=0.0472, val_accuracy=98.4%
epoch 11: train_loss=0.0117, val_loss=0.0432, val_accuracy=98.4%
epoch 12: train_loss=0.0102, val_loss=0.0425, val_accuracy=98.4%
epoch 13: train_loss=0.0088, val_loss=0.0420, val_accuracy=98.4%
epoch 14: train_loss=0.0078, val_loss=0.0424, val_accuracy=98.4%
epoch 15: train_loss=0.0069, val_loss=0.0404, val_accuracy=98.4%
epoch 16: train_loss=0.0063, val_loss=0.0407, val_accuracy=98.4%
epoch 17: train_loss=0.0057, val_loss=0.0398, val_accuracy=98.4%
epoch 18: train_loss=0.0053, val_loss=0.0406, val_accuracy=98.4%
epoch 19: train_loss=0.0048, val_loss=0.0396, val_accuracy=98.4%
epoch 20: train_loss=0.0045, val_loss=0.0405, val_accuracy=98.4%
这只是合成条纹任务的验证结果，不代表能识别真实场景。
```

## 补充检查

数据形状、标签类型、数值范围及训练验证样本独立生成已检查。反向计算产生有限梯度但不修改权重，step 后权重变化，evaluate 前后权重一致。两个脚本从 /tmp 工作目录运行成功，训练验证损失下降。固定种子不保证跨环境数值逐位一致；合成验证结果不代表真实场景表现。
