"""通过归一化向量、相似度与运动门控理解外观关联。"""

import numpy as np
from scipy.optimize import linear_sum_assignment


def normalize(x):
    norm = np.linalg.norm(x, axis=-1, keepdims=True)
    if np.any(norm < 1e-12):
        raise ValueError("zero embedding")
    return x / norm


def main():
    tracks = normalize(np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]))
    observations = normalize(np.array([[0.05, 1.0, 0.0], [1.0, 0.05, 0.0]]))
    cosine = tracks @ observations.T
    geometry = np.array([[0.1, 0.4], [0.4, 0.1]])
    cost = 0.2 * geometry + 0.8 * (1 - cosine)
    rows, cols = linear_sum_assignment(cost)
    assert cols.tolist() == [1, 0]
    print("cosine", cosine.tolist(), "matches", list(zip(rows.tolist(), cols.tolist())))
    updated = normalize(0.9 * tracks[0] + 0.1 * observations[1])
    assert abs(np.linalg.norm(updated) - 1) < 1e-12
    try:
        normalize(np.zeros((1, 3)))
    except ValueError:
        print("zero embedding rejected")
    else:
        raise AssertionError("zero embedding accepted")


if __name__ == "__main__":
    main()
