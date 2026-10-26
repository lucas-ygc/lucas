"""A/B 状态演示；布尔校验标记不是密码学验证。"""

import copy


def boot(state):
    pending = state["pending"]
    if pending is not None:
        if state["valid"][pending] and state["tries"] > 0:
            state["tries"] -= 1
            return pending
        state["pending"] = None
    return state["confirmed"]


def main():
    initial = {
        "confirmed": "A",
        "pending": None,
        "valid": {"A": True, "B": False},
        "tries": 0,
    }
    writing = copy.deepcopy(initial)
    assert boot(writing) == "A"
    staged = copy.deepcopy(initial)
    staged["valid"]["B"] = True
    assert boot(copy.deepcopy(staged)) == "A"
    staged.update(pending="B", tries=2)
    failure = copy.deepcopy(staged)
    assert [boot(failure) for _ in range(3)] == ["B", "B", "A"]
    success = copy.deepcopy(staged)
    assert boot(success) == "B"
    success.update(confirmed="B", pending=None)
    assert boot(success) == "B"
    print(
        "incomplete write: A; uncommitted candidate: A; two failed trials: B B A; confirmed: B"
    )
    print("真实系统还需原子元数据、签名、防回滚及掉电验证")


if __name__ == "__main__":
    main()
