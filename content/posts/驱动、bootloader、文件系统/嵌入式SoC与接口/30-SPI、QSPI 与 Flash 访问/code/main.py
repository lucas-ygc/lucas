def clocks(payload_bytes, data_lanes):
    bits = payload_bytes * 8
    if bits % data_lanes:
        raise ValueError("whole data clocks required in this example")
    return 8 + 24 + 8 + bits // data_lanes


def main():
    single, quad = clocks(256, 1), clocks(256, 4)
    assert (single, quad) == (2088, 552)
    print("single/1-1-4 assumed SDR clocks:", single, quad, "ratio", single / quad)
    print("指令、地址和 dummy 仍为本例给定阶段；不是所有器件事务定义")


if __name__ == "__main__":
    main()
