#!/usr/bin/env python3
import os
import requests
from datetime import datetime
from urllib.parse import urlparse

# Percorso file con URL da scaricare
SOURCES_FILE = "config/sources.txt"

# Cartella di destinazione
today = datetime.now().strftime("%Y-%m-%d")
RAW_DIR = os.path.join("data", "raw", today)
os.makedirs(RAW_DIR, exist_ok=True)

if not os.path.exists(SOURCES_FILE):
    print(f"ERRORE: {SOURCES_FILE} non trovato")
    exit(1)

with open(SOURCES_FILE, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

if not urls:
    print("Nessun URL trovato in sources.txt")
    exit(1)

for url in urls:
    try:
        print(f"Scarico: {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()

        # Nome file basato sull'host e path
        parsed = urlparse(url)
        safe_name = parsed.netloc.replace(".", "_") + parsed.path.replace("/", "_")
        if not safe_name.endswith(".html"):
            safe_name += ".html"

        filepath = os.path.join(RAW_DIR, safe_name)
        with open(filepath, "wb") as out:
            out.write(r.content)

        print(f"Salvato in {filepath}")

    except Exception as e:
        print(f"ERRORE su {url}: {e}")

print("Download completato.")
