"""通过有序四边形和透视变换理解文字裁剪，保留阅读方向与边界信息。"""

import cv2
import numpy as np


def rectify(image, points):
    p = np.asarray(points, np.float32)
    if (
        p.shape != (4, 2)
        or not np.isfinite(p).all()
        or not cv2.isContourConvex(p)
        or abs(cv2.contourArea(p)) < 1
    ):
        raise ValueError("ordered nondegenerate convex quadrilateral required")
    width = max(2, round(max(np.linalg.norm(p[1] - p[0]), np.linalg.norm(p[2] - p[3]))))
    height = max(
        2, round(max(np.linalg.norm(p[3] - p[0]), np.linalg.norm(p[2] - p[1])))
    )
    if max(width, height) > 4096:
        raise ValueError("crop too large")
    dst = np.array(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], np.float32
    )
    matrix = cv2.getPerspectiveTransform(p, dst)
    projected = cv2.perspectiveTransform(p[None], matrix)[0]
    np.testing.assert_allclose(projected, dst, atol=1e-3)
    return cv2.warpPerspective(image, matrix, (width, height))


def main():
    image = np.full((120, 200, 3), 255, np.uint8)
    p = np.array([[25, 25], [170, 15], [180, 80], [20, 95]], np.float32)
    cv2.polylines(image, [p.astype(np.int32)], True, (0, 0, 0), 2)
    crop = rectify(image, p)
    print("rectified shape", crop.shape)
    try:
        rectify(image, [[0, 0], [1, 1], [2, 2], [3, 3]])
    except ValueError:
        print("degenerate quadrilateral rejected")
    else:
        raise AssertionError("degenerate accepted")


if __name__ == "__main__":
    main()
