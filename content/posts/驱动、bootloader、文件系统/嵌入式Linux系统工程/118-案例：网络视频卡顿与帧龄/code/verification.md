# 实际运行记录

日期：2026-10-24。环境：Linux x86_64，Python 3.13.9。

方法：仅复制 code.files 清单中的文件到独立临时目录，在其中运行 `python3 main.py`。退出码 0。Shell 文件通过 `sh -n`；C 实验以 `-Wall -Wextra -Werror` 编译（CMake 包采用其工程参数）。

```text
frame=0 queue=2 compute=10 output=3 age=15 ms
frame=1 queue=5 compute=10 output=5 age=20 ms
frame=2 queue=200 compute=10 output=10 age=220 ms
constructed case: compute stays 10 ms while final age reaches 220 ms
```

## 验证边界

Python 3.10+ 标准库；构造时间线，不代表网络或 NPU 实测。

未执行真实板端访问、交叉部署、远程调试、硬件性能和长期可靠性测试。文章中的工具查询与状态变更示例不属于自动运行范围。
