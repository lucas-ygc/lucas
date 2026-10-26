"""交付可回放的跟踪控制程序、真实视频入口和分层验收报告，完成课程闭环。"""

import argparse, json, math, time
from pathlib import Path
from tracker import Tracker
from controller import Controller


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sequence", type=Path, default=Path(__file__).with_name("sequence.json")
    )
    parser.add_argument("--output", type=Path, default=Path("runs"))
    args = parser.parse_args()
    source = json.loads(args.sequence.read_text())
    tracker = Tracker(max_age=2)
    controller = Controller(timeout=0.2)
    rows = []
    previous = None
    start = time.perf_counter()
    for frame in source["frames"]:
        timestamp = frame["capture_s"]
        dt = timestamp - previous if previous is not None else 0.1
        if dt <= 0:
            raise ValueError("capture timestamps must increase")
        previous = timestamp
        detections = frame["detections"]
        high = [d for d in detections if d["score"] >= 0.6]
        low = [d for d in detections if 0.1 <= d["score"] < 0.6]
        tracks = tracker.step(high, dt=dt, low=low)
        age = frame["finish_s"] - timestamp
        command = controller.step(tracks, source["width"], dt, age)
        assert (
            math.isfinite(command["speed"])
            and abs(command["speed"]) <= controller.max_speed
        )
        if not detections or age > controller.timeout:
            assert command["speed"] == 0
        if "expected_id" in frame:
            assert command["target_id"] == frame["expected_id"]
        rows.append(
            {
                "frame_id": frame["id"],
                "age_s": age,
                "tracks": tracks,
                "command": command,
            }
        )
    report = {
        "mode": "constructed detection replay",
        "frames": len(rows),
        "checks": "passed",
        "wall_seconds": time.perf_counter() - start,
        "hardware_status": "not measured; no motor commands sent",
        "results": rows,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    print(
        "frames",
        len(rows),
        "checks passed",
        "lost/stale stops",
        sum(r["command"]["reason"] == "stale_or_lost" for r in rows),
    )
    print("report:", args.output / "report.json")


if __name__ == "__main__":
    main()
