"""固定 YOLOv8 检测导出契约，完成 letterbox、分类别 NMS 与坐标还原。"""

import argparse, json
from pathlib import Path
import cv2
import numpy as np


def preprocess(image, size):
    h, w = image.shape[:2]
    ratio = min(size / w, size / h)
    nw, nh = round(w * ratio), round(h * ratio)
    left, top = (size - nw) // 2, (size - nh) // 2
    canvas = np.full((size, size, 3), 114, np.uint8)
    canvas[top : top + nh, left : left + nw] = cv2.resize(image, (nw, nh))
    tensor = (
        np.ascontiguousarray(
            canvas[:, :, ::-1].transpose(2, 0, 1)[None], dtype=np.float32
        )
        / 255
    )
    return tensor, (nw / w, nh / h, left, top, w, h)


def iou(a, b):
    lo = np.maximum(a[:2], b[:2])
    hi = np.minimum(a[2:], b[2:])
    inter = np.maximum(hi - lo, 0).prod()
    union = (
        np.maximum(a[2:] - a[:2], 0).prod()
        + np.maximum(b[2:] - b[:2], 0).prod()
        - inter
    )
    return float(inter / union) if union > 0 else 0.0


def decode(raw, meta, classes, score=0.25, threshold=0.45):
    if raw.ndim != 3 or raw.shape[0] != 1 or raw.shape[1] != 4 + classes:
        raise ValueError("expected [1,4+C,A], decoded YOLOv8 detection export")
    if not np.isfinite(raw).all():
        raise ValueError("nonfinite output")
    rows = raw[0].T
    labels = rows[:, 4:].argmax(1)
    scores = rows[np.arange(len(rows)), 4 + labels]
    candidates = []
    for i in np.argsort(-scores)[:3000]:
        if scores[i] < score:
            continue
        cx, cy, w, h = rows[i, :4]
        if w <= 0 or h <= 0:
            continue
        box = np.array([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2])
        if all(
            int(labels[i]) != c or iou(box, b) <= threshold for b, _, c in candidates
        ):
            candidates.append((box, float(scores[i]), int(labels[i])))
    sx, sy, left, top, width, height = meta
    result = []
    for box, s, c in candidates:
        box = (box - np.array([left, top, left, top])) / np.array([sx, sy, sx, sy])
        box[[0, 2]] = box[[0, 2]].clip(0, width)
        box[[1, 3]] = box[[1, 3]].clip(0, height)
        if box[2] > box[0] and box[3] > box[1]:
            result.append({"box": box.tolist(), "score": s, "class_id": c})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path)
    parser.add_argument("--image", type=Path)
    parser.add_argument("--classes", type=int, default=2)
    args = parser.parse_args()
    if args.classes < 1:
        parser.error("classes must be positive")
    if bool(args.model) != bool(args.image):
        parser.error("model and image must be supplied together")
    if args.model:
        import onnxruntime as ort

        session = ort.InferenceSession(
            str(args.model), providers=["CPUExecutionProvider"]
        )
        inputs = session.get_inputs()
        if len(inputs) != 1:
            raise ValueError("one input required")
        inp = inputs[0]
        if (
            inp.type != "tensor(float)"
            or len(inp.shape) != 4
            or inp.shape[:2] != [1, 3]
            or not isinstance(inp.shape[2], int)
            or inp.shape[2] != inp.shape[3]
        ):
            raise ValueError("expected static FP32 [1,3,S,S]")
        image = cv2.imread(str(args.image))
        if image is None:
            raise ValueError("cannot read image")
        x, meta = preprocess(image, inp.shape[2])
        outputs = session.run(None, {inp.name: x})
        if len(outputs) != 1:
            raise ValueError("one detection output required")
        result = decode(outputs[0], meta, args.classes)
    else:
        x, meta = preprocess(np.zeros((360, 640, 3), np.uint8), 640)
        raw = np.array(
            [[[150, 151], [240, 241], [100, 100], [100, 100], [0.9, 0.8], [0.1, 0.2]]],
            np.float32,
        )
        result = decode(raw, meta, 2)
        assert len(result) == 1
        np.testing.assert_allclose(result[0]["box"], [100, 50, 200, 150])
        assert x.shape == (1, 3, 640, 640)
        print("constructed output smoke check; no trained weights")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
