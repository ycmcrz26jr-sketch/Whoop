# Health Tracker — Resoconto giornaliero Whoop + Yazio

Resoconto giornaliero personalizzato che incrocia recovery/sonno/strain
(Whoop) con alimentazione (Yazio), un breve check-in soggettivo, e
suggerimenti su timing allenamento, qualità del cibo, timing integratori e
orario per dormire — con uno storico che cresce nel tempo.

## Architettura

Gira come **attività pianificata locale su Claude Code Desktop** (non come
Routine cloud): i connettori community per Whoop e Yazio sono server MCP
locali che le Routine cloud non possono raggiungere. Compromesso: serve PC
acceso + app Desktop aperta all'orario previsto (attiva "Keep computer
awake" nelle impostazioni per evitare lo stop).

## Struttura del progetto

| Percorso | Contenuto |
|---|---|
| `CLAUDE.md` | Istruzioni operative per Claude Code (ruolo, dati, check-in, stile) |
| `data/history.jsonl` | Storico: una riga JSON per giorno |
| `data/history.schema.json` | Schema della riga giornaliera, con esempio |
| `reports/` | Resoconti giornalieri in Markdown (`YYYY-MM-DD.md`) |
| `SUPPLEMENTS.md` | Il tuo stack integratori (da compilare) |

## Setup one-time (sul tuo computer)

1. Claude Code Desktop installato, abbonamento attivo
2. Node.js installato (Claude Code te lo segnala se manca)
3. Account sviluppatore gratuito su [developer.whoop.com](https://developer.whoop.com) → Client ID/Secret
4. Un connettore MCP per Whoop collegato (chiedi a Claude Code di cercare e
   installare un server MCP Whoop community e guidarti nell'OAuth)
5. Le tue credenziali Yazio pronte (email/password) — **attenzione**: Yazio
   non ha API ufficiale, i connettori usano un'API non documentata e possono
   rompersi con un aggiornamento dell'app
6. Clona questo repository in una cartella locale (es. `~/health-tracker/`)

## Ciclo giornaliero

1. L'attività pianificata parte da sola (es. alle 7:00)
2. Claude Code recupera i dati Whoop + Yazio delle ultime 24-48h e li
   aggiunge allo storico
3. Scrive una bozza di resoconto con i dati oggettivi, e segna le 2 domande
   di check-in ancora aperte
4. Quando apri l'app, rispondi alle 2 domande al volo e Claude completa il
   resoconto con quell'input (schema "bozza + completamento": uno scheduling
   che si fermi a metà in attesa di una risposta in tempo reale non è un
   comportamento garantito)

## Primi passi

1. Compila `SUPPLEMENTS.md` con il tuo stack integratori
2. Fatti guidare da Claude Code nell'installazione dei due connettori MCP
   (Whoop ufficiale via OAuth, Yazio community)
3. Fai un **run manuale** ("Run now") prima di programmarlo, per approvare i
   permessi una volta sola
4. Solo dopo che un run manuale funziona, attiva la pianificazione giornaliera
