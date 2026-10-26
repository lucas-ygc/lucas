# 实际运行记录

日期：2026-10-24。环境：Linux x86_64，Python 3.13.9。

方法：仅复制 code.files 清单中的文件到独立临时目录，在其中运行 `python3 main.py`。退出码 0。Shell 文件通过 `sh -n`；C 实验以 `-Wall -Wextra -Werror` 编译（CMake 包采用其工程参数）。

```text
root-device-or-filesystem: inspect root=, storage driver, partition and fs support
init-execution: inspect init path, permissions, ELF, interpreter and libraries
unknown: retain full log and last confirmed boot stage
```

## 验证边界

Python 标准库；仅对三行构造日志分类线索，未知信息保持 unknown。

未执行真实板端访问、交叉部署、远程调试、硬件性能和长期可靠性测试。文章中的工具查询与状态变更示例不属于自动运行范围。
