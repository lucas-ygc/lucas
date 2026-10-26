"""解码热力图并还原裁剪坐标，区分峰值分数、可见性与动作判断。"""

import numpy as np


def decode(heatmaps, crop, threshold=0.5):
    k, h, w = heatmaps.shape
    x0, y0, x1, y1 = crop
    result = []
    for heat in heatmaps:
        row, col = np.unravel_index(heat.argmax(), heat.shape)
        score = float(heat[row, col])
        point = (
            [x0 + (col + 0.5) * (x1 - x0) / w, y0 + (row + 0.5) * (y1 - y0) / h]
            if score >= threshold
            else None
        )
        result.append({"point": point, "score": score})
    return result


def main():
    maps = np.zeros((3, 4, 4))
    maps[0, 1, 2] = 0.9
    maps[1, 2, 1] = 0.8
    first = decode(maps, [100, 50, 180, 130])
    shifted = decode(maps, [110, 60, 190, 140])
    np.testing.assert_allclose(first[0]["point"], [150, 80])
    assert first[2]["point"] is None
    for a, b in zip(first[:2], shifted[:2]):
        np.testing.assert_allclose(np.array(b["point"]) - a["point"], [10, 10])
    print(first)


if __name__ == "__main__":
    main()
