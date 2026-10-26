#!/bin/sh
set -eu
work=$(mktemp -d "${TMPDIR:-/tmp}/linux-shell.XXXXXX")
trap 'rm -rf -- "$work"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
emit() { printf 'OUT\n'; printf 'ERR\n' >&2; }
emit >"$work/combined" 2>&1
(emit 2>&1 >"$work/out") >"$work/original"
test "$(cat "$work/combined")" = "$(printf 'OUT\nERR')"
test "$(cat "$work/out")" = OUT
test "$(cat "$work/original")" = ERR
status=0
sh -c 'exit 7' || status=$?
test "$status" -eq 7
printf 'redirection order verified; preserved failure status=%s\n' "$status"
