# Setup — tutto dal telefono, una volta sola

L'applicazione è già costruita e la routine giornaliera già programmata.
Restano solo i passaggi con le TUE credenziali, tutti fattibili dal telefono.

## 1. Sblocca la rete dell'ambiente

Nelle impostazioni dell'ambiente su [claude.ai/code](https://claude.ai/code)
(sezione ambienti → network policy) aggiungi ai domini consentiti:

- `api.prod.whoop.com`
- `yzapi.yazio.com`

Senza questo passaggio le sessioni cloud non possono raggiungere le API.

## 2. Inserisci le credenziali (variabili d'ambiente)

Sempre nelle impostazioni dell'ambiente, aggiungi queste variabili:

| Variabile | Valore |
|---|---|
| `YAZIO_EMAIL` | email del tuo account Yazio |
| `YAZIO_PASSWORD` | password del tuo account Yazio |
| `WHOOP_CLIENT_ID` | dal passaggio 3 |
| `WHOOP_CLIENT_SECRET` | dal passaggio 3 |
| `WHOOP_REDIRECT_URI` | lo stesso che registri al passaggio 3 |

## 3. Crea l'app Whoop (gratis, dal browser del telefono)

1. Vai su [developer.whoop.com](https://developer.whoop.com), accedi con il
   tuo account Whoop e crea una nuova app
2. Come **Redirect URI** registra ad esempio `https://example.com/callback`
   (serve solo a leggere il codice dalla barra degli indirizzi)
3. Come **scope** seleziona: recovery, cycles, sleep, workout, profile,
   body_measurement, offline
4. Copia Client ID e Client Secret nelle variabili del passaggio 2

## 4. Autorizza Whoop (one-time)

In una sessione Claude Code su questo repository scrivi:

> Esegui `python3 scripts/whoop_auth.py url` e dammi il link

Apri il link, accedi a Whoop e autorizza. Verrai rimandato al redirect URI:
dalla barra degli indirizzi copia il valore del parametro `code=...` e
incollalo in chat:

> Esegui `python3 scripts/whoop_auth.py <codice>` e committa i token

Questo salva `data/whoop_tokens.json`. **Nota**: Whoop usa refresh token
rotanti, quindi il file viene aggiornato e ricommittato a ogni esecuzione —
per questo il repository DEVE restare privato.

## 5. Run manuale di prova

In chat:

> Esegui il ciclo giornaliero (scripts/daily_fetch.py) e scrivi la bozza del resoconto

Se funziona, la routine delle 7:00 è già attiva e da domani va da sola.

## 6. Ogni giorno (da telefono)

1. La mattina ricevi la notifica: la bozza del resoconto è pronta in `reports/`
2. Apri la sessione, rispondi alle 2 domande di check-in
3. Claude completa il resoconto e aggiorna lo storico

## Risoluzione problemi

- **"CONNECT tunnel failed / 403"** → il dominio non è nella network policy
  (passaggio 1)
- **"ERRORE refresh token Whoop"** → il refresh token è stato invalidato
  (es. due esecuzioni in parallelo): rifai il passaggio 4
- **Errori Yazio** → l'API non è ufficiale e può cambiare senza preavviso;
  chiedi in chat di diagnosticare e aggiornare `scripts/fetch_yazio.py`
