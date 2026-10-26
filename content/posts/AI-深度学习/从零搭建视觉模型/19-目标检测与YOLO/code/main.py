"""IoU、NMS 与坐标还原。运行方式与练习见 README.md。"""
def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0, x2-x1) * max(0, y2-y1)
    area_a = max(0, a[2]-a[0]) * max(0, a[3]-a[1])
    area_b = max(0, b[2]-b[0]) * max(0, b[3]-b[1])
    union = area_a + area_b - intersection
    return intersection / union if union else 0.0

first = [0, 0, 10, 10]
second = [5, 0, 15, 10]
print(iou(first, second))
assert abs(iou(first, second) - 1/3) < 1e-12

# 按类别执行贪心 NMS，输入为 (框, 分数, 类别)。
candidates = [(first,0.9,0),([1,0,11,10],0.8,0),(first,0.7,1)]
kept = []
for box,score,label in sorted(candidates,key=lambda row:row[1],reverse=True):
    if all(label!=other_label or iou(box,other)<=0.5 for other,_,other_label in kept):
        kept.append((box,score,label))
assert len(kept)==2
print('NMS kept:',kept)
# 640x360 -> 640x640：上下各补 140，缩放比例 1。
original = [100,50,200,150]
padded = [100,190,200,290]
restored = [padded[0],padded[1]-140,padded[2],padded[3]-140]
assert restored==original
print('restored:',restored)
