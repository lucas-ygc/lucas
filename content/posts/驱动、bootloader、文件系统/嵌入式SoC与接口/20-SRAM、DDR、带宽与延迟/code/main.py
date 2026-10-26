from fractions import Fraction


def main():
    width, height, fps = 1920, 1080, 30
    nv12 = width * height * Fraction(3, 2)
    rgb = width * height * 3
    # 明确假设：ISP 写 NV12；转换读 NV12/写 RGB；NPU 读 RGB。
    traffic = (nv12 * 2 + rgb * 2) * fps
    assert nv12 == 3110400 and rgb == 6220800
    assert traffic == 559872000
    print("NV12 bytes/frame", int(nv12), "RGB888 bytes/frame", rgb)
    print(
        "assumed DDR traffic MB/s",
        float(traffic / 10**6),
        "triple NV12 buffers MB",
        float(nv12 * 3 / 10**6),
    )
    print("不含 stride、缓存和总线开销；实际硬件可采用不同通路")


if __name__ == "__main__":
    main()
