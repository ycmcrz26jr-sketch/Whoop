#!/usr/bin/env python3
"""Autenticazione one-time con Whoop (OAuth2 authorization code).

Uso:
  1) python3 scripts/whoop_auth.py url
     Stampa l'URL di autorizzazione da aprire nel browser (anche da telefono).
     Dopo il login Whoop reindirizza al redirect URI: copia il parametro
     `code=` dalla barra degli indirizzi.

  2) python3 scripts/whoop_auth.py <authorization_code>
     Scambia il codice con i token e salva data/whoop_tokens.json.

Variabili d'ambiente richieste:
  WHOOP_CLIENT_ID, WHOOP_CLIENT_SECRET
  WHOOP_REDIRECT_URI (deve coincidere esattamente con quello registrato
                      su developer.whoop.com)

NOTA: Whoop usa refresh token ROTANTI: ogni refresh invalida il precedente.
Per questo i token vivono in data/whoop_tokens.json (committato nel
repository privato) e non in una variabile d'ambiente statica.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
SCOPES = "read:recovery read:cycles read:sleep read:workout read:profile read:body_measurement offline"
TOKENS_PATH = Path(__file__).resolve().parent.parent / "data" / "whoop_tokens.json"


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(f"ERRORE: variabile d'ambiente {name} mancante. "
                 "Impostala nelle impostazioni dell'ambiente Claude Code (vedi SETUP.md).")
    return value


def build_auth_url() -> str:
    params = {
        "response_type": "code",
        "client_id": require_env("WHOOP_CLIENT_ID"),
        "redirect_uri": require_env("WHOOP_REDIRECT_URI"),
        "scope": SCOPES,
        "state": "healthtracker0000",  # >= 8 caratteri, richiesto da Whoop
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


def exchange_code(code: str) -> dict:
    body = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "client_id": require_env("WHOOP_CLIENT_ID"),
        "client_secret": require_env("WHOOP_CLIENT_SECRET"),
        "redirect_uri": require_env("WHOOP_REDIRECT_URI"),
    }).encode()
    req = urllib.request.Request(
        TOKEN_URL, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    if sys.argv[1] == "url":
        print(build_auth_url())
        return
    tokens = exchange_code(sys.argv[1])
    TOKENS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKENS_PATH.write_text(json.dumps(tokens, indent=2))
    print(f"Token salvati in {TOKENS_PATH}")
    print("Ricordati di committare data/whoop_tokens.json (repository privato!).")


if __name__ == "__main__":
    main()
