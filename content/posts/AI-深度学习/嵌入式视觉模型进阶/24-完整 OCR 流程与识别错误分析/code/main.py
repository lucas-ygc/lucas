"""串起区域定位、排序、裁剪和识别，用数字样例定位端到端错误。"""

import cv2
import numpy as np


def normalize(crop):
    return (
        cv2.resize(crop, (20, 32), interpolation=cv2.INTER_NEAREST).astype(np.float32)
        / 255
    )


def glyph(text):
    image = np.zeros((50, 40), np.uint8)
    cv2.putText(image, text, (3, 37), cv2.FONT_HERSHEY_SIMPLEX, 1.1, 255, 2, cv2.LINE_8)
    ys, xs = np.where(image > 0)
    return image[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]


def distance(a, b):
    row = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        new = [i]
        for j, cb in enumerate(b, 1):
            new.append(min(new[-1] + 1, row[j] + 1, row[j - 1] + (ca != cb)))
        row = new
    return row[-1]


def main():
    templates = {str(i): normalize(glyph(str(i))) for i in range(10)}
    image = np.zeros((60, 160), np.uint8)
    for i, c in enumerate("120"):
        patch = glyph(c)
        h, w = patch.shape
        image[10 : 10 + h, 10 + i * 45 : 10 + i * 45 + w] = patch
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    count, labels, stats, centers = cv2.connectedComponentsWithStats(binary)
    boxes = sorted(
        [tuple(row[:4]) for row in stats[1:] if row[4] > 10], key=lambda b: b[0]
    )
    results = []
    for x, y, w, h in boxes:
        crop = normalize(binary[y : y + h, x : x + w])
        errors = {c: float(np.mean((crop - t) ** 2)) for c, t in templates.items()}
        char = min(errors, key=errors.get)
        results.append(
            {
                "text": char,
                "box": [int(x), int(y), int(x + w), int(y + h)],
                "template_error": errors[char],
            }
        )
    text = "".join(row["text"] for row in results)
    assert text == "120"
    assert distance("120", "1120") == 1
    print("constructed single-font OCR", results, "CER", distance("120", text) / 3)


if __name__ == "__main__":
    main()
