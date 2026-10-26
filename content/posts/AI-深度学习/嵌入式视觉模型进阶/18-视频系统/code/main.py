"""用离散事件回放解释吞吐、帧龄、丢帧和结果顺序。"""

import math


def simulate(latest, service=50):
    arrivals = list(range(0, 3300, 33))
    i = 0
    now = 0
    latencies = []
    dropped = 0
    while i < len(arrivals):
        now = max(now, arrivals[i])
        chosen = i
        if latest:
            while chosen + 1 < len(arrivals) and arrivals[chosen + 1] <= now:
                chosen += 1
        dropped += chosen - i
        now += service
        latencies.append(now - arrivals[chosen])
        i = chosen + 1
    return {
        "processed": len(latencies),
        "dropped": dropped,
        "p95_ms": sorted(latencies)[math.ceil(0.95 * len(latencies)) - 1],
        "last_finish_ms": now,
    }


def main():
    fifo = simulate(False)
    latest = simulate(True)
    print("FIFO", fifo, "latest slot", latest)
    assert (
        latest["p95_ms"] < fifo["p95_ms"]
        and latest["processed"] + latest["dropped"] == 100
    )
    assert simulate(False, 20) == simulate(True, 20)
    print("fast service has no queue-policy difference")


if __name__ == "__main__":
    main()
