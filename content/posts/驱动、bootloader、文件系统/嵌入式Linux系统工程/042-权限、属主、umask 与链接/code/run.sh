#!/bin/sh
set -eu
work=$(mktemp -d "${TMPDIR:-/tmp}/linux-links.XXXXXX")
trap 'rm -rf -- "$work"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
cd "$work"
printf 'data\n' >original
ln original hard
ln -s original soft
test "$(cat hard)" = data
test "$(cat soft)" = data
# Rename only our own temporary file; the hard link survives.
mv original renamed
test "$(cat hard)" = data
test -L soft
test ! -e soft
printf 'hard link survives rename; symbolic path is now dangling\n'
