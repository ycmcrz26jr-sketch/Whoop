#!/usr/bin/env python3
"""Recupera i dati Yazio del giorno (API non ufficiale v15).

Uso: python3 scripts/fetch_yazio.py [YYYY-MM-DD]   -> stampa JSON su stdout
     (default: oggi, fuso Europe/Rome)

Richiede YAZIO_EMAIL e YAZIO_PASSWORD in ambiente.

ATTENZIONE: Yazio non ha un'API ufficiale. Client ID/secret sono quelli
pubblici dell'app (documentati in github.com/saganos/yazio_public_api);
il tutto può rompersi con un aggiornamento dell'app.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

BASE_URL = "https://yzapi.yazio.com/v15"
# Credenziali client pubbliche dell'app Yazio (non sono segreti dell'utente)
CLIENT_ID = "1_4hiybetvfksgw40o0sog4s884kwc840wwso8go4k8c04goo4c"
CLIENT_SECRET = "6rok2m65xuskgkgogw40wkkk8sw0osg84s8cggsc4woos4s8o"

ENDPOINTS = {
    "consumed_items": "/user/consumed-items?date={date}",
    "daily_summary": "/user/widgets/daily-summary?date={date}",
    "weight_last": "/user/bodyvalues/weight/last?date={date}",
    "goals": "/user/goals/unmodified?date={date}",
}


def login() -> str:
    email = os.environ.get("YAZIO_EMAIL", "").strip()
    password = os.environ.get("YAZIO_PASSWORD", "").strip()
    if not email or not password:
        sys.exit("ERRORE: YAZIO_EMAIL / YAZIO_PASSWORD mancanti. "
                 "Impostale nelle impostazioni dell'ambiente Claude Code (vedi SETUP.md).")
    body = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": email,
        "password": password,
        "grant_type": "password",
    }).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/oauth/token", data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)["access_token"]
    except urllib.error.HTTPError as e:
        sys.exit(f"ERRORE login Yazio ({e.code}): {e.read().decode()[:500]}")


def main() -> None:
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now(ZoneInfo("Europe/Rome")).strftime("%Y-%m-%d")
    token = login()
    out = {"date": date}
    for name, path in ENDPOINTS.items():
        url = BASE_URL + path.format(date=date)
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                out[name] = json.load(resp)
        except urllib.error.HTTPError as e:
            out[name] = {"error": f"HTTP {e.code}", "detail": e.read().decode()[:500]}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
