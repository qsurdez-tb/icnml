#!/usr/bin/env bash

VALUES=$(find . -name '*.asc' -exec gpg -d --yes {} 2>/dev/null \;)

echo ${VALUES} | grep -o 'ssss_key: [0-9]\+-[a-f0-9]\+' | cut -d':' -f2 | ssss-combine -q -t 2 2>&1

