---
title: uboot-fuhan 
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux驱动学习
abbrlink: 9efdaa58
typora-root-url: ./..\..\..
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---

flash采用emmc

# mmc 开启
mmc硬件连接的SD1接口；include/configs/fh8856V500.h 中开启SD1即可。

查看.config 配置和 u-boot.cfg 配置，关于mmc的配置开启。



# uboot环境变量保存位置
修改borad.c，返回设备序号即可。

# 环境变量保存地址
```c
#define EMMC_ENV_OFFSET      0x20000
#define CONFIG_CMD_MMC
#define CONFIG_ENV_IS_IN_MMC
#define CONFIG_SYS_MMC_ENV_DEV 0
#define CONFIG_SYS_MMC_ENV_PART 1
```

