def main():
    total_width, total_height, refresh = 2200, 1125, 60
    clock = total_width * total_height * refresh
    assert clock == 148500000
    print("example pixel clock MHz", clock / 1e6)
    print("仅给定扫描时序的算术；面板、桥接和 PHY 需分别核对")


if __name__ == "__main__":
    main()
