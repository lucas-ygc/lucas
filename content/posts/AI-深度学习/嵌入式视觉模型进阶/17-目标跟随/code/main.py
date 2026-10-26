"""实现目标锁定、死区、限速和失效停止，分离视觉输出与电机驱动。"""

from controller import Controller


def row(x, ident=1, matched=True):
    return {"id": ident, "box": [x, 0, x + 20, 20], "matched": matched}


def main():
    controller = Controller()
    commands = []
    for x in [70, 65, 60, 45]:
        out = controller.step([row(x)], 100, 0.05, 0.02)
        commands.append(out["speed"])
        print(out)
    assert all(abs(v) <= 0.6 for v in commands)
    assert all(abs(a - b) <= 0.100001 for a, b in zip([0] + commands, commands))
    stopped = controller.step([row(70)], 100, 0.05, 0.3)
    assert stopped["speed"] == 0
    lost = controller.step([row(70, 2)], 100, 0.05, 0.02)
    assert lost["speed"] == 0 and lost["target_id"] == 1
    controller.release()
    assert controller.step([row(70, 2)], 100, 0.05, 0.02)["target_id"] == 2
    print("stale stop, identity lock and explicit reacquisition passed")


if __name__ == "__main__":
    main()
