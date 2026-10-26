# 实际运行记录

日期：2026-10-24。环境：Linux x86_64；主机 cc，ASan 与 UBSan。

执行 `sh run.sh`。脚本在独立临时目录构建并运行，使用本课 main.c，退出码 0。

```text
empty, boundary and oversized input checked; no intentional invalid memory access
```

## 环境差异

首次沙箱内执行失败：LeakSanitizer 报告不支持当前 ptrace 环境。随后经允许，在沙箱外执行同一个 run.sh，通过且未关闭任何 sanitizer 检查。此课使用源目录输入、临时构建目录；其余实验采用 code.files 文件复制到独立目录的方法。

## 验证边界

验证了空输入、边界长度和超长输入被拒绝的三个路径。没有故意触发非法内存访问，未做真实板端、交叉工具链或任意输入的完整验证。
