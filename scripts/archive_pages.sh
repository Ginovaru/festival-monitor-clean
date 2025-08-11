#!/usr/bin/env bash
set -euo pipefail
ts=$(date -u +'%Y%m%d')
mkdir -p "data/raw/$ts"

if [ -f config/sources.txt ]; then
  while IFS= read -r url; do
    [ -z "$url" ] && continue
    host=$(echo "$url" | awk -F/ '{print $3}' | tr ':' '_')
    echo ">> Scarico $url"
    # timeout massimo 15 secondi per sito
    if ! curl -L --max-time 15 --silent --show-error "$url" > "data/raw/$ts/${host}.html"; then
      echo "!! Errore nel download di $url"
    fi
  done < config/sources.txt
else
  echo "!! config/sources.txt mancante"
fi
