#!/bin/sh
set -eu
src=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
work=$(mktemp -d "${TMPDIR:-/tmp}/linux-course.XXXXXX")
trap 'rm -rf -- "$work"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
"${CC:-cc}" -std=c11 -Wall -Wextra -Werror -g -O1 -pthread "$src/main.c" -o "$work/demo"
cd "$work"
./demo
