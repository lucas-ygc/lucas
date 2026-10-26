---
title: kernel移植（linux4.115移植）
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux驱动学习
abbrlink: f9607d0d
typora-root-url: ./..\..\..
date: 2023-09-13 00:00:00
swiper_index:
sticky:
---
# 1、选择编译器
安装必备库
```shell
sudo apt-get install libncurses5-dev libncursesw5-dev
```
内核版本，uboot版本，编译器版本，都会影响到程序能否正常运行。
```shell
#/bin/bash
path="/home/ygc/Desktop/linux-gcc/gcc-linaro-4.9.4-2017.01-x86_64_arm-linux-gnueabihf/bin"
make ARCH=arm CROSS_COMPILE=$path/arm-linux-gnueabihf- distclean
make ARCH=arm CROSS_COMPILE=$path/arm-linux-gnueabihf- imx_v7_defconfig
make ARCH=arm CROSS_COMPILE=$path/arm-linux-gnueabihf- menuconfig
make ARCH=arm CROSS_COMPILE=$path/arm-linux-gnueabihf- all -j16
```
确认编译器没有问题。

# 2、添加板子的配置文件
板子的配置文件在arch/arm/configs/目录下，复制一份，修改文件名，并修改内核配置。
```shell
cp imx_v7_mfg_defconfig imx_v7_naro_defconfig
```

在这个文件中注释掉下面
```shell
# CONFIG_BLK_DEV_BSG is not set
# CONFIG_ARCH_MULTI_V6=y
CONFIG_ARCH_MXC=y
```
# 3、添加板子的dtb文件
CONFIG_ARCH_MULTI_V6 是armv6的配置。
arch/arm/boot/dts/目录下，复制一份，修改文件名，并修改内核配置。

imx6ull-14x14-evk-emmc.dtsi复制一份，改为imx6ull-14x14-evk-emmc-naro.dtsi
```shell
cp imx6ull-14x14-evk-emmc.dtsi imx6ull-14x14-evk-emmc-naro.dtsi
```

在/arch/arm/boot/dts/目录下,修改makefile
```Makefile
imx6ull-14x14-evk-btwifi.dtb \
imx6ull-14x14-evk-emmc.dtb \
imx6ull-14x14-naro-emmc.dtb \
imx6ull-14x14-evk-gpmi-weim.dtb \
imx6ull-14x14-evk-usb-certi.dtb \
```

# 4、修改网络驱动
imx6ull-14x14-evk.dtsi
注释一下部分：
```shell
pinctrl_spi4: spi4grp {
        fsl,pins = <
        MX6ULL_PAD_BOOT_MODE0__GPIO5_IO10        0x70a1
        MX6ULL_PAD_BOOT_MODE1__GPIO5_IO11        0x70a1
        # MX6ULL_PAD_SNVS_TAMPER7__GPIO5_IO07      0x70a1
        # MX6ULL_PAD_SNVS_TAMPER8__GPIO5_IO08      0x80000000
        >
};
```
还有以下部分：
```shell
	pinctrl-0 = <&pinctrl_spi4>;
	// pinctrl-assert-gpios = <&gpio5 8 GPIO_ACTIVE_LOW>;
	status = "okay";
	gpio-sck = <&gpio5 11 0>;
	gpio-mosi = <&gpio5 10 0>;
	// cs-gpios = <&gpio5 7 0>;
	num-chipselects = <1>;
```

* 增加网口的复位引脚：
```shell
&iomuxc_snvs {
	pinctrl-names = "default_snvs";
        pinctrl-0 = <&pinctrl_hog_2>;
        imx6ul-evk {

		pinctrl_enet1_reset: enet1resetgrp {
		fsl,pins = <
			/* used for enet1 reset */
			MX6ULL_PAD_SNVS_TAMPER7__GPIO5_IO07 0x10B0
		>;
		pinctrl_enet2_reset: enet2resetgrp {
		fsl,pins = <
			/* used for enet2 reset */
			MX6ULL_PAD_SNVS_TAMPER8__GPIO5_IO08 0x10B0
			>;
		};
```
* 修改两个网口的时钟配置
```shell
pinctrl_enet1: enet1grp {
	fsl,pins = <
		MX6UL_PAD_ENET1_RX_EN__ENET1_RX_EN	0x1b0b0
		MX6UL_PAD_ENET1_RX_ER__ENET1_RX_ER	0x1b0b0
		MX6UL_PAD_ENET1_RX_DATA0__ENET1_RDATA00	0x1b0b0
		MX6UL_PAD_ENET1_RX_DATA1__ENET1_RDATA01	0x1b0b0
		MX6UL_PAD_ENET1_TX_EN__ENET1_TX_EN	0x1b0b0
		MX6UL_PAD_ENET1_TX_DATA0__ENET1_TDATA00	0x1b0b0
		MX6UL_PAD_ENET1_TX_DATA1__ENET1_TDATA01	0x1b0b0
		MX6UL_PAD_ENET1_TX_CLK__ENET1_REF_CLK1 0x4001b009
		>;
	};

pinctrl_enet2: enet2grp {
	fsl,pins = <
		MX6UL_PAD_GPIO1_IO07__ENET2_MDC		0x1b0b0
		MX6UL_PAD_GPIO1_IO06__ENET2_MDIO	0x1b0b0
		MX6UL_PAD_ENET2_RX_EN__ENET2_RX_EN	0x1b0b0
		MX6UL_PAD_ENET2_RX_ER__ENET2_RX_ER	0x1b0b0
		MX6UL_PAD_ENET2_RX_DATA0__ENET2_RDATA00	0x1b0b0
		MX6UL_PAD_ENET2_RX_DATA1__ENET2_RDATA01	0x1b0b0
		MX6UL_PAD_ENET2_TX_EN__ENET2_TX_EN	0x1b0b0
		MX6UL_PAD_ENET2_TX_DATA0__ENET2_TDATA00	0x1b0b0
		MX6UL_PAD_ENET2_TX_DATA1__ENET2_TDATA01	0x1b0b0
		MX6UL_PAD_ENET2_TX_CLK__ENET2_REF_CLK2 0x4001b009
			>;
		};
```

修改节点属性：
```shell
&fec1 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_enet1
			&pinctrl_enet1_reset>;
	phy-mode = "rmii";
	phy-handle = <&ethphy0>;
	status = "okay";
};

&fec2 {
	pinctrl-names = "default";
	pinctrl-0 = <&pinctrl_enet2
			&pinctrl_enet2_reset>;
	phy-mode = "rmii";
	phy-handle = <&ethphy1>;
	status = "okay";

	mdio {
		#address-cells = <1>;
		#size-cells = <0>;

		ethphy0: ethernet-phy@0 {
			compatible = "ethernet-phy-ieee802.3-c22";
			reg = <0>;
		};

		ethphy1: ethernet-phy@1 {
			compatible = "ethernet-phy-ieee802.3-c22";
			reg = <1>;
		};
	};
};
```

* 修改内核源码：
修改fec.c文件，修改fec_probe函数，这个文件在drivers/net/ethernet/freescale/fec.c 代码修改如下：
```c
static int
fec_probe(struct platform_device *pdev)
{
	struct fec_enet_private *fep;
	struct fec_platform_data *pdata;
	struct net_device *ndev;
	int i, irq, ret = 0;
	struct resource *r;
	const struct of_device_id *of_id;
	static int dev_id;
	struct device_node *np = pdev->dev.of_node, *phy_node;
	int num_tx_qs;
	int num_rx_qs;

	void __iomem *IMX6U_ENET1_TX_CLK;
	void __iomem *IMX6U_ENET2_TX_CLK;
	IMX6U_ENET1_TX_CLK = ioremap(0X020E00DC, 4);
	IMX6U_ENET2_TX_CLK = ioremap(0X020E00FC, 4);
	writel(0X14, IMX6U_ENET1_TX_CLK);
	writel(0X14, IMX6U_ENET2_TX_CLK);

	// ************
```


修改smsc.c
```c

#include <linux/of_gpio.h>
#include <linux/io.h>


***********
static int smsc_phy_reset(struct phy_device *phydev)
{
	int err, phy_reset;
	int msec = 1;
	struct device_node *np;
	int timeout = 50000;
	int rc;

	if (phydev->mdio.addr == 0) {
		np = of_find_node_by_path("/soc/aips-bus@02100000/ethernet@02188000");
	} else if (phydev->mdio.addr == 1) {
		np = of_find_node_by_path("/soc/aips-bus@02000000/ethernet@020b4000");
	}

	if (!np) {
		return -1;
	}

	/* A sane reset duration should not be longer than 1s */
	err = of_property_read_u32(np, "phy-reset-duration", &msec);
	if (!err && msec > 1000)
		msec = 1;

	phy_reset = of_get_named_gpio(np, "phy-reset-gpios", 0);
	if (!gpio_is_valid(phy_reset))
		return -1;

	gpio_direction_output(phy_reset, 0);
	gpio_set_value(phy_reset, 0);
	msleep(msec);
	gpio_set_value(phy_reset, 1);

	int rc = phy_read(phydev, MII_LAN83C185_SPECIAL_MODES);
	if (rc < 0)
		return rc;
```
