"""建立正常特征库与最近邻异常分数，分析阈值、空间热图和数据污染。"""

import numpy as np


def nearest(query, bank):
    return np.linalg.norm(query[:, None, :] - bank[None, :, :], axis=2).min(1)


def main():
    rng = np.random.default_rng(7)
    bank = rng.normal(0, 0.1, (100, 2))
    validation = rng.normal(0, 0.1, (200, 2))
    threshold = float(np.quantile(nearest(validation, bank), 0.99))
    query = rng.normal(0, 0.1, (64, 2))
    query[27:30] += 2
    heat = nearest(query, bank).reshape(8, 8)
    assert (heat.flat[27:30] > threshold).all()
    polluted = np.vstack([bank, query[27:30]])
    assert np.max(nearest(query[27:30], polluted)) == 0
    print(
        "constructed normal validation threshold",
        threshold,
        "image max",
        float(heat.max()),
        "hot positions",
        np.argwhere(heat > threshold).tolist(),
    )
    print("contaminated memory bank hides injected anomalies")


if __name__ == "__main__":
    main()
