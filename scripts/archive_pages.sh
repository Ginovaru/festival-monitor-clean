#!/usr/bin/env bash
set -euo pipefail

ts=$(date -u +'%Y%m%d')
root="data/raw/$ts"
mkdir -p "$root"

if [ ! -f config/sources.txt ]; then
  echo "!! config/sources.txt mancante" >&2
  exit 0
fi

while IFS= read -r url; do
  [ -z "$url" ] && continue
  host=$(echo "$url" | awk -F/ '{print $3}' | tr ':' '_')
  file="$root/${host}.html"
  echo ">> INIZIO: $url -> $file"
  # timeout duro: 15 secondi totali, 5 per connessione
  if timeout 15s curl -L --connect-timeout 5 --silent --show-error "$url" > "$file"; then
    echo ">> FINE:  $url"
  else
    echo "!! TIMEOUT/ERRORE: $url" >&2
  fi
done < config/sources.txt
