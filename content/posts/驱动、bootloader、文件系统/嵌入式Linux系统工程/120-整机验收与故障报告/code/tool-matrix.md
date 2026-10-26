# 工具与环境适用表

| 环境 | 常见可用入口 | 需要确认的条件 | 缺失时的替代 |
|---|---|---|---|
| BusyBox BSP | Shell、基础 ps/top、/proc、/sys | applet 与选项按实际构建 | 读固定 proc 项，交叉编译所需工具 |
| systemd 发行版 | systemctl、journalctl | PID 1 和日志策略确为 systemd | 查看实际 init 脚本及文件日志 |
| Buildroot | 构建配置、自有包、overlay | 工具是可选包，内核独立配置 | 加入正式工程输入后重建 |
| Yocto | layer、recipe、image、SDK | 分支、MACHINE、DISTRO 和版本匹配 | 查展开变量和任务日志 |
| 容器 | 容器自身 /proc、挂载、网络视图 | namespace、capability、设备策略 | 在受控宿主采集对应视图 |
| strace/GDB | 用户程序调试 | ptrace 权限、符号及架构 | 应用错误日志、离线 core 分析 |
| perf | CPU 事件和采样 | PMU、配置、权限和符号 | 时间戳、用户态 profiling、tracepoints |
| ftrace | 内核事件/函数 | tracefs、配置、权限、缓冲 | 限量内核日志、应用埋点 |
| eBPF | 事件统计和动态观测 | 程序类型、helper、BTF、加载权限 | 已有 tracepoint 或用户态观测 |
| 硬件测量 | 波形、链路、电源证据 | 仪器、接法、带宽和额定范围 | 只能标未测，软件模型不能替代 |

不要把 GNU 命令选项直接套给 BusyBox。工具的 --help 与版本输出优先于照抄网页；内核文档也应切到目标 BSP 对应版本核对。
