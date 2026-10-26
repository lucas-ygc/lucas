class Ring:
    def __init__(self, size):
        self.slots = [{"state": "FREE", "generation": 0} for _ in range(size)]

    def submit(self, index):
        slot = self.slots[index]
        if slot["state"] != "FREE":
            raise RuntimeError("slot still in use")
        slot["state"] = "DEVICE"
        slot["generation"] += 1
        return index, slot["generation"]

    def complete(self, token):
        index, generation = token
        slot = self.slots[index]
        if slot["state"] != "DEVICE" or slot["generation"] != generation:
            raise RuntimeError("stale completion")
        slot["state"] = "CPU"

    def release(self, index):
        if self.slots[index]["state"] != "CPU":
            raise RuntimeError("not ready to release")
        self.slots[index]["state"] = "FREE"


def main():
    ring = Ring(3)
    first = ring.submit(0)
    try:
        ring.submit(0)
    except RuntimeError:
        pass
    else:
        raise AssertionError("overwrote busy slot")
    ring.complete(first)
    ring.release(0)
    second = ring.submit(0)
    assert first != second
    try:
        ring.complete(first)
    except RuntimeError:
        pass
    else:
        raise AssertionError("old completion accepted")
    ring.complete(second)
    ring.release(0)
    print("busy reuse and stale completion rejected; slot:", ring.slots[0])


if __name__ == "__main__":
    main()
