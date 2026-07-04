#!/usr/bin/env python3
"""Ciclo giornaliero: recupera Whoop + Yazio e aggiorna lo storico.

Uso: python3 scripts/daily_fetch.py [YYYY-MM-DD]   (default: oggi, Europe/Rome)

Cosa fa:
  1. Esegue fetch_whoop.py e fetch_yazio.py
  2. Salva i payload grezzi in data/raw/YYYY-MM-DD.json (per il resoconto)
  3. Estrae i campi dello schema e aggiorna la riga del giorno in
     data/history.jsonl (idempotente: se la data esiste già, la riga viene
     aggiornata preservando checkin e report_summary esistenti)

Se un fetch fallisce, l'altro viene comunque salvato: l'errore compare nel
JSON grezzo e lo script esce con codice 1 per segnalarlo.
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / "data" / "history.jsonl"
RAW_DIR = ROOT / "data" / "raw"


def run_fetch(script: str, *args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *args],
        capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        return {"error": (proc.stderr or proc.stdout).strip()[:1000]}
    return json.loads(proc.stdout)


def extract_whoop(raw: dict) -> dict:
    if "error" in raw:
        return {"error": raw["error"]}
    out = {}
    recs = raw.get("recovery") or []
    if isinstance(recs, list) and recs:
        score = recs[0].get("score") or {}
        out["recovery_pct"] = score.get("recovery_score")
        out["hrv_ms"] = score.get("hrv_rmssd_milli")
        out["rhr_bpm"] = score.get("resting_heart_rate")
    sleeps = raw.get("sleep") or []
    if isinstance(sleeps, list):
        main_sleeps = [s for s in sleeps if not s.get("nap")]
        if main_sleeps:
            s = main_sleeps[0]
            score = s.get("score") or {}
            out["sleep_efficiency_pct"] = score.get("sleep_efficiency_percentage")
            try:
                start = datetime.fromisoformat(s["start"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(s["end"].replace("Z", "+00:00"))
                out["sleep_hours"] = round((end - start).total_seconds() / 3600, 2)
            except (KeyError, ValueError):
                pass
    cycles = raw.get("cycle") or []
    if isinstance(cycles, list) and cycles:
        out["strain"] = (cycles[0].get("score") or {}).get("strain")
    workouts = raw.get("workout") or []
    if isinstance(workouts, list):
        out["workouts"] = []
        for w in workouts:
            entry = {"type": w.get("sport_name")}
            try:
                start = datetime.fromisoformat(w["start"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(w["end"].replace("Z", "+00:00"))
                entry["duration_min"] = round((end - start).total_seconds() / 60)
                entry["time_of_day"] = start.astimezone(ZoneInfo("Europe/Rome")).strftime("%H:%M")
            except (KeyError, ValueError):
                pass
            out["workouts"].append(entry)
    return out


def extract_yazio(raw: dict) -> dict:
    if "error" in raw:
        return {"error": raw["error"]}
    out = {}
    summary = raw.get("daily_summary") or {}
    if isinstance(summary, dict) and "error" not in summary:
        # struttura del widget: lasciamo i totali come arrivano
        for key in ("calories", "consumed", "nutrients", "steps", "water_intake"):
            if key in summary:
                out[key] = summary[key]
    weight = raw.get("weight_last")
    if isinstance(weight, dict) and "error" not in weight:
        out["weight_kg"] = weight.get("value")
    items = raw.get("consumed_items")
    if isinstance(items, (list, dict)) and "error" not in (items if isinstance(items, dict) else {}):
        out["consumed_items"] = items
    return out


def upsert_history(date: str, whoop: dict, yazio: dict) -> None:
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    if HISTORY.exists():
        lines = [json.loads(l) for l in HISTORY.read_text().splitlines() if l.strip()]
    existing = next((r for r in lines if r.get("date") == date), None)
    record = existing or {"date": date, "checkin": None, "report_summary": ""}
    record["whoop"] = whoop
    record["yazio"] = yazio
    if not existing:
        lines.append(record)
    lines.sort(key=lambda r: r.get("date", ""))
    HISTORY.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in lines))


def main() -> None:
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now(ZoneInfo("Europe/Rome")).strftime("%Y-%m-%d")
    whoop_raw = run_fetch("fetch_whoop.py")
    yazio_raw = run_fetch("fetch_yazio.py", date)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{date}.json"
    raw_path.write_text(json.dumps({"whoop": whoop_raw, "yazio": yazio_raw},
                                   indent=2, ensure_ascii=False))

    upsert_history(date, extract_whoop(whoop_raw), extract_yazio(yazio_raw))

    errors = [name for name, raw in (("whoop", whoop_raw), ("yazio", yazio_raw)) if "error" in raw]
    print(f"Storico aggiornato per {date}. Grezzi in {raw_path}")
    if errors:
        print(f"ATTENZIONE: fetch falliti: {', '.join(errors)} (dettagli nel file grezzo)")
        sys.exit(1)


if __name__ == "__main__":
    main()
