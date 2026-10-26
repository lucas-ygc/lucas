---
title: uboot移植（uboot2024.4移植）
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux驱动学习
abbrlink: 4d7a5285
typora-root-url: ./..\..\..
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---



imx6ull板子为例：
下载源码：https://github.com/nxp-imx/uboot-imx/tree/lf_v2024.04
注意设备树的语法最后要空行
# 1、编译
拿到源码后，先编译一遍和自己要移植的板子所用的芯片匹配的配置文件。如我这里用的是imx6ull的板子，就需要编译imx6ull的配置文件。
`编译过后，需要改的目录下生成了一些文件，可以按照文件去判定编译的配置文件是否和自己板子匹配。`
```shell
#!/bin/bash
path="arm CROSS_COMPILE=/home/ygc/Desktop/linux-gcc/2021-6ull/gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-"
make ARCH=arm CROSS_COMPILE=${path} distclean
make ARCH=arm CROSS_COMPILE=${path} menuconfig
make ARCH=arm CROSS_COMPILE=${path} mx6ull_14x14_naro_emmc_defconfig
#make ARCH=arm CROSS_COMPILE=${path} mx6ull_14x14_evk_emmc_defconfig
make V=1 ARCH=arm CROSS_COMPILE=${path} -j12

#make ARCH=arm CROSS_COMPILE=arm-none-linux-gnueabihf- savedefconfig #生成配置文件 与之前的配置文件相比较，看哪些配置变了
#path 为自己的编译器路径
```
# 2、查看u-boot.map文件
编译完成后，会在u-boot-2024.04/build/目录下生成u-boot.bin文件，这个文件就是我们最终要烧写的文件。
查看uboot.map文件，可以知道参与编译的文件。

# 3、烧写到板子上
烧写到板子上，观察有无打印，没打印的，需要检查是否编译的配置文件和自己板子匹配。
一般串口优先使用原厂的串口，如果不行，再尝试其他的串口。

# 4、修改配置文件
将配置文件改为自己的配置文件。mx6ull_14x14_emmc_naro_defconfig、改为自己的配置文件，如mx6ull_14x14_naro_emmc_defconfig。文件存在于uboot/configs/目录下。

这个文件中主要改这几条：

* 第一条：设备树的名字
```config
CONFIG_DEFAULT_DEVICE_TREE="imx6ull-14x14-evk-emmc"
```
改为:
```config
CONFIG_DEFAULT_DEVICE_TREE="imx6ull-14x14-naro-emmc"
```

* 第二条：这个开发版编译的一个条件，存在于uboot/board/freescale/imx6ullevk中
```config
CONFIG_TARGET_MX6ULL_14X14_EVK=y
```
改为:
```config
CONFIG_TARGET_MX6ULL_14X14_NARO=y
```

* 还有一条网络后面说。

#  5、修改板级文件
* 复制一份mx6ullevk,改为自己的板子名，如mx6ullnaro
* 将mx6ullevk.c文件改为自己的板子名，如mx6ullnaro.c

* 更改Kconfig文件，添加自己的板子名。
原文：
```shell
if TARGET_MX6ULL_14X14_EVK || TARGET_MX6ULL_9X9_EVK

config SYS_BOARD
	default "mx6ullevk"

config SYS_VENDOR
	default "freescale"

config SYS_CONFIG_NAME
	default "mx6ullevk"

config IMX_CONFIG
	default "board/freescale/mx6ullevk/imximage.cfg"

config TEXT_BASE
	default 0x87800000
endif


```
改为自己的，前面的配置就是在这里用了。
```shell
if TARGET_MX6ULL_14X14_NARO

config SYS_BOARD
	default "mx6ullnaro"

config SYS_VENDOR
	default "freescale"

config SYS_CONFIG_NAME
	default "mx6ullnaro"

config IMX_CONFIG
	default "board/freescale/mx6ullnaro/imximage.cfg"

config TEXT_BASE
	default 0x87800000
endif

```
就是一些条件编译宏

* 更改MAINTAINERS文件：
原文：
```shell
MX6ULLEVK BOARD
M:	Peng Fan <peng.fan@nxp.com>
S:	Maintained
F:	board/freescale/mx6ullevk/
F:	include/configs/mx6ullevk.h
F:	configs/mx6ull_14x14_evk_defconfig
F:	configs/mx6ull_14x14_evk_plugin_defconfig
F:	configs/mx6ulz_14x14_evk_defconfig
```
这段代码描述了MX6ULL NARO开发板的相关维护信息和配置文件路径。具体说明如下：

M: 维护者信息，Peng Fan peng.fan@nxp.com。
S: 当前状态为“Maintained”，表示该板子正在维护中。
F: 列出了与MX6ULL NARO开发板相关的配置文件路径，包括：
board/freescale/mx6ullevk/
include/configs/mx6ullevk.h
configs/mx6ull_14x14_evk_defconfig
configs/mx6ull_14x14_evk_plugin_defconfig
configs/mx6ulz_14x14_evk_defconfig
这些文件定义了开发板的硬件配置和启动参数。

改为自己的：
```shell
MX6ULLNARO BOARD
M:	Peng Fan <peng.fan@nxp.com>
S:	Maintained
F:	board/freescale/mx6ullnaro/
F:	include/configs/mx6ullnaro.h
F:	configs/mx6ull_14x14_naro_defconfig

```
* 更改Makefile文件：
原文：
```MAKEFILE
# SPDX-License-Identifier: GPL-2.0+
# (C) Copyright 2016 Freescale Semiconductor, Inc.
 
obj-y  := mx6ullevk.o
```
改为自己的：
```MAKEFILE
# SPDX-License-Identifier: GPL-2.0+
# (C) Copyright 2016 Freescale Semiconductor, Inc.

obj-y  := mx6ullnaro.o

```     
 更改mx6ullalpha.c文件：
 原文：
 ```C
 // SPDX-License-Identifier: GPL-2.0+
/*
 * Copyright (C) 2016 Freescale Semiconductor, Inc.
 * Copyright 2017 NXP
 */

#include <init.h>
#include <asm/arch/clock.h>
#include <asm/arch/iomux.h>
#include <asm/arch/imx-regs.h>
#include <asm/arch/crm_regs.h>
#include <asm/arch/mx6-pins.h>
#include <asm/arch/sys_proto.h>
#include <asm/global_data.h>
#include <asm/gpio.h>
#include <asm/mach-imx/iomux-v3.h>
#include <asm/mach-imx/boot_mode.h>
#include <asm/mach-imx/mxc_i2c.h>
#include <asm/io.h>
#include <common.h>
#include <env.h>
#include <fsl_esdhc_imx.h>
#include <i2c.h>
#include <miiphy.h>
#include <linux/sizes.h>
#include <linux/delay.h>
#include <mmc.h>
#include <miiphy.h>
#include <power/pmic.h>
#include <power/pfuze3000_pmic.h>
#include "../common/pfuze.h"

DECLARE_GLOBAL_DATA_PTR;

// 定义I2C引脚控制寄存器的配置
#define I2C_PAD_CTRL    (PAD_CTL_PKE | PAD_CTL_PUE |            \
	PAD_CTL_PUS_100K_UP | PAD_CTL_SPEED_MED |               \
	PAD_CTL_DSE_40ohm | PAD_CTL_HYS |			\
	PAD_CTL_ODE)

// 定义LCD引脚控制寄存器的配置
#define LCD_PAD_CTRL    (PAD_CTL_HYS | PAD_CTL_PUS_100K_UP | PAD_CTL_PUE | \
	PAD_CTL_PKE | PAD_CTL_SPEED_MED | PAD_CTL_DSE_40ohm)

// 定义GPMI NAND引脚控制寄存器的配置
#define GPMI_PAD_CTRL0 (PAD_CTL_PKE | PAD_CTL_PUE | PAD_CTL_PUS_100K_UP)
#define GPMI_PAD_CTRL1 (PAD_CTL_DSE_40ohm | PAD_CTL_SPEED_MED | \
			PAD_CTL_SRE_FAST)
#define GPMI_PAD_CTRL2 (GPMI_PAD_CTRL0 | GPMI_PAD_CTRL1)

#ifdef CONFIG_DM_PMIC
// 初始化电源管理IC（PMIC）
int power_init_board(void)
{
	struct udevice *dev;
	int ret, dev_id, rev_id;
	unsigned int reg;

	// 获取PFUZE3000 PMIC设备
	ret = pmic_get("pfuze3000@8", &dev);
	if (ret == -ENODEV)
		return 0; // 如果设备不存在，返回0
	if (ret != 0)
		return ret; // 如果获取设备失败，返回错误码

	// 读取PMIC的设备ID和修订ID
	dev_id = pmic_reg_read(dev, PFUZE3000_DEVICEID);
	rev_id = pmic_reg_read(dev, PFUZE3000_REVID);
	printf("PMIC: PFUZE3000 DEV_ID=0x%x REV_ID=0x%x\n", dev_id, rev_id);

	// 禁用待机模式期间的低功耗模式
	reg = pmic_reg_read(dev, PFUZE3000_LDOGCTL);
	reg |= 0x1;
	pmic_reg_write(dev, PFUZE3000_LDOGCTL, reg);

	// 设置SW1B的上升时间从2us到4us/25mV
	pmic_reg_write(dev, PFUZE3000_SW1BCONF, 0x40);

	// 设置SW1B模式为APS/PFM
	pmic_reg_write(dev, PFUZE3000_SW1BMODE, 0xc);

	// 设置SW1B待机电压为0.975V
	pmic_reg_write(dev, PFUZE3000_SW1BSTBY, 0xb);

	return 0;
}

#ifdef CONFIG_LDO_BYPASS_CHECK
// 设置LDO旁路模式
void ldo_mode_set(int ldo_bypass)
{
	unsigned int value;
	u32 vddarm;
	struct udevice *dev;
	int ret;

	// 获取PFUZE3000 PMIC设备
	ret = pmic_get("pfuze3000@8", &dev);
	if (ret == -ENODEV) {
		printf("No PMIC found!\n");
		return;
	}

	// 切换到LDO旁路模式
	if (ldo_bypass) {
		prep_anatop_bypass();
		// 将VDDARM电压降低到1.275V
		value = pmic_reg_read(dev, PFUZE3000_SW1BVOLT);
		value &= ~0x1f;
		value |= PFUZE3000_SW1AB_SETP(12750);
		pmic_reg_write(dev, PFUZE3000_SW1BVOLT, value);

		set_anatop_bypass(1);
		vddarm = PFUZE3000_SW1AB_SETP(11750);

		value = pmic_reg_read(dev, PFUZE3000_SW1BVOLT);
		value &= ~0x1f;
		value |= vddarm;
		pmic_reg_write(dev, PFUZE3000_SW1BVOLT, value);

		finish_anatop_bypass();

		printf("switch to ldo_bypass mode!\n");
	}
}
#endif
#endif

// 初始化DRAM
int dram_init(void)
{
	gd->ram_size = imx_ddr_size(); // 获取DDR内存大小

	return 0;
}

// 获取MMC设备编号
int board_mmc_get_env_dev(int devno)
{
	return devno;
}

#ifdef CONFIG_FSL_QSPI
#ifndef CONFIG_DM_SPI
// 定义QuadSPI引脚控制寄存器的配置
#define QSPI_PAD_CTRL1	\
	(PAD_CTL_SRE_FAST | PAD_CTL_SPEED_MED | \
	 PAD_CTL_PKE | PAD_CTL_PUE | PAD_CTL_PUS_47K_UP | PAD_CTL_DSE_120ohm)

// QuadSPI引脚配置数组
static iomux_v3_cfg_t const quadspi_pads[] = {
	MX6_PAD_NAND_WP_B__QSPI_A_SCLK | MUX_PAD_CTRL(QSPI_PAD_CTRL1),
	MX6_PAD_NAND_READY_B__QSPI_A_DATA00 | MUX_PAD_CTRL(QSPI_PAD_CTRL1),
	MX6_PAD_NAND_CE0_B__QSPI_A_DATA01 | MUX_PAD_CTRL(QSPI_PAD_CTRL1),
	MX6_PAD_NAND_CE1_B__QSPI_A_DATA02 | MUX_PAD_CTRL(QSPI_PAD_CTRL1),
	MX6_PAD_NAND_CLE__QSPI_A_DATA03 | MUX_PAD_CTRL(QSPI_PAD_CTRL1),
	MX6_PAD_NAND_DQS__QSPI_A_SS0_B | MUX_PAD_CTRL(QSPI_PAD_CTRL1),
};
#endif

// 初始化QuadSPI
static int board_qspi_init(void)
{
#ifndef CONFIG_DM_SPI
	// 设置QuadSPI引脚
	imx_iomux_v3_setup_multiple_pads(quadspi_pads,
					 ARRAY_SIZE(quadspi_pads));
#endif
	// 启用QuadSPI时钟
	enable_qspi_clk(0);

	return 0;
}
#endif

#ifdef CONFIG_NAND_MXS
// NAND引脚配置数组
static iomux_v3_cfg_t const nand_pads[] = {
	MX6_PAD_NAND_DATA00__RAWNAND_DATA00 | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_DATA01__RAWNAND_DATA01 | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_DATA02__RAWNAND_DATA02 | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_DATA03__RAWNAND_DATA03 | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_DATA04__RAWNAND_DATA04 | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_DATA05__RAWNAND_DATA05 | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_DATA06__RAWNAND_DATA06 | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_DATA07__RAWNAND_DATA07 | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_CLE__RAWNAND_CLE | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_ALE__RAWNAND_ALE | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_CE0_B__RAWNAND_CE0_B | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_CE1_B__RAWNAND_CE1_B | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_RE_B__RAWNAND_RE_B | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_WE_B__RAWNAND_WE_B | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_WP_B__RAWNAND_WP_B | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_READY_B__RAWNAND_READY_B | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
	MX6_PAD_NAND_DQS__RAWNAND_DQS | MUX_PAD_CTRL(GPMI_PAD_CTRL2),
};

// 初始化GPMI NAND
static void setup_gpmi_nand(void)
{
	struct mxc_ccm_reg *mxc_ccm = (struct mxc_ccm_reg *)CCM_BASE_ADDR;

	// 设置GPMI NAND引脚
	imx_iomux_v3_setup_multiple_pads(nand_pads, ARRAY_SIZE(nand_pads));

	// 设置GPMI IO时钟
	setup_gpmi_io_clk((MXC_CCM_CS2CDR_ENFC_CLK_PODF(0) |
			MXC_CCM_CS2CDR_ENFC_CLK_PRED(3) |
			MXC_CCM_CS2CDR_ENFC_CLK_SEL(3)));

	// 启用APBH时钟门控
	setbits_le32(&mxc_ccm->CCGR0, MXC_CCM_CCGR0_APBHDMA_MASK);
}
#endif

#ifdef CONFIG_FEC_MXC
// 初始化FEC（以太网）
static int setup_fec(void)
{
	struct iomuxc *const iomuxc_regs = (struct iomuxc *)IOMUXC_BASE_ADDR;
	int ret;

	/*
	 * 使用50M anatop环回REF_CLK1作为ENET1的时钟源，
	 * 清除gpr1[13]，设置gpr1[17]。
	 */
	clrsetbits_le32(&iomuxc_regs->gpr[1], IOMUX_GPR1_FEC1_MASK,
			IOMUX_GPR1_FEC1_CLOCK_MUX1_SEL_MASK);
	/*
	 * 使用50M anatop环回REF_CLK2作为ENET2的时钟源，
	 * 清除gpr1[14]，设置gpr1[18]。
	 */
	if (!check_module_fused(MODULE_ENET2)) {
		clrsetbits_le32(&iomuxc_regs->gpr[1], IOMUX_GPR1_FEC2_MASK,
				IOMUX_GPR1_FEC2_CLOCK_MUX1_SEL_MASK);
	}

	// 启用ENET1的anatop时钟
	ret = enable_fec_anatop_clock(0, ENET_50MHZ);
	if (ret)
		return ret;

	// 启用ENET2的anatop时钟
	if (!check_module_fused(MODULE_ENET2)) {
		ret = enable_fec_anatop_clock(1, ENET_50MHZ);
		if (ret)
			return ret;
	}

	// 启用ENET时钟
	enable_enet_clk(1);

	return 0;
}

// 配置PHY设备
int board_phy_config(struct phy_device *phydev)
{
	phy_write(phydev, MDIO_DEVAD_NONE, 0x1f, 0x8190);

	if (phydev->drv->config)
		phydev->drv->config(phydev);

	return 0;
}
#endif

#ifdef CONFIG_VIDEO
// LCD引脚配置数组
static iomux_v3_cfg_t const lcd_pads[] = {
	/* 使用GPIO进行亮度调整，占空比=周期。 */
	MX6_PAD_GPIO1_IO08__GPIO1_IO08 | MUX_PAD_CTRL(NO_PAD_CTRL),
};

// 初始化LCD
static int setup_lcd(void)
{
	// 启用LCDIF时钟
	enable_lcdif_clock(LCDIF1_BASE_ADDR, 1);

	// 设置LCD引脚
	imx_iomux_v3_setup_multiple_pads(lcd_pads, ARRAY_SIZE(lcd_pads));

	// 重置LCD
	gpio_request(IMX_GPIO_NR(5, 9), "lcd reset");
	gpio_direction_output(IMX_GPIO_NR(5, 9) , 0);
	udelay(500);
	gpio_direction_output(IMX_GPIO_NR(5, 9) , 1);

	// 设置亮度为高
	gpio_request(IMX_GPIO_NR(1, 8), "backlight");
	gpio_direction_output(IMX_GPIO_NR(1, 8) , 1);

	return 0;
}
#else
static inline int setup_lcd(void) { return 0; }
#endif

// 早期初始化
int board_early_init_f(void)
{
	return 0;
}

// 板级初始化
int board_init(void)
{
	/* 设置启动参数地址 */
	gd->bd->bi_boot_params = PHYS_SDRAM + 0x100;

#ifdef	CONFIG_FEC_MXC
	// 初始化FEC
	setup_fec();
#endif

#ifdef CONFIG_FSL_QSPI
	// 初始化QuadSPI
	board_qspi_init();
#endif

#ifdef CONFIG_NAND_MXS
	// 初始化GPMI NAND
	setup_gpmi_nand();
#endif

	return 0;
}

#ifdef CONFIG_CMD_BMODE
// 定义启动模式
static const struct boot_mode board_boot_modes[] = {
	/* 4位总线宽度 */
	{"sd1", MAKE_CFGVAL(0x42, 0x20, 0x00, 0x00)},
	{"sd2", MAKE_CFGVAL(0x40, 0x28, 0x00, 0x00)},
	{"qspi1", MAKE_CFGVAL(0x10, 0x00, 0x00, 0x00)},
	{NULL,	 0},
};
#endif

// 板子初始化
int board_late_init(void)
{
#ifdef CONFIG_CMD_BMODE
	// 添加启动模式
	add_board_boot_modes(board_boot_modes);
#endif

	// 设置tee环境变量
	env_set("tee", "no");
#ifdef CONFIG_IMX_OPTEE
	env_set("tee", "yes");
#endif

#ifdef CONFIG_ENV_VARS_UBOOT_RUNTIME_CONFIG
	// 设置板级名称
	env_set("board_name", "EVK");

	// 设置板级版本
	if (is_mx6ull_9x9_evk())
		env_set("board_rev", "9X9");
	else
		env_set("board_rev", "14X14");

	// 如果是MX6ULZ CPU，设置特定的环境变量
	if (is_cpu_type(MXC_CPU_MX6ULZ)) {
		env_set("board_name", "ULZ-EVK");
		env_set("usb_net_cmd", "usb start");
    }
#endif

	// 初始化LCD
	setup_lcd();

#ifdef CONFIG_ENV_IS_IN_MMC
	// 初始化MMC环境
	board_late_mmc_env_init();
#endif

	// 设置看门狗复位
	set_wdog_reset((struct wdog_regs *)WDOG1_BASE_ADDR);

	return 0;
}

// 检查板级信息
int checkboard(void)
{
	if (is_mx6ull_9x9_evk())
		puts("Board: MX6ULL 9x9 EVK\n");
	else if (is_cpu_type(MXC_CPU_MX6ULZ))
		puts("Board: MX6ULZ 14x14 EVK\n");
	else
		puts("Board: MX6ULL 14x14 EVK\n");

	return 0;
}

// 静音设备
void board_quiesce_devices(void)
{
#if defined(CONFIG_VIDEO_MXS)
	// 禁用LCDIF时钟
	enable_lcdif_clock(LCDIF1_BASE_ADDR, 0);
#endif
}
```
* 搜索CONFIG_ENV_VARS_UBOOT_RUNTIME_CONFIG配置项
```c
#ifdef CONFIG_ENV_VARS_UBOOT_RUNTIME_CONFIG
	env_set("board_name", "EVK");
 
	if (is_mx6ull_9x9_evk())
		env_set("board_rev", "9X9");
	else
		env_set("board_rev", "14X14");
 
	if (is_cpu_type(MXC_CPU_MX6ULZ)) {
		env_set("board_name", "ULZ-EVK");
		env_set("usb_net_cmd", "usb start");
    }
#endif

```
改为
```c
#ifdef CONFIG_ENV_VARS_UBOOT_RUNTIME_CONFIG
	env_set("board_name", "naro");
	env_set("board_rev", "14X14");
#endif
```

*  找到checkboard函数
```c
int checkboard(void)
{
	if (is_mx6ull_9x9_evk())
		puts("Board: MX6ULL 9x9 EVK\n");
	else if (is_cpu_type(MXC_CPU_MX6ULZ))
		puts("Board: MX6ULZ 14x14 EVK\n");
	else
		puts("Board: MX6ULL 14x14 EVK\n");
 
	return 0;
}
```
改为：
```c
int checkboard(void)
{
	puts("Board: MX6ULL ALPHA\n");
	return 0;
}
```

# 6、添加板级头文件
原文
```c
/* SPDX-License-Identifier: GPL-2.0+ */
/*
 * Copyright (C) 2016 Freescale Semiconductor, Inc.
 * Copyright 2017 NXP
 *
 * Configuration settings for the Freescale i.MX6UL 14x14 EVK board.
 */
#ifndef __MX6ULLEVK_CONFIG_H
#define __MX6ULLEVK_CONFIG_H

#include <asm/arch/imx-regs.h>
#include <linux/sizes.h>
#include <linux/stringify.h>
#include "mx6_common.h"
#include <asm/mach-imx/gpio.h>
#include "imx_env.h"

// 宏定义用于检查是否是MX6ULL 9x9 EVK
#define is_mx6ull_9x9_evk()	CONFIG_IS_ENABLED(TARGET_MX6ULL_9X9_EVK)

// 根据是否是MX6ULL 9x9 EVK定义CMA大小
#ifdef CONFIG_TARGET_MX6ULL_9X9_EVK
#define BOOTARGS_CMA_SIZE   "cma=96M "
#else
#define BOOTARGS_CMA_SIZE   ""
#endif

// 定义MXC UART基地址
#define CFG_MXC_UART_BASE		UART1_BASE

/* MMC Configs */
#ifdef CONFIG_FSL_USDHC
// 定义USDHC基地址
#define CFG_SYS_FSL_ESDHC_ADDR	USDHC2_BASE_ADDR

/* NAND pin conflicts with usdhc2 */
// 如果启用NAND，USDHC数量设置为1，否则设置为2
#ifdef CONFIG_NAND_MXS
#define CONFIG_SYS_FSL_USDHC_NUM	1
#else
#define CONFIG_SYS_FSL_USDHC_NUM	2
#endif
#endif

// 定义NAND启动时的分区信息
#ifdef CONFIG_NAND_BOOT
#define MFG_NAND_PARTITION "mtdparts=gpmi-nand:64m(nandboot),16m(nandkernel),16m(nanddtb),16m(nandtee),-(nandrootfs)"
#else
#define MFG_NAND_PARTITION ""
#endif

// 定义制造环境设置
#define CFG_MFG_ENV_SETTINGS \
	CFG_MFG_ENV_SETTINGS_DEFAULT \
	"initrd_addr=0x86800000\0" \
	"initrd_high=0xffffffff\0" \
	"emmc_dev=1\0"\
	"emmc_ack=1\0"\
	"sd_dev=1\0" \
	"mtdparts=" MFG_NAND_PARTITION \
	"\0"\

// 根据是否是NAND启动定义额外的环境设置
#if defined(CONFIG_NAND_BOOT)
#define CFG_EXTRA_ENV_SETTINGS \
	CFG_MFG_ENV_SETTINGS \
	TEE_ENV \
	"splashimage=0x8c000000\0" \
	"fdt_addr=0x83000000\0" \
	"fdt_high=0xffffffff\0"	  \
	"tee_addr=0x84000000\0" \
	"console=ttymxc0\0" \
	"bootargs=console=ttymxc0,115200 ubi.mtd=nandrootfs "  \
		"root=ubi0:rootfs rootfstype=ubifs "		     \
		BOOTARGS_CMA_SIZE \
		MFG_NAND_PARTITION \
		"\0" \
	"bootcmd=nand read ${loadaddr} 0x4000000 0xc00000;"\
		"nand read ${fdt_addr} 0x5000000 0x100000;"\
		"if test ${tee} = yes; then " \
			"nand read ${tee_addr} 0x6000000 0x400000;"\
			"bootm ${tee_addr} - ${fdt_addr};" \
		"else " \
			"bootz ${loadaddr} - ${fdt_addr};" \
		"fi\0"

#else
#define CFG_EXTRA_ENV_SETTINGS \
	CFG_MFG_ENV_SETTINGS \
	TEE_ENV \
	"script=boot.scr\0" \
	"image=zImage\0" \
	"console=ttymxc0\0" \
	"fdt_high=0xffffffff\0" \
	"initrd_high=0xffffffff\0" \
	"fdt_file=undefined\0" \
	"fdt_addr=0x83000000\0" \
	"tee_addr=0x84000000\0" \
	"tee_file=undefined\0" \
	"boot_fdt=try\0" \
	"ip_dyn=yes\0" \
	"splashimage=0x8c000000\0" \
	"mmcdev="__stringify(CONFIG_SYS_MMC_ENV_DEV)"\0" \
	"mmcpart=1\0" \
	"mmcroot=/dev/mmcblk1p2 rootwait rw\0" \
	"mmcautodetect=yes\0" \
	"mmcargs=setenv bootargs console=${console},${baudrate} " \
		BOOTARGS_CMA_SIZE \
		"root=${mmcroot}\0" \
	"loadbootscript=" \
		"fatload mmc ${mmcdev}:${mmcpart} ${loadaddr} ${script};\0" \
	"bootscript=echo Running bootscript from mmc ...; " \
		"source\0" \
	"loadimage=fatload mmc ${mmcdev}:${mmcpart} ${loadaddr} ${image}\0" \
	"loadfdt=fatload mmc ${mmcdev}:${mmcpart} ${fdt_addr} ${fdt_file}\0" \
	"loadtee=fatload mmc ${mmcdev}:${mmcpart} ${tee_addr} ${tee_file}\0" \
	"mmcboot=echo Booting from mmc ...; " \
		"run mmcargs; " \
		"if test ${tee} = yes; then " \
			"run loadfdt; run loadtee; bootm ${tee_addr} - ${fdt_addr}; " \
		"else " \
			"if test ${boot_fdt} = yes || test ${boot_fdt} = try; then " \
				"if run loadfdt; then " \
					"bootz ${loadaddr} - ${fdt_addr}; " \
				"else " \
					"if test ${boot_fdt} = try; then " \
						"bootz; " \
					"else " \
						"echo WARN: Cannot load the DT; " \
					"fi; " \
				"fi; " \
			"else " \
				"bootz; " \
			"fi; " \
		"fi;\0" \
	"netargs=setenv bootargs console=${console},${baudrate} " \
		BOOTARGS_CMA_SIZE \
		"root=/dev/nfs " \
	"ip=dhcp nfsroot=${serverip}:${nfsroot},v3,tcp\0" \
		"netboot=echo Booting from net ...; " \
		"${usb_net_cmd}; " \
		"run netargs; " \
		"if test ${ip_dyn} = yes; then " \
			"setenv get_cmd dhcp; " \
		"else " \
			"setenv get_cmd tftp; " \
		"fi; " \
		"${get_cmd} ${image}; " \
		"if test ${tee} = yes; then " \
			"${get_cmd} ${tee_addr} ${tee_file}; " \
			"${get_cmd} ${fdt_addr} ${fdt_file}; " \
			"bootm ${tee_addr} - ${fdt_addr}; " \
		"else " \
			"if test ${boot_fdt} = yes || test ${boot_fdt} = try; then " \
				"if ${get_cmd} ${fdt_addr} ${fdt_file}; then " \
					"bootz ${loadaddr} - ${fdt_addr}; " \
				"else " \
					"if test ${boot_fdt} = try; then " \
						"bootz; " \
					"else " \
						"echo WARN: Cannot load the DT; " \
					"fi; " \
				"fi; " \
			"else " \
				"bootz; " \
			"fi; " \
		"fi;\0" \
		"findfdt="\
			"if test $fdt_file = undefined; then " \
				"if test $board_name = ULZ-EVK && test $board_rev = 14X14; then " \
					"setenv fdt_file imx6ulz-14x14-evk.dtb; fi; " \
				"if test $board_name = EVK && test $board_rev = 9X9; then " \
					"setenv fdt_file imx6ull-9x9-evk.dtb; fi; " \
				"if test $board_name = EVK && test $board_rev = 14X14; then " \
					"setenv fdt_file imx6ull-14x14-evk.dtb; fi; " \
				"if test $fdt_file = undefined; then " \
					"echo WARNING: Could not determine dtb to use; " \
				"fi; " \
			"fi;\0" \
		"findtee="\
			"if test $tee_file = undefined; then " \
				"if test $board_name = ULZ-EVK && test $board_rev = 14X14; then " \
					"setenv tee_file uTee-6ulzevk; fi; " \
				"if test $board_name = EVK && test $board_rev = 9X9; then " \
					"setenv tee_file uTee-6ullevk; fi; " \
				"if test $board_name = EVK && test $board_rev = 14X14; then " \
					"setenv tee_file uTee-6ullevk; fi; " \
				"if test $tee_file = undefined; then " \
					"echo WARNING: Could not determine tee to use; " \
				"fi; " \
			"fi;\0" \

#endif

/* Miscellaneous configurable options */

/* Physical Memory Map */
// 定义物理内存基地址
#define PHYS_SDRAM			MMDC0_ARB_BASE_ADDR

// 定义系统SDRAM基地址
#define CFG_SYS_SDRAM_BASE		PHYS_SDRAM
// 定义初始化RAM地址
#define CFG_SYS_INIT_RAM_ADDR	IRAM_BASE_ADDR
// 定义初始化RAM大小
#define CFG_SYS_INIT_RAM_SIZE	IRAM_SIZE

/* environment organization */

/* NAND stuff */
// 定义NAND基地址
#define CFG_SYS_NAND_BASE		0x40000000
#endif
```
evk关键字进行修改，防止遗漏。
宏定义改了
```c
#ifndef __MX6ULLNARO_CONFIG_H
#define __MX6ULLNARO_CONFIG_H

```

找到CONFIG_TARGET_MX6ULL_9X9_EVK。
```c
#ifdef CONFIG_TARGET_MX6ULL_9X9_EVK
#define BOOTARGS_CMA_SIZE   "cma=96M "
#else
#define BOOTARGS_CMA_SIZE   ""
#endif
```
改为：
```c
#define BOOTARGS_CMA_SIZE   ""
```
找findfdt：
```c
"findfdt="\
			"if test $fdt_file = undefined; then " \
				"if test $board_name = ULZ-EVK && test $board_rev = 14X14; then " \
					"setenv fdt_file imx6ulz-14x14-evk.dtb; fi; " \
				"if test $board_name = EVK && test $board_rev = 9X9; then " \
					"setenv fdt_file imx6ull-9x9-evk.dtb; fi; " \
				"if test $board_name = EVK && test $board_rev = 14X14; then " \
					"setenv fdt_file imx6ull-14x14-evk.dtb; fi; " \
				"if test $fdt_file = undefined; then " \
					"echo WARNING: Could not determine dtb to use; " \
				"fi; " \
			"fi;\0" \
```
改为
```c
"findfdt="\
			"if test $fdt_file = undefined; then " \
				"if test $board_name = naro && test $board_rev = 14X14; then " \
					"setenv fdt_file imx6ull-14x14-naro.dtb; fi; " \
				"if test $fdt_file = undefined; then " \
					"echo WARNING: Could not determine dtb to use; " \
				"fi; " \
			"fi;\0" \
```
这里配置的设备树是linux启动时所需要的设备树。

找到findtee：
```c
"if test $tee_file = undefined; then " \
				"if test $board_name = ULZ-EVK && test $board_rev = 14X14; then " \
					"setenv tee_file uTee-6ulzevk; fi; " \
				"if test $board_name = EVK && test $board_rev = 9X9; then " \
					"setenv tee_file uTee-6ullevk; fi; " \
				"if test $board_name = EVK && test $board_rev = 14X14; then " \
					"setenv tee_file uTee-6ullevk; fi; " \
				"if test $tee_file = undefined; then " \
					"echo WARNING: Could not determine tee to use; " \
				"fi; " \
			"fi;\0" \
```
改为
```c
"findtee="\
			"if test $tee_file = undefined; then " \
				"if test $board_name = naro && test $board_rev = 14X14; then " \
					"setenv tee_file uTee-6ullnaro; fi; " \
				"if test $tee_file = undefined; then " \
					"echo WARNING: Could not determine tee to use; " \
				"fi; " \
			"fi;\0" \
```

# 7 、配置Kconfig
找到arch/arm/mach-imx/mx6/Kconfig文件。
搜索TARGET_MX6ULL_14X14_EVK，默认内容为：
```c
config TARGET_MX6ULL_14X14_EVK
	bool "Support mx6ull_14x14_evk"
	depends on MX6ULL
	select BOARD_LATE_INIT
	select DM
	select DM_THERMAL
	select IOMUX_LPSR
	select IMX_MODULE_FUSE
	select OF_SYSTEM_SETUP
	imply CMD_DM
```
下方添加：
```c
config TARGET_MX6ULL_14X14_NARO
	bool "Support mx6ull_14x14_naro"
	depends on MX6ULL
	select BOARD_LATE_INIT
	select DM
	select DM_THERMAL
	select IOMUX_LPSR
	select IMX_MODULE_FUSE
	select OF_SYSTEM_SETUP
	imply CMD_DM
```
搜索source "board/freescale/mx6ullevk/Kconfig" ，在其下方添加：
```c
source "board/freescale/mx6ullnaro/Kconfig"
```

# 8、添加相应设备树文件
## 8-1、dtsi和dts区别
.dtsi文件：类似于C语言中的头文件（.h文件），通常包含多个设备或子系统的公共定义和配置。这些文件可以被多个.dts文件引用，以避免重复定义。例如，处理器的通用外设定义、引脚复用配置等。
.dts文件：是具体的设备树源文件，针对特定的板级配置。它会包含对具体硬件平台的所有详细描述，并且可以引用一个或多个.dtsi文件来组合成完整的设备树。

找到imx6ull-14x14-evk.dts,打开看的包含的文件，也要改，include了下面几个文件，所以也要复制。
找到arch/arm/dts/imx6ull-14x14-evk.dts文件，复制为arch/arm/dts/imx6ull-14X14-naro.dts。

找到arch/arm/dts/imx6ul-14x14-evk.dtsi文件，复制为arch/arm/dts/imx6ull-14X14-naro.dtsi。

找到arch/arm/dts/imx6ull-14x14-evk-u-boot.dtsi文件，复制为arch/arm/dts/imx6ull-14X14-naro-u-boot.dtsi。

修改imx6ull-14X14-naro.dts文件。
原文:
```c
// SPDX-License-Identifier: (GPL-2.0 OR MIT)
//
// Copyright (C) 2016 Freescale Semiconductor, Inc.
 
/dts-v1/;
 
#include "imx6ull.dtsi"
#include "imx6ul-14x14-evk.dtsi"
#include "imx6ul-14x14-evk-u-boot.dtsi"
 
/ {
	model = "i.MX6 ULL 14x14 EVK Board";
	compatible = "fsl,imx6ull-14x14-evk", "fsl,imx6ull";
};
 
&clks {
	assigned-clocks = <&clks IMX6UL_CLK_PLL3_PFD2>,
			  <&clks IMX6UL_CLK_PLL4_AUDIO_DIV>;
	assigned-clock-rates = <320000000>, <786432000>;
};
 
&csi {
	status = "okay";
};
 
&ov5640 {
	status = "okay";
};
 
/delete-node/ &sim2;
```

改为:移植的是EMMC版本的，所以需要将imx6ull-14x14-evk-emmc.dts文件的usdhc2结点复制到imx6ull-alpha.dts文件中，修改后文件内容为：
```c
// SPDX-License-Identifier: (GPL-2.0 OR MIT)
//
// Copyright (C) 2016 Freescale Semiconductor, Inc.

/dts-v1/;

#include "imx6ull-naro.dtsi"
#include "imx6ul-14x14-naro.dtsi"
#include "imx6ull-14x14-naro-u-boot.dtsi"

/ {
	model = "i.MX6 ULL 14x14 naro Board";
	compatible = "fsl,imx6ull-14x14-naro", "fsl,imx6ull";
};

&clks {
	assigned-clocks = <&clks IMX6UL_CLK_PLL3_PFD2>,
			  <&clks IMX6UL_CLK_PLL4_AUDIO_DIV>;
	assigned-clock-rates = <320000000>, <786432000>;
};

&csi {
	status = "okay";
};

&ov5640 {
	status = "okay";
};

/delete-node/ &sim2;

&usdhc2 {
	pinctrl-names = "default", "state_100mhz", "state_200mhz";
	pinctrl-0 = <&pinctrl_usdhc2_8bit>;
	pinctrl-1 = <&pinctrl_usdhc2_8bit_100mhz>;
	pinctrl-2 = <&pinctrl_usdhc2_8bit_200mhz>;
	bus-width = <8>;
	non-removable;
	status = "okay";
};
```

# 9、移植网络
找到configs/mx6ull_alpha_defconfig文件，搜索CONFIG_PHY_MICREL和CONFIG_PHY_MICREL_KSZ8XXX，注释掉这两行，添加CONFIG_PHY_SMSC=y。

找到arch/arm/dts/imx6ull-alpha.dtsi文件，搜索fec1，看到网络默认配置为：
```c

&fec1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_enet1>;
	phy-mode = "rmii";
	phy-handle = <&ethphy0>;
	phy-supply = <&reg_peri_3v3>;
	status = "okay";
};
 
&fec2 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_enet2>;
	phy-mode = "rmii";
	phy-handle = <&ethphy1>;
	phy-supply = <&reg_peri_3v3>;
	status = "okay";
 
	mdio {
		#address-cells = <1>;
		#size-cells = <0>;
 
		ethphy0: ethernet-phy@2 {
			compatible = "ethernet-phy-id0022.1560";
			reg = <2>;
			micrel,led-mode = <1>;
			clocks = <&clks IMX6UL_CLK_ENET_REF>;
			clock-names = "rmii-ref";
 
		};
 
		ethphy1: ethernet-phy@1 {
			compatible = "ethernet-phy-id0022.1560";
			reg = <1>;
			micrel,led-mode = <1>;
			clocks = <&clks IMX6UL_CLK_ENET2_REF>;
			clock-names = "rmii-ref";
		};
	};
};
```
改为：
```c
&fec1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_enet1
				 &pinctrl_enet1_reset>;
	phy-mode = "rmii";
	phy-handle = <&ethphy0>;
	phy-reset-gpios = <&gpio5 7 GPIO_ACTIVE_LOW>;
	phy-reset-duration = <200>;
	status = "disable";
};
 
&fec2 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_enet2
				 &pinctrl_enet2_reset>;
	phy-mode = "rmii";
	phy-handle = <&ethphy1>;
	phy-reset-gpios = <&gpio5 8 GPIO_ACTIVE_LOW>;
	phy-reset-duration = <200>;
	status = "okay";
 
	mdio {
		#address-cells = <1>;
		#size-cells = <0>;
 
		ethphy0: ethernet-phy@0 {
			compatible = "ethernet-phy-id0022.1560";
			reg = <0>;
			smsc,led-mode = <1>;
			clocks = <&clks IMX6UL_CLK_ENET_REF>;
			clock-names = "rmii-ref";
 
		};
 
		ethphy1: ethernet-phy@1 {
			compatible = "ethernet-phy-id0022.1560";
			reg = <1>;
			smsc,led-mode = <1>;
			clocks = <&clks IMX6UL_CLK_ENET2_REF>;
			clock-names = "rmii-ref";
		};
	};
};
```
uboot只能使能一个网口，所以我们需要disable一个网口，fec1使能比较麻烦，所以我这里使能fec2，同时添加了复位引脚。
搜索找到pinctrl_enet1结点位置，在此节点后面添加：
```c
pinctrl_enet1_reset:enet1resetgrp {
		fsl,pins = <
			MX6ULL_PAD_SNVS_TAMPER7__GPIO5_IO07	0x10B0
		>;
	};
```
同理，在pinctrl_enet2后面添加：
```c
pinctrl_enet2_reset:enet2resetgrp {
		fsl,pins = <
			MX6ULL_PAD_SNVS_TAMPER8__GPIO5_IO08	0x10B0
		>;
	};
```

最后需要修改drivers/net/phy/phy.c文件，找到genphy_config_aneg函数，在int result;后面加上phy_reset(phydev);让网口复位

# 10、编译 测试 
`最后会发现无法启动内核，是需要将arch/arm/mach-imx/mx6/Kconfig文件中把select OF_SYSTEM_SETUP去掉----重点`
这里不改，就起不来。

# 11、修改屏幕
arch/arm/dts/imx6ull-naro.dtsi文件，搜索lcdicc结点，找到：
```c
&lcdif {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_lcdif_dat
		     &pinctrl_lcdif_ctrl>;
	display = <&display0>;
	status = "okay";
 
	display0: display@0 {
		bits-per-pixel = <24>;
		bus-width = <24>;
 
		display-timings {
			native-mode = <&timing0>;
 
			timing0: timing0 {
				clock-frequency = <9200000>;
				hactive = <480>;
				vactive = <272>;
				hfront-porch = <8>;
				hback-porch = <4>;
				hsync-len = <41>;
				vback-porch = <2>;
				vfront-porch = <4>;
				vsync-len = <10>;
				hsync-active = <0>;
				vsync-active = <0>;
				de-active = <1>;
				pixelclk-active = <0>;
			};
		};
	};
};
```
改为自己的屏幕参数
```c

&lcdif {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_lcdif_dat
		     &pinctrl_lcdif_ctrl>;
	display = <&display0>;
	status = "okay";

	display0: display {
		bits-per-pixel = <24>;
		bus-width = <24>;

		display-timings {
			native-mode = <&timing0>;
			timing0: timing0 {
			clock-frequency = <33000000>;
			hactive = <800>;
			vactive = <480>;
			hfront-porch = <40>;
			hback-porch = <88>;
			hsync-len = <48>;
			vback-porch = <32>;
			vfront-porch = <13>;
			vsync-len = <3>;

			hsync-active = <0>;
			vsync-active = <0>;
			de-active = <1>;
			pixelclk-active = <0>;
			};
		};
	};
};

```

正点原子的uboot移植视频里还讲了校验码的修改，这个文件写的就是生成的bin文件的头部信息，只有校验码正确了，我们才能够直接烧写uboot编译生成的uboot-dtb.imx文件。
找到board/freescale/mx6ullalpha/imximage.cfg文件，搜索0x021B083C，连续三行默认值为：
```c
DATA 4 0x021B083C 0x41640158
DATA 4 0x021B0848 0x40403237
DATA 4 0x021B0850 0x40403C33

```
改为：
```c
DATA 4 0x021B083C 0x01380138
DATA 4 0x021B0848 0x40402E32
DATA 4 0x021B0850 0x40403432


```

# 12、编译测试
重置环境变量
```shell
env default -a
saveenv
```
配置uboot网络环境,有两个网口，设置mac要注意顺序
```shell
setenv ipaddr 192.168.8.11
setenv eth1addr b8:ae:1d:01:00:00
setenv gatewayip 192.168.8.1
setenv netmask 255.255.255.0
setenv serverip 192.168.8.9
saveenv
```

启动后。测试ping通，显示正常。
```shell
=> ping 192.168.8.9
Using ethernet@20b4000 device
host 192.168.8.9 is alive
```

```shell
setenv bootargs 'console=ttymxc0,115200 root=/dev/mmcblk1p2 rootwait rw'
setenv bootcmd 'mmc dev 1; fatload mmc 1:1 80800000 zImage; imx6ull-14x14-emmc-4.3-800x480-c.dtb; bootz 80800000 - 83000000;'
saveenv
```
可以通过下面命令核对。
```shell
mmc part
fatls mmc 1:1
```
网络挂载系统
```shell
setenv bootargs 'console=ttymxc0,115200 root=/dev/mmcblk1p2 rootwait rw'
setenv bootcmd 'tftp 80800000 zImage; tftp 83000000 imx6ull-14x14-evk-naro-emmc.dtb; bootz 80800000 - 83000000'
saveenv
``` 

# 13、修改emmc
测试发现emmc的设备节点相比旧版本，缺少了重置的gpio，所以需要修改dts文件。
报错信息：
```shell
Normal Boot
Hit any key to stop autoboot:  0
Card did not respond to voltage select! : -110
Card did not respond to voltage select! : -110
```
```shell
	reg_sd1_vmmc: regulator-sd1-vmmc {
		compatible = "regulator-fixed";
		regulator-name = "VSD_3V3";
		regulator-min-microvolt = <3300000>;
		regulator-max-microvolt = <3300000>;
		gpio = <&gpio1 9 GPIO_ACTIVE_HIGH>;
		off-on-delay-us = <20000>;
		enable-active-high;
	};
//下面新增
	reg_sd2_vmmc: regulator-sd2-vmmc {
		compatible = "regulator-fixed";
		regulator-name = "+V3.3";
		regulator-min-microvolt = <3300000>;
		regulator-max-microvolt = <3300000>;
		gpio = <&gpio4 10 GPIO_ACTIVE_HIGH>; //重置引脚，要和硬件对应
		off-on-delay-us = <20000>;
		enable-active-high;
	};
```


```shell

&usdhc2 {
	pinctrl-names = "default", "state_100mhz", "state_200mhz";
	pinctrl-0 = <&pinctrl_usdhc2_8bit>;
	pinctrl-1 = <&pinctrl_usdhc2_8bit_100mhz>;
	pinctrl-2 = <&pinctrl_usdhc2_8bit_200mhz>;
	bus-width = <8>;
	non-removable;
	no-1-8-v;
	vmmc-supply = <&reg_sd2_vmmc>; //新增
	status = "okay";
};
```

移植linux时注意用emmc版本