import csv
from pathlib import Path

with Path(__file__).with_name("resources.csv").open(newline="") as stream:
    rows = [{k: int(v) for k, v in row.items()} for row in csv.DictReader(stream)]
fd_delta = rows[-1]["fd_count"] - rows[0]["fd_count"]
cycles = rows[-1]["cycle"] - rows[0]["cycle"]
rss_span = max(x["rss_kib"] for x in rows) - min(x["rss_kib"] for x in rows)
assert fd_delta == 6 and cycles == 3 and rss_span == 4
print("constructed fd growth per cycle:", fd_delta / cycles)
print("RSS span KiB:", rss_span)
print(
    "next evidence: classify /proc/PID/fd targets and trace open/close; trend alone is not proof"
)
