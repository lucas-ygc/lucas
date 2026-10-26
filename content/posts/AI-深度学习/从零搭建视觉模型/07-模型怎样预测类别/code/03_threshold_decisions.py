"""实验 03：构造样本上的拒绝决策，不代表真实模型评估。"""

import json

from prediction import predict


def main():
    classes = ["飞机", "汽车"]
    # 所有分数和标签均为人为构造，包含一个高分错误样本。
    samples = [([2, 1], 0), ([1, 2], 1), ([0.1, 0], 1), ([5, 0], 1)]
    expected = {0.0: (4, 2), 0.7: (3, 1), 0.9: (1, 1), 1.0: (0, 0)}
    for threshold in expected:
        print(f"阈值={threshold:.1f}（score >= 阈值时接受）")
        accepted = errors = 0
        for scores, target in samples:
            result = predict(scores, classes, threshold)
            print(json.dumps(result, ensure_ascii=False))
            if result["accepted"]:
                accepted += 1
                errors += result["class_id"] != target
        assert (accepted, errors) == expected[threshold]
        rejection_rate = (len(samples) - accepted) / len(samples)
        error_rate = f"{errors / accepted:.1%}" if accepted else "不适用（无接受样本）"
        print(f"接受={accepted}/{len(samples)}，拒绝率={rejection_rate:.1%}，"
              f"接受样本错误率={error_rate}")
    print("高分也可能预测错误；阈值提高不保证接受样本错误率下降。")


if __name__ == "__main__":
    main()
