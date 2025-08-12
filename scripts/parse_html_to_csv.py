from pathlib import Path
from datetime import datetime
import re
import pandas as pd
from bs4 import BeautifulSoup

RAW_DIR = Path("data/raw")
CSV = Path("data/records.csv")
CSV.parent.mkdir(parents=True, exist_ok=True)

# mapping host -> nome festival "umano"
FESTIVAL_BY_HOST = {
    "www.premioubu.it": "Ubu",
    "premioubu.it": "Ubu",
    "www.riccioneteatro.it": "Riccione",
    "riccioneteatro.it": "Riccione",
    "www.associazionescenario.it": "Scenario",
    "associazionescenario.it": "Scenario",
    "www.hystrio.it": "Hystrio",
    "hystrio.it": "Hystrio",
    "www.inboxproject.it": "In-Box",
    "inboxproject.it": "In-Box",
    "www.centroelteatro.it": "Dante Cappelletti",
    "centroelteatro.it": "Dante Cappelletti",
    "www.milanooff.com": "Milano Off",
    "milanooff.com": "Milano Off",
}

KEYWORDS = {
    "vincitore": "vincitore",
    "vincitrice": "vincitore",
    "menzione": "menzione",
    "premio": "premio",
    "finalista": "finalista",
}

def latest_snapshot_dir(root: Path) -> Path | None:
    if not root.exists():
        return None
    dirs = [d for d in root.iterdir() if d.is_dir() and d.name.isdigit()]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.name)[-1]

def load_existing(csv_path: Path) -> pd.DataFrame:
    if csv_path.exists():
        try:
            return pd.read_csv(csv_path)
        except Exception:
            pass
    cols = ["festival","edizione","anno","opera","autore","compagnia","categoria",
            "esito","motivazione","temi","forma","fonte_url","data_rilevazione"]
    return pd.DataFrame(columns=cols)

def infer_festival_from_filename(name: str) -> str:
    host = name.replace(".html","")
    return FESTIVAL_BY_HOST.get(host, host)

def extract_candidates(text: str) -> list[dict]:
    """
    Prende il testo di una pagina e ritorna righe "candidate"
    molto grezze: cerca righe con parole chiave, estrae un titolo tra virgolette
    o una sequenza in Maiuscolo come nome opera, altrimenti lascia vuoto.
    """
    results = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    year_now = datetime.now().year
    for ln in lines:
        ln_low = ln.lower()
        hit = None
        for k,v in KEYWORDS.items():
            if k in ln_low:
                hit = v
                break
        if not hit:
            continue

        # prova a pescare un possibile titolo tra virgolette
        m = re.search(r'“([^”]{3,80})”|\"([^"]{3,80})\"', ln)
        title = m.group(1) or m.group(2) if m else ""

        # in mancanza, tenta parole con iniziali maiuscole
        if not title:
            caps = re.findall(r'\b([A-Z][A-Za-zÀ-ÖØ-öø-ÿ0-9’\'\-]{2,})\b', ln)
            title = " ".join(caps[:5]) if caps else ""

        # motivazione: uno spezzone ripulito
        motiv = re.sub(r'\s+', ' ', ln)
        results.append({
            "anno": year_now,
            "opera": title.strip(),
            "esito": hit,
            "motivazione": motiv[:400],
        })
    return results

def main():
    snap = latest_snapshot_dir(RAW_DIR)
    if not snap:
        print("Nessuno snapshot in data/raw. Salto.")
        return

    df = load_existing(CSV)
    existing_keys = set(
        (str(r.get("festival","")), str(r.get("opera","")), int(r.get("anno",0)))
        for _, r in df.fillna("").iterrows()
    )

    new_rows = []
    for html in sorted(snap.glob("*.html")):
        festival = infer_festival_from_filename(html.name)
        try:
            soup = BeautifulSoup(html.read_text(encoding="utf-8", errors="ignore"), "lxml")
            text = soup.get_text(" ", strip=True)
        except Exception:
            continue

        for cand in extract_candidates(text):
            key = (festival, cand["opera"], int(cand["anno"]))
            if key in existing_keys:
                continue
            row = {
                "festival": festival,
                "edizione": "",
                "anno": cand["anno"],
                "opera": cand["opera"],
                "autore": "",
                "compagnia": "",
                "categoria": "drammaturgia",
                "esito": cand["esito"],
                "motivazione": cand["motivazione"],
                "temi": "",
                "forma": "",
                "fonte_url": f"(snapshot){html.name}",
                "data_rilevazione": datetime.now().strftime("%Y-%m-%d"),
            }
            new_rows.append(row)
            existing_keys.add(key)

    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        df.to_csv(CSV, index=False, encoding="utf-8")
        print(f"Aggiunte {len(new_rows)} righe da HTML.")
    else:
        print("Nessuna nuova riga trovata.")

if __name__ == "__main__":
    main()
