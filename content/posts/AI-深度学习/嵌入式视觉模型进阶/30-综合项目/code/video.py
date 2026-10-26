"""本地视频/摄像头 + YOLOv8 ONNX + 跟踪 + 控制意图，只写日志，不驱动电机。"""

import argparse, json, time, math
from pathlib import Path
import cv2
import onnxruntime as ort
from detector import preprocess, decode
from tracker import Tracker
from controller import Controller


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--video", type=Path)
    source.add_argument("--camera", type=int)
    parser.add_argument("--classes", type=int, required=True)
    parser.add_argument("--output", type=Path, default=Path("runs-video"))
    parser.add_argument("--max-frames", type=int, default=300)
    args = parser.parse_args()
    if args.classes < 1 or args.max_frames < 1:
        parser.error("positive classes/max-frames required")
    session = ort.InferenceSession(str(args.model), providers=["CPUExecutionProvider"])
    inputs = session.get_inputs()
    if len(inputs) != 1 or len(session.get_outputs()) != 1:
        raise ValueError("one input/output required")
    inp = inputs[0]
    if (
        inp.type != "tensor(float)"
        or len(inp.shape) != 4
        or inp.shape[:2] != [1, 3]
        or not isinstance(inp.shape[2], int)
        or inp.shape[2] != inp.shape[3]
    ):
        raise ValueError("static FP32 [1,3,S,S] expected")
    cap = cv2.VideoCapture(str(args.video) if args.video else args.camera)
    if not cap.isOpened():
        raise RuntimeError("cannot open input")
    fps = cap.get(cv2.CAP_PROP_FPS)
    if args.video and (not math.isfinite(fps) or fps <= 0):
        cap.release()
        raise ValueError("video FPS unavailable; use explicit timestamped replay")
    tracker = Tracker()
    controller = Controller()
    previous = None
    args.output.mkdir(parents=True, exist_ok=True)
    count = 0
    try:
        with (args.output / "frames.jsonl").open("w") as log:
            for frame_id in range(args.max_frames):
                start = time.monotonic()
                ok, image = cap.read()
                if not ok:
                    break
                timestamp = frame_id / fps if args.video else time.monotonic()
                dt = (
                    timestamp - previous
                    if previous is not None
                    else (1 / fps if math.isfinite(fps) and fps > 0 else 0.033)
                )
                previous = timestamp
                x, meta = preprocess(image, inp.shape[2])
                raw = session.run(None, {inp.name: x})[0]
                detections = decode(raw, meta, args.classes, score=0.1)
                tracks = tracker.step(
                    [d for d in detections if d["score"] >= 0.6],
                    dt=max(dt, 1e-6),
                    low=[d for d in detections if 0.1 <= d["score"] < 0.6],
                )
                elapsed = time.monotonic() - start
                command = controller.step(
                    tracks, image.shape[1], max(dt, 1e-6), elapsed
                )
                log.write(
                    json.dumps(
                        {
                            "frame_id": frame_id,
                            "media_time_s": timestamp,
                            "local_processing_s": elapsed,
                            "tracks": tracks,
                            "command": command,
                        }
                    )
                    + "\n"
                )
                count += 1
            log.write(
                json.dumps(
                    {
                        "event": "end",
                        "command": {"speed": 0, "reason": "input_end"},
                        "motor_io": False,
                    }
                )
                + "\n"
            )
    finally:
        cap.release()
    print(
        "processed frames",
        count,
        "no motor I/O; local processing excludes sensor buffering",
    )


if __name__ == "__main__":
    main()
