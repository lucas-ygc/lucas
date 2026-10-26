"""离线 W1C 模型，不访问 MMIO。"""


def write_one_to_clear(status, written):
    return status & ~written


def main():
    original = 0b101
    intended = write_one_to_clear(original, 0b001)
    accidental = write_one_to_clear(original, original)
    assert intended == 0b100 and accidental == 0
    print(
        "status",
        bin(original),
        "clear bit0",
        bin(intended),
        "write back read value",
        bin(accidental),
    )


if __name__ == "__main__":
    main()
