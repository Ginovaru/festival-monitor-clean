#!/usr/bin/env python3
import os
import requests
from datetime import datetime
from urllib.parse import urlparse

SOURCES_FILE = "config/sources.txt"
today = datetime.now().strftime("%Y-%m-%d")
RAW_DIR = os.path.join("data", "raw", today)
os.makedirs(RAW_DIR, exist_ok=True)

if not os.path.exists(SOURCES_FILE):
    print(f"ERRORE: {SOURCES_FILE} non trovato")
    raise SystemExit(0)

with open(SOURCES_FILE, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

if not urls:
    print("Nessun URL in sources.txt")
    raise SystemExit(0)

for url in urls:
    try:
        print(f"Scarico: {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        parsed = urlparse(url)
        safe = parsed.netloc.replace(".", "_") + parsed.path.replace("/", "_")
        if not safe.endswith(".html"):
            safe += ".html"
        path = os.path.join(RAW_DIR, safe)
        with open(path, "wb") as out:
            out.write(r.content)
        print(f"Salvato: {path}")
    except Exception as e:
        print(f"ERRORE su {url}: {e}")

print("Download completato.")
