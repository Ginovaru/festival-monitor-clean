#!/usr/bin/env bash
set -euo pipefail
ts=$(date -u +'%Y%m%d')
mkdir -p "data/raw/$ts"

if [ -f config/sources.txt ]; then
  while IFS= read -r url; do
    [ -z "$url" ] && continue
    host=$(echo "$url" | awk -F/ '{print $3}' | tr ':' '_')
    echo ">> INIZIO: $url"
    # timeout totale di 15 secondi, poi passa avanti
    if timeout 15s curl -L --silent --show-error "$url" > "data/raw/$ts/${host}.html"; then
      echo ">> FINE: $url"
    else
      echo "!! ERRORE o TIMEOUT: $url"
    fi
  done < config/sources.txt
else
  echo "!! config/sources.txt mancante"
fi
