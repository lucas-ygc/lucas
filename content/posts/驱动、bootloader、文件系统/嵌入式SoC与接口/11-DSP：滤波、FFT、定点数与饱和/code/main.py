import math, cmath


def saturate_q15(value):
    return max(-32768, min(32767, value))


def fir(values, coefficients):
    return [
        sum(
            coefficient * values[n - k]
            for k, coefficient in enumerate(coefficients)
            if n >= k
        )
        for n in range(len(values))
    ]


def main():
    values = [0.0] * 4 + [1.0] * 8
    filtered = fir(values, [0.25] * 4)
    assert filtered[4:8] == [0.25, 0.5, 0.75, 1.0]
    raw = 24576 + 24576
    saturated = saturate_q15(raw) / 32768
    wrapped = ((raw + 32768) % 65536 - 32768) / 32768
    assert saturated == 32767 / 32768 and wrapped == -0.5
    count = 64
    signal = [math.sin(2 * math.pi * 8 * n / count) for n in range(count)]
    # 小规模直接 DFT 是频谱计算参考，不是快速 FFT 实现。
    spectrum = [
        abs(
            sum(
                value * cmath.exp(-2j * math.pi * k * n / count)
                for n, value in enumerate(signal)
            )
        )
        for k in range(count // 2)
    ]
    peak = max(range(len(spectrum)), key=spectrum.__getitem__)
    assert peak == 8
    print(
        "step response:",
        filtered,
        "Q15 saturation/wrap:",
        saturated,
        wrapped,
        "DFT peak bin:",
        peak,
    )


if __name__ == "__main__":
    main()
