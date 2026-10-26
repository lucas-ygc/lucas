"""变量、类型、输出，以及与 C/C++ 不同的除法。"""

width = 3
height = 2
name = "sample.ppm"
is_rgb = True

print("文件:", name)
print(f"宽={width}, 高={height}, 像素数={width * height}")
print("width 的类型:", type(width).__name__)
print("is_rgb:", is_rgb)

# / 是除法；// 是向下取整除法。负数时尤其要注意区别。
print("5 / 2 =", 5 / 2)
print("5 // 2 =", 5 // 2)
print("-5 // 2 =", -5 // 2)

# 名字可以重新绑定到另一种类型的对象，不等于对象没有类型。
value = 255
print("value:", value, type(value).__name__)
value = "255"
print("value:", value, type(value).__name__)
print("转回整数再加 1:", int(value) + 1)
