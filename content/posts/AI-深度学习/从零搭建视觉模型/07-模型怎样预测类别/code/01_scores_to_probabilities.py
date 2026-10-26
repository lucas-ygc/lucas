"""实验 01：稳定 Softmax、平移不变性和类别选择。"""

import math

from prediction import argmax, softmax


def main():
    examples = [[2, 1], [-4, -5], [102, 101], [1002, 1001]]
    reference = softmax(examples[0])
    for scores in examples:
        probs = softmax(scores)
        print(f"logits={scores} → 概率={[round(p, 4) for p in probs]}"
              f" → 类别索引={argmax(scores)}")
        assert math.isclose(sum(probs), 1.0, abs_tol=1e-12)
        assert all(math.isclose(a, b, abs_tol=1e-12)
                   for a, b in zip(probs, reference))
        assert argmax(scores) == argmax(probs)
    try:
        math.exp(1002)
    except OverflowError:
        print("直接 exp(1002) 溢出；先减最大值的实现正常。")
    assert softmax([0, 0]) == [0.5, 0.5]
    print("全部验证通过；相同分数时本实现取第一个类别。")


if __name__ == "__main__":
    main()
