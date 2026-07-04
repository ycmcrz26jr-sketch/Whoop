#!/usr/bin/env python3
"""Recupera i dati Whoop (API ufficiale v2) delle ultime 48h.

Uso: python3 scripts/fetch_whoop.py            -> stampa JSON su stdout

Richiede WHOOP_CLIENT_ID e WHOOP_CLIENT_SECRET in ambiente e
data/whoop_tokens.json creato una volta con scripts/whoop_auth.py.

I refresh token Whoop sono rotanti: a ogni esecuzione il nuovo refresh
token viene risalvato subito in data/whoop_tokens.json — il file va poi
ricommittato perché il token sopravviva alla prossima sessione cloud.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
BASE_URL = "https://api.prod.whoop.com/developer/v2"
TOKENS_PATH = Path(__file__).resolve().parent.parent / "data" / "whoop_tokens.json"

COLLECTIONS = {
    "recovery": "/recovery",
    "sleep": "/activity/sleep",
    "cycle": "/cycle",
    "workout": "/activity/workout",
}


def refresh_access_token() -> str:
    if not TOKENS_PATH.exists():
        sys.exit("ERRORE: data/whoop_tokens.json mancante. "
                 "Esegui prima l'autenticazione one-time: scripts/whoop_auth.py (vedi SETUP.md).")
    tokens = json.loads(TOKENS_PATH.read_text())
    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "client_id": os.environ.get("WHOOP_CLIENT_ID", ""),
        "client_secret": os.environ.get("WHOOP_CLIENT_SECRET", ""),
        "scope": "offline",
    }).encode()
    req = urllib.request.Request(
        TOKEN_URL, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            new_tokens = json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"ERRORE refresh token Whoop ({e.code}): {e.read().decode()[:500]}\n"
                 "Se il refresh token è stato invalidato, rifai l'autenticazione con scripts/whoop_auth.py.")
    # Rotazione: salva SUBITO il nuovo refresh token, il vecchio è già invalido
    TOKENS_PATH.write_text(json.dumps(new_tokens, indent=2))
    return new_tokens["access_token"]


def get_paginated(path: str, access_token: str, start: str, end: str) -> list:
    records, next_token = [], None
    while True:
        params = {"start": start, "end": end, "limit": 25}
        if next_token:
            params["nextToken"] = next_token
        url = f"{BASE_URL}{path}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            page = json.load(resp)
        records.extend(page.get("records", []))
        next_token = page.get("next_token")
        if not next_token:
            return records


def main() -> None:
    access_token = refresh_access_token()
    now = datetime.now(timezone.utc)
    start = (now - timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    out = {}
    for name, path in COLLECTIONS.items():
        try:
            out[name] = get_paginated(path, access_token, start, end)
        except urllib.error.HTTPError as e:
            out[name] = {"error": f"HTTP {e.code}", "detail": e.read().decode()[:500]}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
