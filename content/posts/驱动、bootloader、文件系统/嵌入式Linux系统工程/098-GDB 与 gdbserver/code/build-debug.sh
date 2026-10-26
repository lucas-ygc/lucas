#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")"
"${CC:-cc}" -std=c11 -g -O0 -Wall -Wextra -pthread main.c -o demo
printf 'built ./demo for manual debugging; run only on the matching architecture
'
