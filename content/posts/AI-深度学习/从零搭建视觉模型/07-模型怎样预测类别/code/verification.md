# 类别预测实验验证

2026-10-23 验证，Python 3.13.9，仅标准库。以下记录来自实际运行，输入均为构造数据，不代表训练成绩。

## 01_scores_to_probabilities.py

```text
logits=[2, 1] → 概率=[0.7311, 0.2689] → 类别索引=0
logits=[-4, -5] → 概率=[0.7311, 0.2689] → 类别索引=0
logits=[102, 101] → 概率=[0.7311, 0.2689] → 类别索引=0
logits=[1002, 1001] → 概率=[0.7311, 0.2689] → 类别索引=0
直接 exp(1002) 溢出；先减最大值的实现正常。
全部验证通过；相同分数时本实现取第一个类别。
```

## 02_batch_predictions.py

```text
输出形状 [N, C] = [2, 3]：两张图片，每张三个类别
图片 0：概率=[0.8438, 0.1142, 0.042]，class_id=0，class_name=飞机
图片 1：概率=[0.09, 0.6652, 0.2447]，class_id=1，class_name=汽车
类别顺序写反后： ['汽车', '飞机']
分数和索引没变，名称却错了；推理必须保留训练时的类别顺序。
错误地沿图片轴取最大值： [0, 1, 1]
得到的是每类在哪张图片上分数最高，并非每张图片的类别。
```

## 03_threshold_decisions.py

```text
阈值=0.0（score >= 阈值时接受）
{"class_id": 0, "class_name": "飞机", "score": 0.7310585786300049, "accepted": true}
{"class_id": 1, "class_name": "汽车", "score": 0.7310585786300049, "accepted": true}
{"class_id": 0, "class_name": "飞机", "score": 0.52497918747894, "accepted": true}
{"class_id": 0, "class_name": "飞机", "score": 0.9933071490757153, "accepted": true}
接受=4/4，拒绝率=0.0%，接受样本错误率=50.0%
阈值=0.7（score >= 阈值时接受）
{"class_id": 0, "class_name": "飞机", "score": 0.7310585786300049, "accepted": true}
{"class_id": 1, "class_name": "汽车", "score": 0.7310585786300049, "accepted": true}
{"class_id": 0, "class_name": "飞机", "score": 0.52497918747894, "accepted": false}
{"class_id": 0, "class_name": "飞机", "score": 0.9933071490757153, "accepted": true}
接受=3/4，拒绝率=25.0%，接受样本错误率=33.3%
阈值=0.9（score >= 阈值时接受）
{"class_id": 0, "class_name": "飞机", "score": 0.7310585786300049, "accepted": false}
{"class_id": 1, "class_name": "汽车", "score": 0.7310585786300049, "accepted": false}
{"class_id": 0, "class_name": "飞机", "score": 0.52497918747894, "accepted": false}
{"class_id": 0, "class_name": "飞机", "score": 0.9933071490757153, "accepted": true}
接受=1/4，拒绝率=75.0%，接受样本错误率=100.0%
阈值=1.0（score >= 阈值时接受）
{"class_id": 0, "class_name": "飞机", "score": 0.7310585786300049, "accepted": false}
{"class_id": 1, "class_name": "汽车", "score": 0.7310585786300049, "accepted": false}
{"class_id": 0, "class_name": "飞机", "score": 0.52497918747894, "accepted": false}
{"class_id": 0, "class_name": "飞机", "score": 0.9933071490757153, "accepted": false}
接受=0/4，拒绝率=100.0%，接受样本错误率=不适用（无接受样本）
高分也可能预测错误；阈值提高不保证接受样本错误率下降。
```

三个入口均从 `/tmp` 工作目录运行成功，教学断言全部通过；共享模块从脚本目录加载，无外部文件或第三方包依赖。
