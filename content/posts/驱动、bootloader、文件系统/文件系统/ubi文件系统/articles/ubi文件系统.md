---
title: UBI 文件系统空间分配详解
categories: 驱动、bootloader、文件系统
tags: ubi 文件系统
date: 2023-09-13 00:00:00
abbrlink: d9538d63
cover: "../images/封面.png"
---

## 9MB MTD分区空间分配详解

### 1. 物理分区概况
```
MTD分区大小: 0x00900000 = 9,437,184 字节 ≈ 9MB
擦除块大小: 0x00020000 = 131,072 字节 = 128KB
总擦除块数: 9,437,184 / 131,072 = 72 个PEB
```

### 2. UBI层空间分配

当使用 [ubinize](file:///home/tuling/project/tuling/EC2K_Rel_and_SDK/EC2K_Rel/pack/EC2KR/_build/ubinize) 创建UBI镜像时，空间按以下方式分配：

#### UBI元数据开销
