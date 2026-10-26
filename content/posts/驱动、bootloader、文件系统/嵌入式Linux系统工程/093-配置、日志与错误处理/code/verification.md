# 实际运行记录

日期：2026-10-24。环境：Linux x86_64，Python 3.13.9。

方法：仅复制 code.files 清单中的文件到独立临时目录，在其中运行 `sh run.sh`。退出码 0。Shell 文件通过 `sh -n`；C 实验以 `-Wall -Wextra -Werror` 编译（CMake 包采用其工程参数）。

```text
valid=16; empty, zero, negative, suffix, bound and overflow rejected
```

## 验证边界

主机 Linux 的有界 C 实验；不访问真实外设，不代表板端时序或性能。

未执行真实板端访问、交叉部署、远程调试、硬件性能和长期可靠性测试。文章中的工具查询与状态变更示例不属于自动运行范围。
