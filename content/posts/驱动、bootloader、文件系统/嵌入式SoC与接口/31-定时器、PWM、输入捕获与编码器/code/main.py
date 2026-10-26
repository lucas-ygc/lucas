def main():
    clock, psc, arr = 72_000_000, 71, 999
    frequency = clock / ((psc + 1) * (arr + 1))
    delta = (10 - 65530) % (1 << 16)
    assert frequency == 1000 and delta == 16
    print("assumed upcounter PWM Hz", frequency, "single-wrap capture ticks", delta)
    print("回绕公式假设间隔小于一次完整计数周期；多次回绕需要额外信息")


if __name__ == "__main__":
    main()
