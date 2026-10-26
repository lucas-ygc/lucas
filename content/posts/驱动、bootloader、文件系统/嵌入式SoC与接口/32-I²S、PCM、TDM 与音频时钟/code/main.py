def main():
    fs, slot_width = 48000, 32
    stereo = fs * slot_width * 2
    tdm = fs * slot_width * 8
    assert stereo == 3072000 and tdm == 12288000
    print("stereo BCLK Hz", stereo, "8-slot TDM BCLK Hz", tdm)
    print("按槽宽计算；24 位有效样本也可占 32 位槽")


if __name__ == "__main__":
    main()
