#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p build
"${CXX:-g++}" -std=c++17 -Wall -Wextra -Werror -pthread -I. \
    Ptz.cpp manager_test.cpp -Wl,--wrap=open -Wl,--wrap=close \
    -Wl,--wrap=ioctl -o build/manager_test
./build/manager_test
