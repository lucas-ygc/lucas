# 模型怎样预测类别

本章仅使用 Python 3 标准库，无第三方依赖，无需下载数据或训练模型。
在本目录打开终端，依次运行：

```bash
python3 01_scores_to_probabilities.py
python3 02_batch_predictions.py
python3 03_threshold_decisions.py
```

三个入口共同使用本目录的 `prediction.py`。下载时保留整个代码包；不依赖其他文章目录。输入直接写在脚本内，均为构造的分数与标签，不是 CNN 实测输出。

1. 对比分数整体平移后的 Softmax，观察直接求指数的溢出与稳定计算。
2. 用列表模拟 `[N, C]`，逐行计算类别，并观察错误类别映射和错误轴的结果。此处未使用 PyTorch 张量。
3. 输出 `class_id`、`class_name`、`score`、`accepted`，比较不同阈值下的拒绝率和接受样本错误率。拒绝时类别字段仍保留候选预测，业务应先检查 `accepted`。

可修改分数观察概率变化；修改预设样本时也需相应修改教学断言。类别顺序必须与训练时一致。本例平分时取第一个类别，实际任务应明确平分策略。

阈值仅用于演示，不能直接移植为上线标准。全拒绝时接受样本错误率没有定义，不能记为零。运行记录见 [verification.md](verification.md)。
