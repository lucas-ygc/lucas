import csv
from pathlib import Path

with Path(__file__).with_name("frames.csv").open(newline="") as stream:
    rows = list(csv.DictReader(stream))
ids = [int(row["frame"]) for row in rows]
held = [int(row["held_buffers"]) for row in rows]
gaps = [(a, b) for a, b in zip(ids, ids[1:]) if b != a + 1]
assert gaps == [(11, 14)] and held == [1, 2, 3, 4]
print("constructed frame gap:", gaps)
print("held buffers:", held)
print(
    "clues only: need source sequence, drop policy and release records to identify cause"
)
