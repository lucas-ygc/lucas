"""自定义模块：这里只定义函数，导入时不运行示例。"""


def pixel_count(width, height):
    return width * height


def main():
    print("直接运行模块:", pixel_count(3, 2))


if __name__ == "__main__":
    main()
