def main():
    payload = 1920 * 1080 * 30 * 16
    assert payload == 995328000 and payload > 480000000
    print("uncompressed payload Mbit/s", payload / 1e6, "USB2 HS raw line Mbit/s", 480)
    print("有效负载已超过原始线速；缓冲无法补足长期速率缺口")


if __name__ == "__main__":
    main()
