#!/usr/bin/env bash
set -euo pipefail
SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
: "${KERNEL_DIR:?请设置已完成构建且与板端匹配的内核源码绝对路径}"
: "${CROSS_COMPILE:?请设置 ARM 交叉工具链的绝对路径前缀}"
test -s "$KERNEL_DIR/Module.symvers"
for option in CONFIG_W1 CONFIG_W1_MASTER_GPIO; do
    grep -qx "$option=m" "$KERNEL_DIR/.config" || {
        echo "需要 $option=m" >&2
        exit 1
    }
done
if grep -Eq '^CONFIG_W1_SLAVE_THERM=[ym]$' "$KERNEL_DIR/.config"; then
    echo "请关闭 CONFIG_W1_SLAVE_THERM" >&2
    exit 1
fi
make -C "$KERNEL_DIR" ARCH=arm CROSS_COMPILE="$CROSS_COMPILE" \
    -j"${BUILD_JOBS:-4}" modules
grep -q '[[:space:]]w1_register_family[[:space:]]' "$KERNEL_DIR/Module.symvers" || {
    echo "内核模块构建后仍缺少 w1 导出符号，停止构建外部模块" >&2
    exit 1
}
make -C "$KERNEL_DIR" M="$SOURCE_DIR" ARCH=arm \
    CROSS_COMPILE="$CROSS_COMPILE" -j"${BUILD_JOBS:-4}" modules
echo "已生成 $SOURCE_DIR/ct1820b.ko；wire.ko 和 w1-gpio.ko 请使用同一内核构建产物。"
