from pathlib import Path
from datetime import datetime
import pandas as pd

data = Path("data/records.csv")
reports = Path("reports"); reports.mkdir(parents=True, exist_ok=True)
out = reports / "ultimo_report.md"

if not data.exists():
    out.write_text("# Report festival – nessun dato\n", encoding="utf-8")
    raise SystemExit(0)

df = pd.read_csv(data)
if "anno" in df.columns:
    df["anno"] = pd.to_numeric(df["anno"], errors="coerce")

now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

# ultimi ~12 mesi (grezzo)
recent = df
if df["anno"].notna().any():
    recent = df[df["anno"] >= df["anno"].max() - 1]

by_fest = recent.groupby("festival")["opera"].count().sort_values(ascending=False)

keys = ["linguaggio","drammaturgia","innovazione","politico","sociale","corpo","regia","ibridazione","struttura","emotivo"]
motifs = {k:0 for k in keys}
for s in df["motivazione"].dropna().astype(str).str.lower():
    for k in keys:
        if k in s:
            motifs[k]+=1
motifs_series = pd.Series(motifs).sort_values(ascending=False)

lines = []
lines.append(f"# Report festival – aggiornato {now}\n")
lines.append("## Trend ultimi 12 mesi (conteggio opere segnalate)")
lines.append(by_fest.to_markdown() if len(by_fest) else "_Nessun dato_")
lines.append("\n## Pattern ricorrenti nelle motivazioni")
lines.append(motifs_series.to_frame("occorrenze").to_markdown() if motifs_series.sum() else "_Nessun pattern rilevato_")
out.write_text("\n\n".join(lines), encoding="utf-8")
