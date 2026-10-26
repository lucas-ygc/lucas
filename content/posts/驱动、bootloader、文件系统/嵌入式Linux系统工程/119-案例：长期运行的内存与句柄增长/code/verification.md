# 实际运行记录

日期：2026-10-24。环境：Linux x86_64，Python 3.13.9。

方法：仅复制 code.files 清单中的文件到独立临时目录，在其中运行 `python3 main.py`。退出码 0。Shell 文件通过 `sh -n`；C 实验以 `-Wall -Wextra -Werror` 编译（CMake 包采用其工程参数）。

```text
constructed fd growth per cycle: 2.0
RSS span KiB: 4
next evidence: classify /proc/PID/fd targets and trace open/close; trend alone is not proof
```

## 验证边界

Python 标准库；分析构造趋势，不声称发现真实进程泄漏。

未执行真实板端访问、交叉部署、远程调试、硬件性能和长期可靠性测试。文章中的工具查询与状态变更示例不属于自动运行范围。
