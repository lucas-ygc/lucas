"""输出归一化角速度意图，不直接驱动电机。"""

import math


class Controller:
    def __init__(
        self, kp=1.2, deadzone=0.05, max_speed=0.6, max_accel=2.0, timeout=0.2
    ):
        self.kp = kp
        self.deadzone = deadzone
        self.max_speed = max_speed
        self.max_accel = max_accel
        self.timeout = timeout
        self.previous = 0.0
        self.target = None

    def step(self, rows, width, dt, age):
        if (
            width <= 0
            or dt <= 0
            or not all(math.isfinite(v) for v in [width, dt, age])
            or age < 0
        ):
            raise ValueError("invalid timing or dimensions")
        visible = [r for r in rows if r["matched"]]
        chosen = next((r for r in visible if r["id"] == self.target), None)
        if chosen is None and self.target is None and visible:
            chosen = min(
                visible, key=lambda r: abs((r["box"][0] + r["box"][2]) / 2 - width / 2)
            )
            self.target = chosen["id"]
        if age > self.timeout or chosen is None:
            self.previous = 0.0
            return {"target_id": self.target, "speed": 0.0, "reason": "stale_or_lost"}
        center = (chosen["box"][0] + chosen["box"][2]) / 2
        error = (center - width / 2) / (width / 2)
        desired = (
            0.0
            if abs(error) <= self.deadzone
            else max(-self.max_speed, min(self.max_speed, self.kp * error))
        )
        delta = self.max_accel * dt
        speed = max(self.previous - delta, min(self.previous + delta, desired))
        self.previous = speed
        return {"target_id": self.target, "speed": speed, "reason": "tracking"}

    def release(self):
        self.target = None
        self.previous = 0.0
