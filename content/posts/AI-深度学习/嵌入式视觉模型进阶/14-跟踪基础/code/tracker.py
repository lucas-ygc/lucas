"""教学版恒速 Kalman + IoU/Hungarian 跟踪；非官方 SORT/ByteTrack 实现。"""

import numpy as np
from scipy.optimize import linear_sum_assignment


def iou(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    lo = np.maximum(a[:2], b[:2])
    hi = np.minimum(a[2:], b[2:])
    inter = np.maximum(hi - lo, 0).prod()
    union = (
        np.maximum(a[2:] - a[:2], 0).prod()
        + np.maximum(b[2:] - b[:2], 0).prod()
        - inter
    )
    return float(inter / union) if union > 0 else 0.0


def measure(box):
    box = np.asarray(box, dtype=float)
    return np.r_[(box[:2] + box[2:]) / 2, box[2:] - box[:2]]


class Track:
    def __init__(self, ident, detection):
        self.id = ident
        self.label = detection.get("class_id", 0)
        self.x = np.r_[measure(detection["box"]), np.zeros(4)]
        self.p = np.diag([10.0] * 4 + [100.0] * 4)
        self.missed = 0
        self.hits = 1
        self.matched = True

    @property
    def box(self):
        cx, cy, w, h = self.x[:4]
        w, h = max(w, 1), max(h, 1)
        return np.array([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2])

    def predict(self, dt):
        f = np.eye(8)
        f[:4, 4:] = np.eye(4) * dt
        self.x = f @ self.x
        self.p = f @ self.p @ f.T + np.eye(8) * 0.1
        self.missed += 1
        self.matched = False

    def update(self, detection):
        h = np.eye(4, 8)
        r = np.eye(4)
        innovation = measure(detection["box"]) - h @ self.x
        s = h @ self.p @ h.T + r
        k = np.linalg.solve(s, (self.p @ h.T).T).T
        self.x += k @ innovation
        a = np.eye(8) - k @ h
        self.p = a @ self.p @ a.T + k @ r @ k.T
        self.missed = 0
        self.hits += 1
        self.matched = True


class Tracker:
    def __init__(self, max_age=2, threshold=0.2):
        self.max_age = max_age
        self.threshold = threshold
        self.tracks = []
        self.next_id = 1

    def associate(self, indices, detections):
        if not indices or not detections:
            return [], list(indices), list(range(len(detections)))
        cost = np.full((len(indices), len(detections)), 1e6)
        for r, index in enumerate(indices):
            track = self.tracks[index]
            for c, det in enumerate(detections):
                overlap = iou(track.box, det["box"])
                if track.label == det.get("class_id", 0) and overlap >= self.threshold:
                    cost[r, c] = 1 - overlap
        rows, cols = linear_sum_assignment(cost)
        pairs = [(indices[r], int(c)) for r, c in zip(rows, cols) if cost[r, c] < 1e6]
        return (
            pairs,
            [i for i in indices if i not in {a for a, b in pairs}],
            [j for j in range(len(detections)) if j not in {b for a, b in pairs}],
        )

    def step(self, detections, dt=1.0, low=None):
        if not np.isfinite(dt) or dt <= 0:
            raise ValueError("positive dt required")
        for det in list(detections) + list(low or []):
            b = np.asarray(det["box"])
            if b.shape != (4,) or not np.isfinite(b).all() or np.any(b[2:] <= b[:2]):
                raise ValueError("invalid xyxy")
        for track in self.tracks:
            track.predict(dt)
        pairs, unmatched, new = self.associate(
            list(range(len(self.tracks))), detections
        )
        for i, j in pairs:
            self.tracks[i].update(detections[j])
        if low:
            pairs, _, _ = self.associate(unmatched, low)
            for i, j in pairs:
                self.tracks[i].update(low[j])
        for j in new:
            self.tracks.append(Track(self.next_id, detections[j]))
            self.next_id += 1
        self.tracks = [t for t in self.tracks if t.missed <= self.max_age]
        return [
            {
                "id": t.id,
                "box": t.box.tolist(),
                "matched": t.matched,
                "missed": t.missed,
                "class_id": t.label,
            }
            for t in self.tracks
        ]
