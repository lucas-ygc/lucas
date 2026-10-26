"""实验 02：逐行预测和类别映射；列表模拟 [N, C] 张量。"""

import math

from prediction import argmax, softmax


def main():
    classes = ["飞机", "汽车", "轮船"]
    batch = [[3, 1, 0], [0, 2, 1]]
    print("输出形状 [N, C] = [2, 3]：两张图片，每张三个类别")
    predictions = []
    for row, scores in enumerate(batch):
        probs = softmax(scores)
        index = argmax(scores)
        predictions.append(index)
        print(f"图片 {row}：概率={[round(p, 4) for p in probs]}，"
              f"class_id={index}，class_name={classes[index]}")
        assert math.isclose(sum(probs), 1.0, abs_tol=1e-12)
    assert predictions == [0, 1]
    wrong_classes = ["汽车", "飞机", "轮船"]
    print("类别顺序写反后：", [wrong_classes[i] for i in predictions])
    print("分数和索引没变，名称却错了；推理必须保留训练时的类别顺序。")
    wrong_axis = [argmax(column) for column in zip(*batch)]
    print("错误地沿图片轴取最大值：", wrong_axis)
    print("得到的是每类在哪张图片上分数最高，并非每张图片的类别。")
    assert wrong_axis == [0, 1, 1]


if __name__ == "__main__":
    main()
