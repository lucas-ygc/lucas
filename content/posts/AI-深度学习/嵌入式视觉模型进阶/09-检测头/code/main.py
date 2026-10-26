"""比较 anchor 偏移与距离回归，分清坐标解码和分数含义。"""

import math
import numpy as np


def anchor_decode(anchor, delta):
    cx, cy, w, h = anchor
    dx, dy, dw, dh = delta
    cx, cy = cx + dx * w, cy + dy * h
    w, h = w * math.exp(dw), h * math.exp(dh)
    return np.array([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2])


def distance_decode(point, ltrb, stride):
    x, y = point
    l, t, r, b = ltrb
    if min(ltrb) < 0:
        raise ValueError("distances must be nonnegative")
    return np.array([x - l, y - t, x + r, y + b]) * stride


def main():
    a = anchor_decode([40, 40, 16, 16], [0, 0, 0, 0])
    b = distance_decode([5, 5], [1, 1, 1, 1], 8)
    np.testing.assert_allclose(a, b)
    print("same xyxy:", a.tolist())
    feature = np.zeros((1, 6, 4, 4))
    print("example head shape", feature.shape, "four distances + two class logits")


if __name__ == "__main__":
    main()
