"""两份副本的教学模型，不模拟真实 cache 指令或 DMA API。"""


class Buffer:
    def __init__(self):
        self.memory = 0
        self.cache = 0
        self.owner = "CPU"

    def cpu_write(self, value):
        if self.owner != "CPU":
            raise RuntimeError("device owns buffer")
        self.cache = value

    def hand_to_device(self):
        self.memory = self.cache
        self.owner = "DEVICE"

    def device_write(self, value):
        if self.owner != "DEVICE":
            raise RuntimeError("CPU owns buffer")
        self.memory = value

    def hand_to_cpu(self):
        self.cache = self.memory
        self.owner = "CPU"


def main():
    buffer = Buffer()
    buffer.cpu_write(42)
    assert buffer.memory == 0
    buffer.hand_to_device()
    assert buffer.memory == 42
    try:
        buffer.cpu_write(99)
    except RuntimeError:
        pass
    else:
        raise AssertionError("ownership check missing")
    buffer.device_write(84)
    assert buffer.cache == 42
    buffer.hand_to_cpu()
    assert buffer.cache == 84
    print(
        "stale memory/cache demonstrated; synchronized ownership result:", buffer.cache
    )


if __name__ == "__main__":
    main()
