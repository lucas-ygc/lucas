# 进程生命周期与状态

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

运行 fork/wait 示例，观察父进程取得退出码 7。参考结论：退出状态由父进程通过 wait 系列接口读取，不能直接把 wait 返回值当退出码。

## 参考分析

父进程用 waitpid 得到的是子进程 PID，真正退出原因在 status 中。WIFEXITED 为真才能读取 WEXITSTATUS；被信号终止时应按 WIFSIGNALED 分支解释，避免把编码后的状态误当业务返回值。
