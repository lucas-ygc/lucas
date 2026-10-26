"""区分相对深度与米制距离，并通过去噪对照理解参考图、PSNR 和细节损失。"""

import cv2, numpy as np


def psnr(a, b):
    mse = float(np.mean((a - b) ** 2))
    return float("inf") if mse == 0 else 10 * np.log10(1 / mse)


def main():
    metric = np.array([1.0, 2.0, 4.0, 8.0])
    raw = 2 / metric + 0.3
    scale, offset = np.linalg.lstsq(
        np.c_[raw, np.ones_like(raw)], 1 / metric, rcond=None
    )[0]
    restored = 1 / (scale * raw + offset)
    np.testing.assert_allclose(restored, metric)
    rng = np.random.default_rng(7)
    clean = np.tile(np.linspace(0.2, 0.8, 64), (64, 1)).astype(np.float32)
    noisy = np.clip(clean + rng.normal(0, 0.05, clean.shape), 0, 1).astype(np.float32)
    denoised = cv2.GaussianBlur(noisy, (3, 3), 0.8)
    before, after = psnr(clean, noisy), psnr(clean, denoised)
    assert after > before
    print(
        "constructed inverse-depth scale/offset",
        scale,
        offset,
        "distance",
        restored.tolist(),
    )
    print("smooth synthetic image PSNR before/after", before, after)


if __name__ == "__main__":
    main()
