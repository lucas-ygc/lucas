def main():
    width, height, fps, depth, lanes = 1920, 1080, 30, 10, 2
    payload = width * height * fps * depth
    ideal_lane = payload / lanes
    illustrative_budget = ideal_lane * 1.2
    ddr = width * height * fps * 2
    assert payload == 622080000 and ideal_lane == 311040000
    print("payload Mbit/s", payload / 1e6, "ideal per-lane Mbit/s", ideal_lane / 1e6)
    print("ASSUMED 20% budget per-lane Mbit/s", illustrative_budget / 1e6)
    print("unpacked 16-bit DDR write MB/s", ddr / 1e6)
    print("20% 不是规范值；最终按 sensor mode 与接收端能力配置")


if __name__ == "__main__":
    main()
