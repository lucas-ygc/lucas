#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p build
for name in motion speed; do
    "${CC:-cc}" -std=c99 -Wall -Wextra -Werror "${name}_test.c" -o "build/${name}_test"
    "build/${name}_test"
done
