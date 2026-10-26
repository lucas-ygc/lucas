"""十进制单位，忽略重叠细节的资源下界，不是芯片实测。"""


def bounds(operations, bytes_moved, ops_per_second, bytes_per_second):
    if min(operations, bytes_moved) < 0 or min(ops_per_second, bytes_per_second) <= 0:
        raise ValueError("invalid workload or rate")
    compute = operations / ops_per_second
    transfer = bytes_moved / bytes_per_second
    return compute, transfer, max(compute, transfer)


def main():
    compute, transfer, lower = bounds(1e9, 100e6, 1e12, 5e9)
    assert compute == 0.001 and transfer == 0.02 and lower == 0.02
    print(
        "compute/transfer/optimistic lower bound ms:",
        compute * 1000,
        transfer * 1000,
        lower * 1000,
    )
    assert bounds(1e9, 100e6, 2e12, 5e9)[2] == lower
    print("doubling compute peak does not reduce this transfer bound")


if __name__ == "__main__":
    main()
