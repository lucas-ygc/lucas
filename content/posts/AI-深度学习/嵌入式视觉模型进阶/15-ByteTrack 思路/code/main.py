"""比较单阈值与两阶段关联，理解低分观测的用途及身份切换风险。"""

from tracker import Tracker


def run(two_stage):
    tracker = Tracker(max_age=1)
    ids = []
    for frame, score in enumerate([0.9, 0.9, 0.3, 0.3, 0.9]):
        det = {
            "box": [10 + 2 * frame, 10, 30 + 2 * frame, 30],
            "score": score,
            "class_id": 0,
        }
        high = [det] if score >= 0.6 else []
        low = [det] if 0.1 <= score < 0.6 else []
        low.append({"box": [200, 200, 220, 220], "score": 0.2, "class_id": 0})
        rows = tracker.step(high, low=low if two_stage else None)
        ids.append([r["id"] for r in rows if r["matched"]])
    return ids


def main():
    baseline = run(False)
    two = run(True)
    print("high only", baseline, "two stage", two)
    assert baseline[-1] == [2] and all(row == [1] for row in two)


if __name__ == "__main__":
    main()
