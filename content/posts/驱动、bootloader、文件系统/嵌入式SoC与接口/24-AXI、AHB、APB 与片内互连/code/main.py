def main():
    valid = [1, 1, 1, 0, 1, 1]
    ready = [0, 1, 0, 1, 1, 1]
    transfers = [i for i, (v, r) in enumerate(zip(valid, ready)) if v and r]
    stalls = [i for i, (v, r) in enumerate(zip(valid, ready)) if v and not r]
    assert transfers == [1, 4, 5] and stalls == [0, 2]
    print("accepted cycles", transfers, "backpressure cycles", stalls)
    print("64-bit / 200MHz ideal GB/s:", 64 / 8 * 200e6 / 1e9)


if __name__ == "__main__":
    main()
