"""本章共享的计算函数，仅使用 Python 标准库。"""

import math


def softmax(scores):
    """输入一张图片的有限实数分数，返回按类别排列的概率。"""
    if not scores or not all(math.isfinite(x) for x in scores):
        raise ValueError("分数必须是非空的有限实数序列")
    shift = max(scores)
    exp_scores = [math.exp(x - shift) for x in scores]
    total = sum(exp_scores)
    return [x / total for x in exp_scores]


def argmax(values):
    """相同最大值时取最先出现的索引。"""
    return max(range(len(values)), key=values.__getitem__)


def predict(scores, classes, threshold):
    if len(scores) != len(classes):
        raise ValueError("类别名称数必须与输出分数数目一致")
    if not 0 <= threshold <= 1:
        raise ValueError("阈值必须在 0 到 1 之间")
    probs = softmax(scores)
    index = argmax(scores)
    return {
        "class_id": index,
        "class_name": classes[index],
        "score": probs[index],
        "accepted": probs[index] >= threshold,
    }
