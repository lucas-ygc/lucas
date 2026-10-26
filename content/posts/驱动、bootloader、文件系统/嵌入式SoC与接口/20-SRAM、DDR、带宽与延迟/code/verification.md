# 本地验证记录

日期：2026-10-24。环境：Python 3.13.9，标准库，无第三方依赖。

仅复制 code.files 清单中的文件到独立临时目录，执行 `python3 main.py`，退出码为 0，内置断言通过。

```text
NV12 bytes/frame 3110400 RGB888 bytes/frame 6220800
assumed DDR traffic MB/s 559.872 triple NV12 buffers MB 9.3312
不含 stride、缓存和总线开销；实际硬件可采用不同通路
```

验证范围：构造数据下的机制与计算。未连接开发板，未执行电气测量、真实驱动或性能测试。
