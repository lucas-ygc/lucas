# 本地验证记录

日期：2026-10-24。环境：Python 3.13.9，标准库，无第三方依赖。

仅复制 code.files 清单中的文件到独立临时目录，执行 `python3 main.py`，退出码为 0，内置断言通过。

```text
uncompressed payload Mbit/s 995.328 USB2 HS raw line Mbit/s 480
有效负载已超过原始线速；缓冲无法补足长期速率缺口
```

验证范围：构造数据下的机制与计算。未连接开发板，未执行电气测量、真实驱动或性能测试。
