"""列表、元组、字典、切片，以及赋值不自动复制列表。"""

rgb = [255, 128, 0]
size = (3, 2)
info = {"width": 3, "height": 2, "mode": "RGB"}

print("R 通道:", rgb[0])
print("最后一个通道:", rgb[-1])
print("前两个通道:", rgb[:2])
width, height = size
print(f"元组解包: width={width}, height={height}")
print("字典里的模式:", info["mode"])

# 与 C++ 的 vector 值拷贝不同，两个名字指向同一个列表。
alias = rgb
alias[0] = 100
print("修改 alias 后的 rgb:", rgb)
print("是否同一个对象:", alias is rgb)

copied = rgb.copy()
copied[0] = 50
print("修改副本后的 rgb:", rgb)
print("副本:", copied)

# 这是浅拷贝；嵌套列表内部的对象仍然共享。
rows = [[1, 2], [3, 4],[5,6]]
rows_copy = rows.copy()
rows_copy[0][0] = 9
print("嵌套列表浅拷贝:", rows)
print("修改后的 rows_copy:", rows_copy)

rows_copy[0] = 9
print("修改 rows_copy[0] 后的 rows:", rows_copy)