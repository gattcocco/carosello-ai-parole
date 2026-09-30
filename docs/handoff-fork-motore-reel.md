# HANDOFF — fork del motore reel (montaggio + testo animato)

*Settembre 2026. Scritto per chi apre un fork del progetto e vuole portarsi via
il motore nato sul reel Lipsia, senza l'episodio. Chi legge può essere una
persona o un assistente in una sessione nuova: qui c'è tutto quello che serve
per ripartire senza leggere la storia del progetto.*

Documenti collegati, da leggere dopo questo:
- `docs/metodo-reel-testo-animato.md` — il metodo e il perché delle scelte (9:16).
- `reels/reel-lipsia/HANDOFF.md` — lo stato dell'episodio Lipsia (v7 e v8).

---

## 1. In una riga

Il motore trasforma **un file JSON** (testi, tempi, inquadrature) in **un video
finito**: il testo animato è una pagina web fotografata fotogramma per
fotogramma in Chrome headless e sovrapposta a un montaggio moviepy, con
musica originale sintetizzata e titoli di coda a scorrimento.

Il riferimento da guardare per capire il risultato è
`reels/reel-lipsia/dist/discarica-dei-libri-v8-youtube.mp4` (16:9, 4:02).

---

## 2. Cosa portare nel fork

Oggi il motore vive dentro `reels/reel-lipsia/scripts/`. Nel fork conviene
metterlo in una cartella propria (es. `motore/`) e tenere gli episodi separati.

### Motore (generico, da copiare)

| File | Ruolo |
|---|---|
| `scripts/captions16.html` | Pagina didascalie **16:9** (1920×1080): parole animate, evidenziazione verde, cartelli-capitolo, citazioni, etichette. Guidata da `window.seek(t)` |
| `scripts/captions.html` | La stessa pagina in **9:16** (1080×1920), versione precedente: non ha capitoli, citazioni, `\|`, bilanciamento righe |
| `scripts/render_captions16.py` | Chrome headless: per ogni fotogramma `seek(t)` → screenshot PNG con alpha |
| `scripts/render_captions.py` | Idem per la pagina 9:16 (serve anche a `check_timeline.py`) |
| `scripts/build_fullscreen.py` | Libreria visiva: clip cover-crop, Ken Burns sulle immagini, **zoom indagine** (`focus_zoom_clip`), registro `IMAGE_SOURCES` |
| `scripts/build_standup.py` | `build_visual_shot()`: smista gli shot per `kind` |
| `scripts/build_standup_html.py` | Montaggio: concatena gli shot e sovrappone la sequenza PNG → video **muto** |
| `scripts/synth_newwave.py` | Sintetizzatore numpy della colonna sonora (new wave, Am–F–C–G). Durata come argomento |
| `scripts/assemble_v7.py` | Master: titoli di coda a scorrimento + concat + musica con fade. Versione come argomento |
| `scripts/compose_banknotes.py` | Esempio di **pre-composizione** di immagini con proporzioni sbagliate in card 16:9 o 9:16 |
| `scripts/check_timeline.py` | Controlli prima del render (**solo 9:16**, vedi §9) |
| `scripts/compose_cover.py` | Copertine per la griglia Instagram (9:16) |

### Specifici dell'episodio (da usare come esempio, non da copiare così)

- `scripts/make_credits_v8.py` — la lista dei crediti è scritta nel codice: va riscritta per ogni episodio.
- `content/timeline_v8.json` — la timeline di esempio più completa: usa tutti i campi e tutti i tipi di shot.
- `IMAGE_SOURCES` in `build_fullscreen.py` — gli id delle immagini di Lipsia vanno svuotati e sostituiti.

### Da NON portare

`build_discarica.py`, `generate_narration.py`, `timeline.json`…`timeline_v5.json`:
pipeline precedenti (voce TTS, PIL) superate. Stanno nell'episodio per storia.

---

## 3. Ambiente

| Cosa | Versione usata | Note |
|---|---|---|
| Python (venv) | 3.14 | moviepy 2.2.1, playwright 1.63, pillow 11.3, numpy 2.x, imageio-ffmpeg |
| Python di sistema | — | numpy + Pillow bastano per synth, crediti, assemble |
| Chrome installato | — | Playwright lo usa con `channel="chrome"` (niente download di Chromium) |
| ffmpeg nel PATH | 8.0 | usato da `assemble_v7.py` e per estrarre fotogrammi |

**Font di sistema (Windows)**: Bodoni MT Condensed Bold (`BOD_CB.TTF`) e la
famiglia Bodoni MT; Consolas; Liberation Serif; DejaVu Sans Mono. La pagina li
carica con `local(...)`: se mancano, Chrome ripiega **in silenzio** su un serif
qualsiasi e l'impaginazione cambia. Nel fork, se si passa a un'altra macchina,
conviene mettere i font in una cartella del progetto e dichiararli con
`@font-face src: url(...)`.

**Git**: `dist/`, clip, raw e tutte le immagini sono gitignorati (pesi e
diritti di terzi). Nel repo vanno solo codice, JSON e i `.md` delle fonti.

---

## 4. Architettura

```
content/timeline.json                      FONTE UNICA: testi, durate, shot, capitoli
        │
        ├─► captions16.html  ── render_captions16.py ──► dist/captions/frame_00000.png …
        │      (window.seek(t), deterministica)            una PNG con alpha per fotogramma
        │
        └─► build_standup_html.py
               shot per shot (build_fullscreen.py):
                 clip   → cover-crop 16:9
                 image  → Ken Burns (zoom lento verso il centro)
                 focus  → fermo immagine + mirino + zoom sul dettaglio
                 solid  → nero
               + sequenza PNG sovrapposta
                        ──► dist/<out_name_html>          MONTAGGIO MUTO
                                     │
   synth_newwave.py  → newwave.wav   │
   make_credits_vN.py → crediti PNG  │
                                     ▼
                        assemble_v7.py vN  ──►  dist/…-vN-youtube.mp4   MASTER
```

**Il principio che regge tutto: il determinismo.** La pagina non si riproduce
mai. Ogni proprietà visiva è funzione di `t`; il renderer chiama `seek(t)`,
aspetta, fotografa. Stesso JSON → stessi fotogrammi, bit per bit, anche su un
computer lento. Correggere una parola non sposta niente altro. Non introdurre
mai animazioni CSS, transizioni o `requestAnimationFrame` nella pagina: si
romperebbe questa proprietà.

---

## 5. La timeline: formato completo

```json
{
  "width": 1920, "height": 1080, "fps": 25,
  "out_name_html": "episodio-v1-yt.mp4",
  "beats": [
    { "chapter": { "title": "PLOTTENDORF", "sub": "A SUD DI LIPSIA · 22 LUGLIO 1991" },
      "text": null, "highlight": null, "duration": 2.5,
      "shots": [{ "source": "black", "kind": "solid" }] },

    { "text": "Indizio n. 1: «Kastanienallee», poesie di Elke Erb.",
      "highlight": "Elke Erb",
      "duration": 3.8,
      "label": "fotogramma 05:45",
      "cite": "Süddeutsche Zeitung · 2017",
      "shots": [{ "source": "plottendorf", "kind": "focus", "raw": "plottendorf",
                  "at": 345.5, "focus": [0.47, 0.36, 0.8] }] }
  ]
}
```

| Campo | Regola |
|---|---|
| `text` | Battuta a schermo. `null` = beat muto (nessuna fascia). ` \| ` (con spazi) = **a capo forzato** |
| `highlight` | Sottostringa **identica** di `text` (maiuscole comprese) o `null`. Se non combacia, il verde sparisce senza errore |
| `duration` | Secondi. La somma è la durata del corpo del video |
| `chapter` | `{title, sub}`: cartello-capitolo su nero. Usare con uno shot `solid` e `text: null` |
| `cite` | Citazione della fonte, in alto a destra (mono piccolo) |
| `label` | Etichetta del materiale, in alto a sinistra (es. archivio e anno, timecode) |
| `shots` | Uno o più; si dividono la `duration` in parti uguali |

**Tipi di shot**

| `kind` | Parametri | Uso |
|---|---|---|
| `clip` | `source` = nome in `assets/clips/*.mp4`, `seek` (s) | Filmato, cover-crop al formato |
| `image` | `source` = id in `IMAGE_SOURCES`, `zoom` | Ken Burns. 1.04 lento, 1.10 marcato, **1.0–1.03 per card grafiche** |
| `focus` | `raw` = id in `RAW_SOURCES`, `at` (s nel file originale), `focus` = `[cx, cy, larghezza]` in frazioni 0–1 del fotogramma | **Zoom indagine**: campo intero → mirino verde che si stringe → zoom sul dettaglio → fermo |
| `solid` | — | Nero pieno (cartelli, pause) |

Il riquadro finale di `focus` ha sempre le proporzioni dell'uscita. Tempi:
0–30% campo intero con mirino, 30–80% zoom con easing, poi fermo. **La fascia
del testo copre il 25–35% inferiore del frame** (dipende da 1, 2 o 3 righe):
il dettaglio da leggere va tenuto nella parte alta del riquadro finale.

---

## 6. Comandi

Dalla cartella dell'episodio. `VENV` = python del venv.

```bash
# anteprima dell'animazione nel browser, senza render
"$VENV" scripts/render_captions16.py timeline.json --preview

# prova rapida: 1 fotogramma al secondo in una cartella a parte (~20 s)
"$VENV" scripts/render_captions16.py timeline.json --every 25 --out /tmp/prova

# didascalie complete (~10 fotogrammi/s: ~8 min per 3:30)
"$VENV" scripts/render_captions16.py timeline.json

# montaggio muto (~20-25 min per 3:30)
"$VENV" scripts/build_standup_html.py timeline.json

# musica: durata = corpo + 34 s di crediti
python scripts/synth_newwave.py dist/audio/newwave-EPISODIO.wav 242.0

# master (crediti + concat + musica; fade-out calcolato da solo)
python scripts/assemble_v7.py v8
```

**Cosa rifare quando cambi cosa**

| Cambi | Rifai |
|---|---|
| `text`, `highlight`, `duration`, `cite`, `label`, `chapter` | didascalie + montaggio + master (+ musica se cambia la durata) |
| solo `shots` | montaggio + master |
| musica, crediti, volume | solo master |

**Due trucchi che fanno risparmiare ore**
1. **Prima di un render lungo, costruisci una volta ogni shot distinto** (un
   fotogramma ciascuno) chiamando `build_visual_shot()`: un id sbagliato fa
   morire il montaggio dopo venti minuti, così muore in dieci secondi.
2. **Controlla le didascalie con `--every 25`** e un provino (ritaglia la
   fascia in basso di ogni battuta e affiancale in una griglia): si vedono
   a capo sbagliati ed evidenziazioni spezzate prima di sprecare mezz'ora.

---

## 7. Parametri da ritarare

In cima a `captions16.html`:

| Costante | Valore | Cosa fa |
|---|---|---|
| `--safe` | 1500px | Larghezza massima del testo |
| `--bottom` | 60px | Distanza della fascia dal bordo inferiore |
| `--scrim-alpha` | 0.647 | Opacità della fascia scura |
| `MAX_FONT` / `MIN_FONT` | 78 / 44 | Corpo: parte dal massimo e scende a passi di 4 finché il testo sta in `MAX_LINES` |
| `MAX_LINES` | 3 | Righe massime |
| `WORD_DUR`, `RISE_EM`, `BLUR_MAX` | 0.44 s, 0.72 em, 9px | Entrata di ogni parola: sale, appare, si mette a fuoco |
| `WIPE_DUR`, `UL_DUR` | 0.40, 0.5 s | Passata verde e sottolineatura che si disegna |
| `CHAP_*`, `CL_STEP` | — | Cartello-capitolo: sottotitolo → riga dal centro → titolo lettera per lettera |

Due regole CSS che contano:
- `.lines { text-wrap: balance }` — righe di lunghezza simile, niente parola
  sola sull'ultima riga.
- `.hlgroup { white-space: nowrap }` — le parole evidenziate consecutive
  restano **sempre** sulla stessa riga. Senza, il bilanciamento spezza il verde.

**Cambiare formato** (es. 1080×1350 per il feed): non basta cambiare
`width`/`height` nel JSON. Vanno ricalcolati `--safe`, `--bottom`, i corpi e le
dimensioni di `html, body, #stage` nella pagina.

---

## 8. Consigli estetici per fare un bel reel

Tutti nati da difetti visti nel video, non da teoria.

### Storia

- **Apri sul fatto più inatteso, non sull'inizio cronologico.** Il reel Lipsia
  è migliorato quando l'hook è diventato Cassini («un libro buttato via è
  servito a una sonda per Saturno»). Il resto del video diventa la risposta a
  una domanda. Formula: *fatto sorprendente → domanda → «Andiamo con ordine»*.
- **Chiudi il cerchio.** L'hook va ripreso nel finale con le stesse parole o
  quasi («Il mercato lo aveva buttato via. Lui lo usò per arrivare a Saturno»).
- **Un aneddoto va nel capitolo in cui è successo.** Cassini stava nel capitolo
  della discarica ma era successo a Katlenburg anni dopo: lo spettatore sente
  il salto anche senza sapere perché. Prima di cercare un «ponte», controlla la
  cronologia sulla fonte.
- **Il ponte migliore è un esempio concreto** della frase prima («si possono
  ancora portare via» → «un ricercatore ci trovò il libro giusto»).
- **Il cliffhanger non si inventa, si trova**: è una domanda già presente nel
  testo («E i libri che restano invenduti?»).
- **L'indagine dà credibilità.** Mostrare il metodo («abbiamo riguardato il
  filmato fotogramma per fotogramma») e poi gli indizi con lo zoom `focus`
  trasforma l'archivio in prova. Regola ferrea: **solo quello che si legge
  davvero nel fotogramma**; il resto si attribuisce alla fonte scritta («altri
  nomi li riporta la stampa»). Un dettaglio che rima con la storia (il libro
  sulla cicogna che deve rifarsi il nido) vale più di un nome famoso.

### Testo a schermo

- **Una frase per battuta, 2–3 righe.** Il reel Lipsia gira a circa 18–20
  caratteri al secondo (mediana 18,6) ed è leggibile; oltre 25 no.
- **Affermazione, poi spiegazione**: se un'idea è difficile, due battute brevi
  sulla stessa clip (con `seek` diversi) invece di una lunga.
- **Il verde va sul cortocircuito, non sull'informazione**: «Ma non al mercato»,
  «arrivare a Saturno», «tirature intere». Mai su parole di servizio.
- **Un solo soggetto per frase.** «Li ha tenuti in vita una persona sola e…
  hanno cambiato nido» si legge come un errore; a schermo non c'è tempo per
  rileggere.
- **Niente metafore a due passaggi, niente aggettivi ambigui.**
- **A capo forzato** (` | `) sulle battute chiave, per farle cadere sulla pausa
  naturale: «Il mercato lo aveva buttato via. | Lui lo usò per arrivare a Saturno.»
- **Le card grafiche non portano didascalia** (`text: null`).

### Immagini e montaggio

- **Tagli netti dentro i capitoli, dip-to-black solo tra capitoli** (il cartello
  fa da transizione). Su un video da leggere il glitch disturba.
- **Codice colore con un significato**: bianco e nero = il sistema, il piano,
  l'ideale (film didattico 1951); colore = le cose vere (la discarica, i luoghi).
  Se l'alternanza è casuale sembra riempitivo.
- **Il materiale migliore non si usa per riempire**: se mostri la discarica sotto
  frasi che parlano d'altro, quando il testo la annuncia non è più una rivelazione.
- **Le immagini con le proporzioni sbagliate si pre-compongono** in una card del
  formato giusto (fondo inchiostro, oggetto intero, sopra la fascia del testo)
  e si usano con zoom 1.0–1.03. Esempio: `compose_banknotes.py`.
- **Scegli il lato che racconta**: delle banconote DDR funziona il **retro**
  (scene di vita: l'operaia al quadro comandi, i bambini che escono da scuola),
  non il fronte con i ritratti.
- **Etichette e citazioni** (`label`, `cite`) alla prima comparsa di un materiale
  o di un dato: danno il registro documentario senza appesantire il testo.
- **Misura la risoluzione prima di adottare un archivio**: 720×540 regge il
  16:9, 320×240 no. Lo zoom `focus` ingrandisce anche i difetti: sopra 2–2,5×
  sul 720×540 il testo si sgrana.

### Palette e tipografia (sistema Critical Inventory)

- Osso `#F2EFE9` per il testo, verde acido `#A6FF00` per l'evidenziazione e i
  mirini, inchiostro `#0B0B0D` per fondi e fasce. Il verde è **l'unico** colore
  d'accento: usarlo per una sola cosa per frase.
- Display: Bodoni MT Condensed Bold (didascalie, titoli). Mono piccolo e
  spaziato per citazioni, etichette, sottotitoli dei capitoli.

### Musica

- **Originale e sintetizzata** (`synth_newwave.py`): zero Content-ID su YouTube,
  e la stessa musica vale per YouTube, newsletter e sito.
- **Strumentale**: il testo da leggere e un testo cantato competono.
- **Arrangiamento ancorato alla fine**: il pad entra subito, l'arpeggio a 6 s,
  il basso a 12 s, la batteria a 18 s; la batteria esce 20 s prima della fine, cioè
  sul finale emotivo. Le uscite sono calcolate dalla durata totale, quindi
  basta passare la durata giusta.
- Volume del letto a 0.92 con fade-in 1,5 s e fade-out sugli ultimi 2,8 s.

### Crediti e copertina

- **Titoli di coda veri**: ogni filmato, foto, fonte e la musica. Rileggili a
  ogni versione: nella v7 citavano ancora una musica non più usata.
- La **copertina non è un fotogramma del video** (vedi `compose_cover.py` e
  §9 del metodo): titolo centrato, velo calcolato, verde sul cortocircuito.

---

## 9. Trappole note

- **`check_timeline.py` misura sulla pagina 9:16** (`captions.html`), non su
  `captions16.html`. Per il 16:9 i suoi controlli di impaginazione non valgono:
  nel fork va collegato a `captions16.html` (basta parametrizzare `PAGE`).
- **`dist/captions/` è unica per tutte le timeline.** Il renderer la svuota a
  ogni giro e il montaggio pretende il numero esatto di fotogrammi: rifai sempre
  le didascalie quando passi da una timeline all'altra.
- **I nomi dei file sono dell'episodio**: `assemble_v7.py` costruisce i percorsi
  `discarica-dei-libri-{versione}-…`, e i crediti si chiamano
  `make_credits_{versione}.py`. Nel fork: parametrizzare il nome del progetto.
- **Il log del montaggio può restare a 0 byte per minuti** mentre lavora (output
  bufferizzato): guarda la RAM del processo o l'mp4 che cresce.
- **Console Windows in cp1252**: niente caratteri non-ASCII nelle `print()`.
- **La musica deve durare quanto il video**: se cambi le durate e non rigeneri
  la musica, il fade-out cade nel punto sbagliato o il video si tronca
  (`-shortest`).
- **`focus` legge dal file raw** (`RAW_SOURCES` in `build_fullscreen.py`), non
  dalle clip estratte: il timecode `at` è quello del filmato originale.

---

## 10. Diritti

Regola operativa: **ogni asset ha una provenienza scritta prima di entrare nel
montaggio** (un `SOURCES.md` per episodio). Riassunto dalle esperienze:

| Fonte | Stato |
|---|---|
| NASA / JPL | Pubblico dominio, con credito |
| Wikimedia Commons CC BY-SA | Pulito, attribuzione nei crediti |
| Internet Archive con licenza dichiarata | Pulito |
| Internet Archive senza licenza | Caso per caso |
| Archivi civici o di movimento (es. KANAL X) | Chiedere prima di pubblicare |
| «L'azienda di Stato non esiste più» | **Non** vuol dire pubblico dominio: i diritti passano ai successori |

---

## 11. Primo giro nel fork (checklist)

1. Copia i file della §2 in `motore/`; crea un episodio con `content/`,
   `assets/clips/`, `assets/raw/`, `assets/images/`, `dist/`.
2. Svuota `IMAGE_SOURCES` e `RAW_SOURCES` e registra i tuoi asset.
3. Parte da `timeline_v8.json` di Lipsia come modello: tieni la struttura,
   sostituisci i beat.
4. `--preview`, poi `--every 25` + provino della fascia testo.
5. Costruisci una volta ogni shot distinto (§6, trucco 1).
6. Render completo → montaggio → musica (durata = corpo + crediti) → master.
7. Guarda il master a fotogrammi: hook, zoom `focus`, battute con verde su più
   parole, finale.
8. Crediti e `SOURCES.md` aggiornati prima di pubblicare.
