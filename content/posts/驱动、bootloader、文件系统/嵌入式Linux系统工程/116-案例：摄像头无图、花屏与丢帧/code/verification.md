# 实际运行记录

日期：2026-10-24。环境：Linux x86_64，Python 3.13.9。

方法：仅复制 code.files 清单中的文件到独立临时目录，在其中运行 `python3 main.py`。退出码 0。Shell 文件通过 `sh -n`；C 实验以 `-Wall -Wextra -Werror` 编译（CMake 包采用其工程参数）。

```text
constructed frame gap: [(11, 14)]
held buffers: [1, 2, 3, 4]
clues only: need source sequence, drop policy and release records to identify cause
```

## 验证边界

Python 标准库；构造帧序号和持有量，未接入摄像头。

未执行真实板端访问、交叉部署、远程调试、硬件性能和长期可靠性测试。文章中的工具查询与状态变更示例不属于自动运行范围。
