import json
from pathlib import Path

rows = json.loads(Path(__file__).with_name("timeline.json").read_text())
ages = []
for row in rows:
    capture, start, finish, present = (
        row[k] for k in ("capture_ms", "start_ms", "finish_ms", "present_ms")
    )
    if not capture <= start <= finish <= present:
        raise ValueError("timestamps must be in one clock domain and ordered")
    queue, compute, output, age = (
        start - capture,
        finish - start,
        present - finish,
        present - capture,
    )
    ages.append(age)
    print(
        f"frame={row['frame']} queue={queue} compute={compute} output={output} age={age} ms"
    )
assert ages == [15, 20, 220]
print("constructed case: compute stays 10 ms while final age reaches 220 ms")
