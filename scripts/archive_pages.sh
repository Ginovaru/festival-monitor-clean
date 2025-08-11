#!/usr/bin/env bash
set -euo pipefail
ts=$(date -u +'%Y%m%d')
mkdir -p "data/raw/$ts"
if [ -f config/sources.txt ]; then
  while IFS= read -r url; do
    [ -z "$url" ] && continue
    host=$(echo "$url" | awk -F/ '{print $3}' | tr ':' '_')
    echo ">> scarico $url"
    curl -L --max-time 30 --silent --show-error "$url" > "data/raw/$ts/${host}.html" || true
  done < config/sources.txt
fi
