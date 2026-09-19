# Reel Lipsia — «La discarica dei libri»

Aprile 1991: alla fiera del libro di Lipsia si vede il collasso dell'editoria
della Germania Est. Poche settimane dopo, tonnellate di libri appena stampati
finiscono in una discarica a Plottendorf. Un pastore di paese, Martin Weskott,
vede la foto sul giornale, ci va con il furgone, e nel tempo organizza 150
viaggi in camion. Oggi quei libri — circa un milione — riempiono una chiesa e
un granaio in pietra a Katlenburg.

Formato: verticale 1080×1920, 25 fps, testo animato in sovrimpressione,
nessuna traccia audio (la musica si aggiunge da Instagram in pubblicazione).

## Stato

Pubblicato in due parti, da `timeline_v6.json`:

| | Durata | Copre |
|---|---|---|
| Parte 1 | 75,00s | Dall'hook al crollo dell'editoria dell'est, chiude su «E i libri che restano invenduti?» |
| Parte 2 | 67,88s | La discarica, il pastore, Katlenburg, la tesi |

Le due parti sono ritagliate dal montaggio intero al confine del beat 24: non
sono due render separati.

## Come si lavora

Il metodo completo — perché la pipeline è fatta così, le regole editoriali e
le trappole — sta in [`docs/metodo-reel-testo-animato.md`](../../docs/metodo-reel-testo-animato.md).
I comandi di questo episodio stanno in
[`README-didascalie-html.md`](README-didascalie-html.md).

In breve:

```powershell
# 1. controlla la timeline (10 secondi, prima di tutto)
.venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\check_timeline.py timeline_v6.json

# 2. didascalie: Chrome headless fotografa la pagina, una PNG per fotogramma
.venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\render_captions.py timeline_v6.json

# 3. montaggio
.venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\build_standup_html.py timeline_v6.json
```

Se cambi solo gli `shots` e non il testo, salti il passo 2.

## File

### In uso

| File | Ruolo |
|---|---|
| `content/timeline_v6.json` | **Fonte unica**: testo, evidenziazioni, durate, inquadrature |
| `scripts/captions.html` | La pagina animata. `window.seek(t)` la porta a un istante e la lascia ferma |
| `scripts/render_captions.py` | Cattura la sequenza PNG con canale alpha |
| `scripts/build_standup_html.py` | Monta il video sovrapponendo le PNG al footage |
| `scripts/check_timeline.py` | Valida la timeline prima del render |
| `scripts/build_fullscreen.py` | Registro degli asset (`IMAGE_SOURCES`) e utility di montaggio, importate dagli altri |
| `scripts/compose_banknotes.py` | Card 1080×1920 dalle scansioni delle banconote DDR |
| `scripts/compose_cover.py` | Copertine per la griglia del profilo |

### Storico

Versioni precedenti della stessa storia, tenute perché documentano le scelte
scartate. Non vanno usate per un reel nuovo.

| File | Cos'era |
|---|---|
| `scripts/build_standup.py` | Didascalie disegnate con Pillow: una PNG ferma per beat. Funziona ancora, ma il testo non si muove |
| `scripts/build_fullscreen.py` (`main`) | Versione con voce reale e transizioni glitch, senza testo a schermo |
| `scripts/build_discarica.py` | Primo montaggio |
| `scripts/generate_narration.py` | Traccia vocale via Gemini TTS, abbandonata |
| `content/timeline.json` … `timeline_v5.json` | Le versioni precedenti del testo |

Gli script storici hanno riferimenti che escono dalla cartella — il `.env` tre
livelli sopra, il font in `C:/Windows/Fonts` — quindi vanno sistemati se
qualcuno prova a rieseguirli.

## Asset e diritti

`assets/SOURCES.md` traccia provenienza e licenza di ogni singolo asset, ed è
il file da leggere prima di riusare qualcosa. In sintesi:

- **Pulito**: le foto di Katlenburg (Wikimedia Commons, CC BY-SA 3.0 e pubblico
  dominio), con attribuzione obbligatoria in didascalia
- **Da verificare**: i filmati di Plottendorf e la pubblicità Trabant
- **Non ridistribuibili**: la copertina del manuale Trabant e il ritratto di
  Weskott

Il `.gitignore` esclude `dist/`, `assets/raw/`, `assets/clips/`, `assets/scan/`
e tutti i binari: nel repo restano solo codice, timeline e file di provenienza.
Il materiale pesante resta sulla chiavetta.

## Dipendenze

`requirements.txt`. Playwright usa il Chrome già installato
(`channel="chrome"`): dopo il `pip install` non serve `playwright install`.
