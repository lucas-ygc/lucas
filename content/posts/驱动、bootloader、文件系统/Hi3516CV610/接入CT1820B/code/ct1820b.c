// SPDX-License-Identifier: GPL-2.0-only
/* CT1820B, external supply only. No configuration/EEPROM writes.
 * This module owns family 0x28; do not load w1_therm alongside it.
 */
#include <linux/module.h>
#include <linux/device.h>
#include <linux/delay.h>
#include <linux/jiffies.h>
#include <linux/w1.h>

static ssize_t temperature_show(struct device *dev,
		struct device_attribute *attr, char *buf)
{
	struct w1_slave *sl = dev_to_w1_slave(dev);
	struct w1_master *master = sl->master;
	unsigned long deadline;
	u8 data[9];
	int ret, raw;

	ret = mutex_lock_interruptible(&master->bus_mutex);
	if (ret)
		return ret;

	ret = -ENODEV;
	if (w1_reset_select_slave(sl))
		goto out;
	w1_write_8(master, 0xb4); /* READ POWER SUPPLY */
	if (!w1_touch_bit(master, 1)) {
		dev_warn_ratelimited(dev, "Parasite supply unsupported; use external VCC\n");
		ret = -EOPNOTSUPP;
		goto out;
	}
	if (w1_reset_select_slave(sl))
		goto out;
	w1_write_8(master, 0x44); /* CONVERT TEMPERATURE */
	/* 30 ms is typical, not a guaranteed maximum. Poll with a 1 s bound.
	 * Keep the bus locked so discovery/other readers cannot reset conversion.
	 */
	deadline = jiffies + msecs_to_jiffies(1000);
	for (;;) {
		if (msleep_interruptible(5)) {
			ret = -EINTR;
			goto out;
		}
		if (w1_touch_bit(master, 1))
			break;
		if (time_after_eq(jiffies, deadline)) {
			ret = -ETIMEDOUT;
			goto out;
		}
	}
	if (w1_reset_select_slave(sl))
		goto out;
	w1_write_8(master, 0xbe); /* READ REGISTERS including CRC */
	ret = -EIO;
	if (w1_read_block(master, data, sizeof(data)) != sizeof(data))
		goto out;
	ret = -EBADMSG;
	if (w1_calc_crc8(data, 8) != data[8])
		goto out;
	/* Rev 1.3 lists 0x6f on p10 and 0x7f on p12. Accept both.
	 * Reject stuck-low data
	 * (all zero bytes have a valid CRC) and incompatible configurations.
	 */
	ret = -EIO;
	if (data[4] != 0x7f && data[4] != 0x6f)
		goto out;
	raw = (s16)((data[1] << 8) | data[0]);
	ret = -ERANGE;
	if (raw < -50 * 16 || raw > 150 * 16)
		goto out;
	ret = sysfs_emit(buf, "%d\n", raw * 1000 / 16);
out:
	mutex_unlock(&master->bus_mutex);
	return ret;
}
static DEVICE_ATTR_RO(temperature);

static struct attribute *ct1820_attrs[] = {
	&dev_attr_temperature.attr,
	NULL,
};
ATTRIBUTE_GROUPS(ct1820);

static const struct w1_family_ops ct1820_ops = {
	.groups = ct1820_groups,
};
static struct w1_family ct1820_family = {
	.fid = 0x28,
	.fops = &ct1820_ops,
};
module_w1_family(ct1820_family);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("ygc");
MODULE_DESCRIPTION("CT1820B on-demand temperature, external supply only");
MODULE_ALIAS("w1-family-0x28");
