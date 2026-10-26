import math


def main():
    reference, bits = 3.3, 12
    step = reference / (1 << bits)
    assert abs(step - 0.0008056640625) < 1e-12
    sample_rate, frequency = 1000, 800
    alias = abs((frequency + sample_rate / 2) % sample_rate - sample_rate / 2)
    assert alias == 200
    # 800Hz 与 -200Hz 的正弦采样相同；符号反映相位方向。
    a = [math.sin(2 * math.pi * frequency * n / sample_rate) for n in range(20)]
    b = [math.sin(-2 * math.pi * alias * n / sample_rate) for n in range(20)]
    assert max(abs(x - y) for x, y in zip(a, b)) < 1e-12
    print("ideal ADC step mV:", step * 1000, "alias frequency Hz:", alias)


if __name__ == "__main__":
    main()
