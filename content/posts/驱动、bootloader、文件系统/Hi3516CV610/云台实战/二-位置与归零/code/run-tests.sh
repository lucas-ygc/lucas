#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p build
"${CC:-cc}" -std=c99 -Wall -Wextra -Werror absolute_test.c -o build/absolute_test
./build/absolute_test
"${CC:-cc}" -std=c99 -Wall -Wextra -Werror home_test.c -Wl,--wrap=ioctl -o build/home_test
./build/home_test
