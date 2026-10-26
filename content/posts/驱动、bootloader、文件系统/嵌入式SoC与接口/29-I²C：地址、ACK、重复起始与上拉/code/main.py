import math


def main():
    address = 0x36
    write = address << 1
    read = write | 1
    assert (write, read) == (0x6C, 0x6D)
    resistance, capacitance = 4700, 100e-12
    # 理想一阶 RC 从 30% 上升到 70%，不是整套 I2C 电气认证。
    rise = math.log(0.7 / 0.3) * resistance * capacitance
    print("7-bit address", hex(address), "write/read bytes", hex(write), hex(read))
    print("assumed 4.7kohm / 100pF 30%-70% rise ns:", rise * 1e9)
    assert 398 < rise * 1e9 < 399
    print("需另核对模式限值、灌电流、总线负载与实际波形")


if __name__ == "__main__":
    main()
