"""在独立验证对上选择阈值，区分一对一核验、检索与未知身份拒绝。"""

import numpy as np


def rates(genuine, impostor, threshold):
    return float(np.mean(impostor >= threshold)), float(np.mean(genuine < threshold))


def main():
    genuine = np.array([0.62, 0.71, 0.80, 0.91])
    impostor = np.array([0.1, 0.3, 0.5, 0.65])
    candidates = np.r_[
        -1.0,
        np.unique(np.r_[genuine, impostor]),
        np.nextafter(np.unique(np.r_[genuine, impostor]), np.inf),
        1.01,
    ]
    feasible = [
        (rates(genuine, impostor, t)[1], t)
        for t in candidates
        if rates(genuine, impostor, t)[0] == 0
    ]
    frr, threshold = min(feasible)
    far, frr = rates(genuine, impostor, threshold)
    assert far == 0 and frr == 0.25
    print("constructed validation threshold", threshold, "FAR", far, "FRR", frr)
    test_rates = rates(np.array([0.6, 0.85]), np.array([0.2, 0.72]), threshold)
    print("frozen-threshold constructed test FAR/FRR", test_rates)
    assert test_rates == (0.5, 0.5)


if __name__ == "__main__":
    main()
