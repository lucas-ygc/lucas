def serial_seconds(byte_count, baud, data_bits=8, parity_bits=0, stop_bits=1):
    if byte_count < 0 or baud <= 0:
        raise ValueError("invalid size or baud")
    return byte_count * (1 + data_bits + parity_bits + stop_bits) / baud


def main():
    duration = serial_seconds(256, 115200)
    assert abs(duration - 0.022222222222222223) < 1e-12
    print("256 bytes 115200 8N1 ideal wire ms:", duration * 1000)
    print("未包含字节间隔、RS-485 转向和应用等待；DMA 完成不等于尾停止位已出线")


if __name__ == "__main__":
    main()
