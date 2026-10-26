---
title: uboot移植（uboot2016移植）
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux驱动学习
abbrlink: 99b63079
typora-root-url: ./..\..\..
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---

# 移植uboot2016.03版本
主要修改：配置文件，板子头文件。驱动文件

`注意使用低版本的交叉编译工具，板子运行报错。`
## 1、修改配置文件
找到符合自己板子的配置文件--mx6ull_14x14_evk_emmc_deconfig
复制一份
```shell
cp mx6ull_14x14_evk_emmc_deconfig mx6ull_naro_emmc_deconfig
```
文件内容修改如下
```shell
CONFIG_SYS_EXTRA_OPTIONS="IMX_CONFIG=board/freescale/mx6ull_naro/imximage.cfg,MX6ULL_EVK_EMMC_REWORK"
CONFIG_ARM=y
CONFIG_ARCH_MX6=y
CONFIG_TARGET_MX6ULL_NARO=y
CONFIG_CMD_GPIO=y
```
修改第一条板级配置文件路径，修改第四条编译的选项。

## 2、修改板子的头文件
找到include/configs/mx6ullevk.h，复制一份
```shell
cp mx6ullevk.h mx6ull_naro.h
```

将开头的编译宏改为
```c
#ifndef __MX6ULL_NARO
#define __MX6ULL_NARO 

```
移植uboot的是时候没有某个功能可以到下面这个文件中找
```c
#include "mx6_common.h"
```

## 3、修改板子board文件夹下文件
将board/freescale/mx6ullevk复制一份,命名为mx6ull_naro
```shell
cp -r board/freescale/mx6ullevk board/freescale/mx6ull_naro
```
* 修改board/freescale/mx6ull_naro/Kconfig
原本的：
```shell
if TARGET_MX6ULL_14X14_EVK || TARGET_MX6ULL_9X9_EVK

config SYS_BOARD
	default "mx6ullevk"

config SYS_VENDOR
	default "freescale"

config SYS_CONFIG_NAME
	default "mx6ullevk"

endif

```
改为：
```shell
if TARGET_MX6ULL_NARO

config SYS_BOARD
	default "mx6ull_naro"

config SYS_VENDOR
	default "freescale"

config SYS_CONFIG_NAME
	default "mx6ull_naro"

endif
```

* 修改makefile

```makefile

obj-y  := mx6ull_naro.o

extra-$(CONFIG_USE_PLUGIN) :=  plugin.bin
$(obj)/plugin.bin: $(obj)/plugin.o
	$(OBJCOPY) -O binary --gap-fill 0xff $< $@


```
修改为：
```makefile
obj-y  := mx6ull_naro.o

extra-$(CONFIG_USE_PLUGIN) :=  plugin.bin
$(obj)/plugin.bin: $(obj)/plugin.o
	$(OBJCOPY) -O binary --gap-fill 0xff $< $@

```

* 修改imximage.cfg
原来的
```shell
#ifdef CONFIG_USE_PLUGIN
/*PLUGIN    plugin-binary-file    IRAM_FREE_START_ADDR*/
PLUGIN	board/freescale/mx6ullevk/plugin.bin 0x00907000
#else
```
改为:
```shell
#ifdef CONFIG_USE_PLUGIN
/*PLUGIN    plugin-binary-file    IRAM_FREE_START_ADDR*/
PLUGIN	board/freescale/mx6ull_naro/plugin.bin 0x00907000
#else
```

* 修改MAINTAINERS文件
原来的：
```shell
MX6ULLEVK BOARD
M:	Peng Fan <peng.fan@nxp.com>
S:	Maintained
F:	board/freescale/mx6ullevk/
F:	include/configs/mx6ullevk.h
F:	configs/mx6ull_14x14_evk_defconfig
F:	configs/mx6ull_9x9_evk_defconfig
```
修改为：
```shell
MX6ULLEVK BOARD
M:	Peng Fan <peng.fan@nxp.com>
S:	Maintained
F:	board/freescale/mx6ull_naro/
F:	include/configs/mx6ull_naro.h

```
# 4、修改图形配置文件

修改arch/arm/cpu/armv7/mx6/Kconfig,找到mx6ull相关的配置，添加以下内容
```shell
source "board/freescale/mx6ull_naro/Kconfig"
```

```shell
config TARGET_MX6ULL_NARO
	bool "Support mx6ull_naro"
	select MX6ULL
	select DM
	select DM_THERMAL
```

# 5、修改lcd
在board/freescale/mx6ull_naro/mx6ull_naro.c，修改如下代码
```c
struct display_info_t const displays[] = {{
	.bus = MX6UL_LCDIF1_BASE_ADDR,
	.addr = 0,
	.pixfmt = 24,
	.detect = NULL,
	.enable	= do_enable_parallel_lcd,
	.mode	= {
		.name			= "TFT4384",
		.xres           = 800,
		.yres           = 480,
		.pixclock       = 32258,
		.left_margin    = 88,
		.right_margin   = 40,
		.upper_margin   = 32,
		.lower_margin   = 13,
		.hsync_len      = 48,
		.vsync_len      = 3,
		.sync           = 0,
		.vmode          = FB_VMODE_NONINTERLACED
} } };
```
.pixclock 这个值要参考屏幕的的手册。

# 6、修改网络驱动
* 在mx6ull_naro.h中
```c
#if (CONFIG_FEC_ENET_DEV == 0)
#define IMX_FEC_BASE			ENET_BASE_ADDR
#define CONFIG_FEC_MXC_PHYADDR          0x2
#define CONFIG_FEC_XCV_TYPE             RMII
#elif (CONFIG_FEC_ENET_DEV == 1)
#define IMX_FEC_BASE			ENET2_BASE_ADDR
#define CONFIG_FEC_MXC_PHYADDR		0x1
#define CONFIG_FEC_XCV_TYPE		RMII
#endif
#define CONFIG_ETHPRIME			"FEC"

```
修改为：

```c

#if (CONFIG_FEC_ENET_DEV == 0)
#define IMX_FEC_BASE			ENET_BASE_ADDR
#define CONFIG_FEC_MXC_PHYADDR          0x0
#define CONFIG_FEC_XCV_TYPE             RMII
#elif (CONFIG_FEC_ENET_DEV == 1)
#define IMX_FEC_BASE			ENET2_BASE_ADDR
#define CONFIG_FEC_MXC_PHYADDR		0x1
#define CONFIG_FEC_XCV_TYPE		RMII
#endif
#define CONFIG_ETHPRIME			"FEC"
#define CONFIG_PHYLIB
#define CONFIG_PHY_SMSC
```
 * 在mx6ull_naro.c中,修改复位口，如下：
 ```c
// #define IOX_SDI IMX_GPIO_NR(5, 10)
// #define IOX_STCP IMX_GPIO_NR(5, 7)
// #define IOX_SHCP IMX_GPIO_NR(5, 11)
// #define IOX_OE IMX_GPIO_NR(5, 8)
#define ENET1_RESET IMX_GPIO_NR(5, 7)
#define ENET2_RESET IMX_GPIO_NR(5, 8)
```

继续往下找：将这部分注释掉
```c

static iomux_v3_cfg_t const iox_pads[] = {
	// /* IOX_SDI */
	// MX6_PAD_BOOT_MODE0__GPIO5_IO10 | MUX_PAD_CTRL(NO_PAD_CTRL),
	// /* IOX_SHCP */
	// MX6_PAD_BOOT_MODE1__GPIO5_IO11 | MUX_PAD_CTRL(NO_PAD_CTRL),
	// /* IOX_STCP */
	// MX6_PAD_SNVS_TAMPER7__GPIO5_IO07 | MUX_PAD_CTRL(NO_PAD_CTRL),
	// /* IOX_nOE */
	// MX6_PAD_SNVS_TAMPER8__GPIO5_IO08 | MUX_PAD_CTRL(NO_PAD_CTRL),
};
```

注释掉下面的内容
```c
static void iox74lv_init(void)
{
	// int i;

	// gpio_direction_output(IOX_OE, 0);

	// for (i = 7; i >= 0; i--) {
	// 	gpio_direction_output(IOX_SHCP, 0);
	// 	gpio_direction_output(IOX_SDI, seq[qn_output[i]][0]);
	// 	udelay(500);
	// 	gpio_direction_output(IOX_SHCP, 1);
	// 	udelay(500);
	// }

	// gpio_direction_output(IOX_STCP, 0);
	// udelay(500);
	// /*
	//  * shift register will be output to pins
	//  */
	// gpio_direction_output(IOX_STCP, 1);

	// for (i = 7; i >= 0; i--) {
	// 	gpio_direction_output(IOX_SHCP, 0);
	// 	gpio_direction_output(IOX_SDI, seq[qn_output[i]][1]);
	// 	udelay(500);
	// 	gpio_direction_output(IOX_SHCP, 1);
	// 	udelay(500);
	// }
	// gpio_direction_output(IOX_STCP, 0);
	// udelay(500);
	// /*
	//  * shift register will be output to pins
	//  */
	// gpio_direction_output(IOX_STCP, 1);
};

void iox74lv_set(int index)
{
	// int i;

	// for (i = 7; i >= 0; i--) {
	// 	gpio_direction_output(IOX_SHCP, 0);

	// 	if (i == index)
	// 		gpio_direction_output(IOX_SDI, seq[qn_output[i]][0]);
	// 	else
	// 		gpio_direction_output(IOX_SDI, seq[qn_output[i]][1]);
	// 	udelay(500);
	// 	gpio_direction_output(IOX_SHCP, 1);
	// 	udelay(500);
	// }

	// gpio_direction_output(IOX_STCP, 0);
	// udelay(500);
	// /*
	//   * shift register will be output to pins
	//   */
	// gpio_direction_output(IOX_STCP, 1);

	// for (i = 7; i >= 0; i--) {
	// 	gpio_direction_output(IOX_SHCP, 0);
	// 	gpio_direction_output(IOX_SDI, seq[qn_output[i]][1]);
	// 	udelay(500);
	// 	gpio_direction_output(IOX_SHCP, 1);
	// 	udelay(500);
	// }

	// gpio_direction_output(IOX_STCP, 0);
	// udelay(500);
	// /*
	//   * shift register will be output to pins
	//   */
	// gpio_direction_output(IOX_STCP, 1);
};

```
还有这个，板子的初始化中
```c
nt board_init(void)
{
	/* Address of boot parameters */
	gd->bd->bi_boot_params = PHYS_SDRAM + 0x100;

	// imx_iomux_v3_setup_multiple_pads(iox_pads, ARRAY_SIZE(iox_pads));

	// iox74lv_init();

#ifdef CONFIG_SYS_I2C_MXC
```

* 在网口的接口体中添加复位接口
```c
static iomux_v3_cfg_t const fec1_pads[] = {
	MX6_PAD_GPIO1_IO06__ENET1_MDIO | MUX_PAD_CTRL(MDIO_PAD_CTRL),
	MX6_PAD_GPIO1_IO07__ENET1_MDC | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_TX_DATA0__ENET1_TDATA00 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_TX_DATA1__ENET1_TDATA01 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_TX_EN__ENET1_TX_EN | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_TX_CLK__ENET1_REF_CLK1 | MUX_PAD_CTRL(ENET_CLK_PAD_CTRL),
	MX6_PAD_ENET1_RX_DATA0__ENET1_RDATA00 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_RX_DATA1__ENET1_RDATA01 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_RX_ER__ENET1_RX_ER | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET1_RX_EN__ENET1_RX_EN | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_SNVS_TAMPER7__GPIO5_IO07 | MUX_PAD_CTRL(NO_PAD_CTRL),
};

static iomux_v3_cfg_t const fec2_pads[] = {
	MX6_PAD_GPIO1_IO06__ENET2_MDIO | MUX_PAD_CTRL(MDIO_PAD_CTRL),
	MX6_PAD_GPIO1_IO07__ENET2_MDC | MUX_PAD_CTRL(ENET_PAD_CTRL),

	MX6_PAD_ENET2_TX_DATA0__ENET2_TDATA00 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET2_TX_DATA1__ENET2_TDATA01 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET2_TX_CLK__ENET2_REF_CLK2 | MUX_PAD_CTRL(ENET_CLK_PAD_CTRL),
	MX6_PAD_ENET2_TX_EN__ENET2_TX_EN | MUX_PAD_CTRL(ENET_PAD_CTRL),

	MX6_PAD_ENET2_RX_DATA0__ENET2_RDATA00 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET2_RX_DATA1__ENET2_RDATA01 | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET2_RX_EN__ENET2_RX_EN | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_ENET2_RX_ER__ENET2_RX_ER | MUX_PAD_CTRL(ENET_PAD_CTRL),
	MX6_PAD_SNVS_TAMPER8__GPIO5_IO08 | MUX_PAD_CTRL(NO_PAD_CTRL),
};
```

* 修改复位函数
```c
static void setup_iomux_fec(int fec_id)
{
	if (fec_id == 0) {
		imx_iomux_v3_setup_multiple_pads(fec1_pads,
						 ARRAY_SIZE(fec1_pads));
		gpio_direction_output(ENET1_RESET, 1);
		gpio_set_value(ENET1_RESET, 0);
		mdelay(20);
		gpio_set_value(ENET1_RESET, 1);
	}
	else
	{
		imx_iomux_v3_setup_multiple_pads(fec2_pads,
						 ARRAY_SIZE(fec2_pads));
		gpio_direction_output(ENET2_RESET, 1);
		gpio_set_value(ENET2_RESET, 0);
		mdelay(20);
		gpio_set_value(ENET2_RESET, 1);
	}
}

```

* 在uboot/drivers/net/phy/phy.c中添加如下代码：
```c
int genphy_update_link(struct phy_device *phydev)
{
	unsigned int mii_reg;

#ifdef CONFIG_PHY_SMSC
	static int lan8720_flag = 0;
	int bmcr_reg = 0;
	if (lan8720_flag == 0) {
		bmcr_reg = phy_read(phydev, MDIO_DEVAD_NONE, MII_BMCR);
		phy_write(phydev, MDIO_DEVAD_NONE, MII_BMCR, BMCR_RESET);
		while (phy_read(phydev, MDIO_DEVAD_NONE, MII_BMCR) & 0X8000) {
			udelay(100);
		}
		phy_write(phydev, MDIO_DEVAD_NONE, MII_BMCR, bmcr_reg);
		lan8720_flag = 1;
	}
#endif
```

不然网络复位有问题

# 7、修改板子名字
```c
int checkboard(void)
{
	if (is_mx6ull_9x9_evk())
		puts("Board: MX6ULL 9x9 EVK\n");
	else
		puts("Board: MX6ULL NARO\n");

	return 0;
}
```
# 8、编译测试
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
setenv bootcmd 'tftp 80800000 zImage; tftp 83000000 imx6ull-14x14-naro-emmc.dtb; bootz 80800000 - 83000000'
saveenv
``` 