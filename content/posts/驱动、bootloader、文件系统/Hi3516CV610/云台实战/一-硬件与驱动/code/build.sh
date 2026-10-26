#!/usr/bin/env bash
set -euo pipefail
SRC_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
: "${KERNEL_DIR:?设置匹配板端的已构建内核绝对路径}"
: "${CROSS_COMPILE:?设置交叉工具链的绝对路径前缀}"
for option in CONFIG_HIGH_RES_TIMERS CONFIG_OF_GPIO CONFIG_PINCTRL_SINGLE; do
    grep -qx "$option=y" "$KERNEL_DIR/.config" || {
        echo "缺少 $option=y" >&2
        exit 1
    }
done
test -s "$KERNEL_DIR/Module.symvers"
mkdir -p "$SRC_DIR/build"
cp "$SRC_DIR/Makefile" "$SRC_DIR/tuling_ptzmotor.c" \
   "$SRC_DIR/ptz_ioctl.h" "$SRC_DIR/ptz_motion.h" "$SRC_DIR/build/"
make -C "$KERNEL_DIR" M="$SRC_DIR/build" ARCH=arm \
    CROSS_COMPILE="$CROSS_COMPILE" -j"${BUILD_JOBS:-4}" modules
"${CROSS_COMPILE}gcc" -std=c99 -Os -Wall -Wextra -Werror -static \
    "$SRC_DIR/ptzctl.c" -o "$SRC_DIR/build/ptzctl"
"${CROSS_COMPILE}gcc" -std=c99 -Os -Wall -Wextra -Werror -static \
    "$SRC_DIR/ptz_gpio_mux.c" -o "$SRC_DIR/build/ptz_gpio_mux"
cp "$SRC_DIR/ptz.sh" "$SRC_DIR/build/ptz.sh"
echo "产物在 $SRC_DIR/build；没有加载驱动或执行运动。"
