# strace 定位系统调用问题

## 范围与环境

主机 Linux 的有界 C 实验；不访问真实外设，不代表板端时序或性能。

C 示例需要 Linux、C11 编译器和 libc/pthread 开发文件；Shell 使用 POSIX sh、mktemp 及基础工具；Python 示例仅用 Python 3.10+ 标准库。具体以本包文件类型为准。

## 运行

解压后进入本目录：

```sh
sh run.sh
```

C 的 run.sh 在新建临时目录编译和运行并清理自己的临时产物；默认使用 cc，可用 CC 指定兼容编译器的可执行文件路径。交叉编译出的程序必须在匹配目标运行，不能直接由主机 run.sh 执行。所有结果以 verification.md 为准，本文的板端工具命令不由实验脚本自动执行。

## 练习

对 pipe 示例跟踪 read、write 和 close，解释 EOF 出现条件。参考结论：关闭写端后 read=0 是正常结束，与 EAGAIN、EINTR 不同。 配套 run.sh 仅编译并运行被跟踪程序，strace 能力另行检查。

## 参考分析

strace 显示 read 持续阻塞，需要确认预期输入和所有写端；若频繁返回 EAGAIN 且 CPU 高，则可能忙轮询。相同“读不到数据”现象有不同修复方向。

需要手动调试时先 `sh build-debug.sh`，然后按文章运行 strace 或 GDB；这会在本目录生成 demo，默认 run.sh 不调用调试器。
