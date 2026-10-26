"""结构、参数与一次推理。运行方式与练习见 README.md。"""
classes = ['airplane', 'automobile']
# 构造的两个特征：天空比例、轮子响应；不是训练得到的视觉特征。
features = [0.8, 0.1]
weights = [[2.0, -1.0], [-1.0, 2.0]]
def predict(x, w):
    scores = [sum(a*b for a,b in zip(row,x)) for row in w]
    return scores, classes[max(range(len(scores)), key=scores.__getitem__)]
scores, name = predict(features, weights)
print('features:', features, 'scores:', scores, 'class:', name)
assert name == 'airplane'
changed = list(reversed(weights))
assert predict(features, changed)[1] == 'automobile'
print('同样的结构，更换参数后:', predict(features, changed))
