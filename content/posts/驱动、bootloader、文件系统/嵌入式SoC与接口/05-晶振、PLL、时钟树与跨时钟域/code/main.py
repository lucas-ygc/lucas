"""只计算理想时钟比例，不代表任何 PLL 的合法配置。"""

from fractions import Fraction


def main():
    reference = 24_000_000
    multiplier = 50
    divider = 4
    output = Fraction(reference * multiplier, divider)
    assert output == 300_000_000
    print("ideal output Hz:", output, "period ns:", float(Fraction(10**9, output)))
    print("还需核对参考/VCO/输出范围、锁定和切换规则")


if __name__ == "__main__":
    main()
