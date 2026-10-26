import json
from pathlib import Path


def main():
    rows = json.loads(Path(__file__).with_name("events.json").read_text())
    stale = []
    for row in rows:
        capture, start, finish = row["capture_ms"], row["start_ms"], row["finish_ms"]
        if not capture <= start <= finish:
            raise ValueError("timestamps out of order")
        queue = start - capture
        compute = finish - start
        age = finish - capture
        print(row["id"], "queue/compute/age ms:", queue, compute, age)
        if age > 100:
            stale.append(row["id"])
    assert stale == [2]
    print("constructed stale result:", stale, "not a hardware benchmark")


if __name__ == "__main__":
    main()
