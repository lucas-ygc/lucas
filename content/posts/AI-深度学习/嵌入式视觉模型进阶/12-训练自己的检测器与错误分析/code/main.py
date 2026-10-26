"""检查 YOLO 标注、按来源划分数据，并提供真实数据训练入口。"""

import numpy as np


def check_label(line, classes):
    values = list(map(float, line.split()))
    if len(values) != 5 or not np.isfinite(values).all():
        raise ValueError("five finite values required")
    c, x, y, w, h = values
    if (
        c != int(c)
        or not 0 <= c < classes
        or min(w, h) <= 0
        or not 0 <= x - w / 2 <= x + w / 2 <= 1
        or not 0 <= y - h / 2 <= y + h / 2 <= 1
    ):
        raise ValueError("invalid class or box")
    return int(c), np.array([x - w / 2, y - h / 2, x + w / 2, y + h / 2])


def iou(a, b):
    inter = np.maximum(np.minimum(a[2:], b[2:]) - np.maximum(a[:2], b[:2]), 0).prod()
    return float(inter / ((a[2:] - a[:2]).prod() + (b[2:] - b[:2]).prod() - inter))


def main():
    truth = [check_label("0 .3 .3 .2 .2", 2), check_label("1 .7 .7 .2 .2", 2)]
    predictions = [(0, truth[0][1], 0.9), (0, truth[0][1], 0.8), (0, truth[1][1], 0.7)]
    used = set()
    tp = 0
    for c, box, score in sorted(predictions, key=lambda p: -p[2]):
        candidates = [
            (iou(box, b), i)
            for i, (label, b) in enumerate(truth)
            if label == c and i not in used
        ]
        if candidates and max(candidates)[0] >= 0.5:
            tp += 1
            used.add(max(candidates)[1])
    fp = len(predictions) - tp
    fn = len(truth) - tp
    assert (tp, fp, fn) == (1, 2, 1)
    print("constructed TP/FP/FN:", tp, fp, fn)
    try:
        check_label("0 .9 .9 .4 .4", 2)
    except ValueError:
        print("invalid boundary rejected")
    else:
        raise AssertionError("invalid label accepted")


if __name__ == "__main__":
    main()
