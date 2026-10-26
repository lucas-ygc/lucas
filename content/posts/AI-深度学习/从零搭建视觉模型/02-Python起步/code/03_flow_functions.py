"""缩进、条件、循环、函数、默认参数与关键字参数。"""


def scale_pixel(value, maximum=255):
    if maximum <= 0:
        raise ValueError("maximum 必须大于 0")
    return value / maximum


values = [0, 128, 255]
scaled = []
for value in values:
    scaled.append(scale_pixel(value))
print("缩放结果:", scaled)

for index in range(3):
    print(f"第 {index} 个值: {values[index]}")

# enumerate 同时给出下标和值。
for index, value in enumerate(values):
    if value == 0:
        print(f"values[{index}] 是最小值")
    elif value == 255:
        print(f"values[{index}] 是最大值")
    else:
        print(f"values[{index}] 是中间值")

print("关键字参数:", scale_pixel(value=128, maximum=255))
print("另一个数值范围:", scale_pixel(512, maximum=1023))

# 有意触发并捕获一个错误，观察错误信息，脚本仍能正常结束。
try:
    scale_pixel(128, maximum=0)
except ValueError as error:
    print("捕获到错误:", error)
