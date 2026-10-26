# 交叉编译、sysroot 与 pkg-config

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

运行独立 hello 构建，再用 readelf 检查架构和解释器。参考结论：能在主机运行只验证本机构建，不代表已完成交叉部署。

## 参考分析

pkg-config 输出主机绝对路径时，检查 PKG_CONFIG_LIBDIR 和 PKG_CONFIG_SYSROOT_DIR 等配置，并查看工具链包装器。只改 CC 变量不保证其他构建探测和依赖路径已经切到目标。
