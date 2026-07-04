# Health Tracker — Resoconto giornaliero Whoop + Yazio

Resoconto giornaliero personalizzato che incrocia recovery/sonno/strain
(Whoop) con alimentazione (Yazio), un breve check-in soggettivo, e
suggerimenti su timing allenamento, qualità del cibo, timing integratori e
orario per dormire — con uno storico che cresce nel tempo.

## Architettura (100% cloud — funziona dal telefono)

Tutto gira come **Routine cloud di Claude Code**: nessun PC acceso, nessuna
app Desktop, nessun connettore MCP locale. Al posto dei connettori, script
Python senza dipendenze che chiamano direttamente le API:

- **Whoop**: API ufficiale v2 (`api.prod.whoop.com`), OAuth2 con refresh
  token rotanti persistiti in `data/whoop_tokens.json`
- **Yazio**: API non ufficiale v15 (`yzapi.yazio.com`), login email/password —
  può rompersi con un aggiornamento dell'app

Le credenziali vivono nelle variabili d'ambiente dell'ambiente Claude Code,
mai nel repository (eccetto i token OAuth Whoop, che richiedono repository
privato). Setup completo in **[SETUP.md](SETUP.md)**.

## Struttura del progetto

| Percorso | Contenuto |
|---|---|
| `CLAUDE.md` | Istruzioni operative per Claude Code (ruolo, dati, check-in, stile) |
| `SETUP.md` | I passaggi one-time che restano tuoi (tutti fattibili da telefono) |
| `scripts/whoop_auth.py` | Autorizzazione OAuth Whoop one-time |
| `scripts/fetch_whoop.py` | Fetch dati Whoop ultime 48h |
| `scripts/fetch_yazio.py` | Fetch dati Yazio del giorno |
| `scripts/daily_fetch.py` | Orchestratore: fetch + aggiornamento storico |
| `data/history.jsonl` | Storico: una riga JSON per giorno |
| `data/history.schema.json` | Schema della riga giornaliera, con esempio |
| `data/raw/` | Payload API grezzi per giorno |
| `reports/` | Resoconti giornalieri in Markdown (`YYYY-MM-DD.md`) |
| `SUPPLEMENTS.md` | Il tuo stack integratori (da compilare) |

## Ciclo giornaliero

1. La routine cloud parte da sola ogni mattina (~7:00 ora italiana)
2. La sessione esegue `scripts/daily_fetch.py`: dati Whoop + Yazio delle
   ultime 24-48h nello storico
3. Scrive una bozza di resoconto con i dati oggettivi e le 2 domande di
   check-in aperte, poi committa e pusha — ricevi la notifica sul telefono
4. Quando apri l'app, rispondi alle 2 domande e Claude completa il resoconto
   (schema "bozza + completamento")

## Primi passi

1. Segui **[SETUP.md](SETUP.md)**: network policy, credenziali, OAuth Whoop
2. Compila `SUPPLEMENTS.md` con il tuo stack integratori
3. Fai un run manuale in chat prima di fidarti della routine
