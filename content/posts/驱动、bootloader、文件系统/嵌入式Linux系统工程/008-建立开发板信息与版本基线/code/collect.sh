#!/bin/sh
set -eu
# /proc/self refers to each reader command, not a selected business process.
# Fixed allowlist: no environment, command lines, credentials or recursive traversal.
printf 'embedded Linux bounded read-only snapshot\n'
uname -srm
for file in /proc/uptime /proc/meminfo /proc/loadavg /proc/self/status /proc/self/limits /proc/self/cgroup /proc/net/dev; do
    printf '\nSOURCE %s (first 24 lines)\n' "$file"
    if [ -r "$file" ]; then
        sed -n '1,24p' "$file" || printf 'READ_FAILED %s\n' "$file"
    else
        printf 'UNAVAILABLE %s\n' "$file"
    fi
done
printf '\nEND snapshot; SDK, board revision and firmware manifest require manual entry\n'
