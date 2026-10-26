#!/bin/sh
# Application-side wiring test only; 50 half-steps/s, no kernel motor driver.
set -eu
axis=${1:-h}
direction=${2:-forward}
steps=${3:-32}
case "$axis" in
    h) gpios="80 82 76 81" ;;
    v) gpios="0 74 77 75" ;;
    *) echo "Usage: $0 h|v [forward|reverse] [steps:1..128]" >&2; exit 2 ;;
esac
case "$direction" in forward) delta=1 ;; reverse) delta=7 ;; *) exit 2 ;; esac
case "$steps" in ''|*[!0-9]*) exit 2 ;; esac
[ "$steps" -ge 1 ] && [ "$steps" -le 128 ] || exit 2
command -v usleep >/dev/null || { echo 'usleep is required' >&2; exit 1; }
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
[ -x "$here/ptz_gpio_mux" ] || { echo 'Missing ptz_gpio_mux beside ptz.sh' >&2; exit 1; }
mkdir /run/ptz-gpio-test.lock || { echo 'Another GPIO test is running' >&2; exit 1; }
owned=""
touched=""
cleanup() {
    for gpio in $touched; do
        echo 0 > "/sys/class/gpio/gpio$gpio/value" 2>/dev/null || :
    done
    for gpio in $owned; do
        echo "$gpio" > /sys/class/gpio/unexport 2>/dev/null || :
    done
    rmdir /run/ptz-gpio-test.lock 2>/dev/null || :
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM HUP
for gpio in $gpios; do
    if [ ! -d "/sys/class/gpio/gpio$gpio" ]; then
        echo "$gpio" > /sys/class/gpio/export
        owned="$owned $gpio"
    else
        echo "Reusing exported GPIO$gpio"
    fi
    touched="$touched $gpio"
    echo low > "/sys/class/gpio/gpio$gpio/direction"
done
"$here/ptz_gpio_mux" "$axis"
echo "Test: axis=$axis direction=$direction half-steps=$steps speed=50"
phase=0
count=0
while [ "$count" -lt "$steps" ]; do
    case "$phase" in
        0) pattern=1 ;; 1) pattern=3 ;; 2) pattern=2 ;; 3) pattern=6 ;;
        4) pattern=4 ;; 5) pattern=12 ;; 6) pattern=8 ;; 7) pattern=9 ;;
    esac
    # Switch off before switch on to avoid transient extra energized coils.
    bit=1
    for gpio in $gpios; do
        if [ "$((pattern & bit))" -eq 0 ]; then echo 0 > "/sys/class/gpio/gpio$gpio/value"; fi
        bit=$((bit * 2))
    done
    bit=1
    for gpio in $gpios; do
        if [ "$((pattern & bit))" -ne 0 ]; then echo 1 > "/sys/class/gpio/gpio$gpio/value"; fi
        bit=$((bit * 2))
    done
    usleep 20000
    phase=$(((phase + delta) % 8))
    count=$((count + 1))
done
echo 'Finished; releasing coils.'
