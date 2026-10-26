"""用五点几何实验验证相似变换与裁剪，建立人脸识别前的输入契约。"""

import cv2
import numpy as np


def main():
    template = np.array([[30, 35], [70, 35], [50, 55], [35, 75], [65, 75]], np.float32)
    forward = cv2.getRotationMatrix2D((50, 50), 15, 1.2)
    forward[:, 2] += np.array([8, 4])
    observed = cv2.transform(template[None], forward)[0]
    matrix, inliers = cv2.estimateAffinePartial2D(observed, template, method=cv2.LMEDS)
    assert matrix is not None
    aligned = cv2.transform(observed[None], matrix)[0]
    error = float(np.linalg.norm(aligned - template, axis=1).max())
    assert error < 1e-3
    image = np.zeros((128, 128, 3), np.uint8)
    for point in observed:
        cv2.circle(image, tuple(np.round(point).astype(int)), 3, (0, 255, 0), -1)
    crop = cv2.warpAffine(
        image, matrix, (100, 100), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0)
    )
    assert crop.shape == (100, 100, 3)
    print(
        "max landmark error",
        error,
        "crop shape",
        crop.shape,
        "inliers",
        int(inliers.sum()),
    )


if __name__ == "__main__":
    main()
