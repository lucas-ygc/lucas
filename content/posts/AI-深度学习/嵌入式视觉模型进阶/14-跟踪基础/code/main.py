"""实现恒速 Kalman、IoU 匹配和轨迹管理，认识检测与身份关联的区别。"""

from tracker import Tracker


def det(x, y=10):
    return {"box": [x, y, x + 20, y + 20], "score": 0.9, "class_id": 0}


def main():
    tracker = Tracker(max_age=2)
    frames = [[det(10), det(100)], [det(102), det(12)], [det(104)], [det(16), det(106)]]
    seen = []
    for i, detections in enumerate(frames):
        rows = tracker.step(detections)
        seen.append(rows)
        print(i, [(r["id"], round(r["box"][0], 2), r["matched"]) for r in rows])
    assert [r["id"] for r in seen[-1]] == [1, 2]
    assert not seen[2][0]["matched"] and seen[3][0]["matched"]
    for _ in range(3):
        rows = tracker.step([])
    assert rows == []
    print("expiry passed")


if __name__ == "__main__":
    main()
