# Linux 资源速查表

| 资源 | 观察入口 | 使用与管理接口 | 常见故障与下一步 |
|---|---|---|---|
| CPU/线程 | /proc/PID/task、/proc/stat、top | pthread、sched、affinity | 热点/等待：分别取执行栈和阻塞证据 |
| 调度约束 | /proc/PID/status、cgroup cpu.stat | 调度策略、cpuset、cpu.max | 空闲仍卡顿：查允许核和父组配额 |
| 用户内存 | status、maps、smaps_rollup | malloc/free、mmap/munmap | 增长：关联对象数、共享页与平台期 |
| 内核内存 | meminfo、slabinfo | 驱动对象生命周期 | 持续增长：查看对象数与错误路径 |
| 连续与媒体内存 | meminfo、reserved-memory、厂商统计 | DMA API、dma-buf、SDK 缓冲池 | 分配失败：查区域、对齐、在途量与释放 |
| 文件句柄 | /proc/PID/fd、limits、file-nr | open/close、dup、CLOEXEC | EMFILE：查句柄类型及关闭配对 |
| 存储 | mounts、diskstats、df、/proc/mtd | 文件系统/块层/MTD/UBI | 慢或只读：查错误、写回与介质状态 |
| 设备绑定 | /sys/bus、driver 链接、日志 | 驱动匹配、probe、资源管理 | 无节点：先查注册与绑定，再查 /dev 管理 |
| MMIO/IRQ | iomem、interrupts、softirqs | 内核 MMIO、IRQ API | 无完成：查提交、通知、清源和后续工作 |
| GPIO/时钟/电源 | gpioinfo、pinctrl/clk/regulator 调试信息 | 各内核资源框架 | 无响应：查复用、供应依赖及 runtime PM |
| 网络 | ip、ss、net/dev、抓包 | socket、路由、过滤规则 | 逐层查链路、邻居、路由、连接及业务 |
| 视频/音频/显示 | V4L2、media-ctl、ALSA、DRM | 各子系统及厂商 SDK | 查协商格式、队列所有权、时钟和呈现 |
| 电源与温度 | cpufreq、devfreq、thermal、power | PM 框架与策略 | 热态降速：对齐温度、频率和持续负载 |
| 故障现场 | 日志、core、pstore、符号产物 | 有界采集和受控调试 | 首错优先，保存精确构建和复现输入 |

这些入口并非每个 BSP 都有；不存在、不可读与数值为零必须分别记录。查询其他进程需相应权限。可写属性不得当普通配置文件盲写。
