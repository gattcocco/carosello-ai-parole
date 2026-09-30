# HANDOFF — reel Lipsia, versione YouTube v7

*Ultimo lavoro: settembre 2026. Questo file serve a «riattaccare la spina» da una sessione
nuova (anche con un altro account/assistente). Dice cos'è pronto, cosa manca, e come
rigenerare tutto dai file del progetto.*

---

## 0. AGGIORNAMENTO — v8 «Dalla discarica a Saturno» (settembre 2026)

La v8 riscrive lo storytelling attorno a Cassini. **Master:** `dist/discarica-dei-libri-v8-youtube.mp4` (~4:02).
Fonte unica: `content/timeline_v8.json` (il `_readme` interno spiega le scelte). La v7 resta rigenerabile.

- **Hook su Saturno** (NASA: fine missione 15/9/2017) → «come ci è arrivato un libro buttato via?»;
  il cerchio si chiude in OGGI: istituto Max Planck nello stesso comune → il libro giusto → Saturno.
  Cassini sta a Katlenburg, NON nella discarica (SZ: «in einem der Stapel» di Weskott, ~1997).
- **PLOTTENDORF come indagine:** nuovo tipo di shot `"kind": "focus"` (fermo immagine dal filmato
  originale + mirino verde + zoom; `at` = secondi nel raw, `focus` = [cx, cy, larghezza] in frazioni).
  Implementato in `build_fullscreen.focus_zoom_clip`. Indizi usati SOLO se leggibili: Elke Erb
  «Kastanienallee», Joachim Nowotny «Adebar und Kunigunde». Dettagli in `assets/SOURCES.md` sez. E.
- **Banconote DDR reinserite** in 16:9: `compose_banknotes.py --16x9` → `ddr-marchi/card16/`, id `marco16_*`.
- **Immagini NASA** (pubblico dominio): `nasa_dive`, `nasa_cassini`, `nasa_saturn` in `assets/images/nasa/`.
- **Crediti:** `make_credits_v8.py`. Corretto anche il refuso della v7 (citava ancora «Cylinder Five»
  come musica: la colonna sonora è nostra). Il master v7 va riassemblato per avere la correzione.
- Script generalizzati: `synth_newwave.py OUT.wav DURATA`, `assemble_v7.py v8` (fade-out automatico).

Rigenerare la v8:
```bash
"$VENV" scripts/render_captions16.py timeline_v8.json
"$VENV" scripts/build_standup_html.py timeline_v8.json
python scripts/synth_newwave.py dist/audio/newwave-lipsia-v8.wav 242.0   # corpo 208,0 + crediti 34
python scripts/assemble_v7.py v8
```
Nota: `dist/captions/` è condivisa tra v7 e v8 — rifare le didascalie quando si passa da una all'altra.

---

## 1. In una riga

È pronto un **reel storico-divulgativo per YouTube**, **nativo 16:9 (1920×1080)**, ~**3:33**,
con **colonna sonora originale** (new wave sintetizzata da noi) e **titoli di coda**.

**Master finale:** `dist/discarica-dei-libri-v7-youtube.mp4`

Questa è una *nuova pipeline 16:9* affiancata a quella verticale 9:16 (i reel Instagram in
due parti restano com'erano, vedi `README.md`). Le due pipeline **non si toccano**.

---

## 2. Cosa contiene la v7 (rispetto alla v6 verticale)

- **Formato YouTube**: 16:9 nativo, il footage riempie il frame (cover-crop), non più verticale.
- **Testi rivisti** con le fonti primarie (più precisi, storico-divulgativi):
  - Robert **Darnton, *I censori all'opera*** (capitolo DDR): la censura come «pianificazione»,
    il **permesso di stampa** (*Druckgenehmigung*), l'autocensura, «66 titoli in più» (non cento),
    «anche il mercato è una censura» attribuito al censore.
  - **Süddeutsche Zeitung 2017** (ritratto Weskott): refettorio **del XII secolo** (non «Milleduecento»),
    aneddoto **Cassini** con la formulazione esatta (un libro con la mistura di materiali per uno
    spettrofotometro), «Brot für die Welt», 130.000 €.
  - Fix di lettura dall'audit: `prete → pastore`; chiusura sull'agency («una persona sola, con
    un furgone») al posto di «da uno Stato a una chiesa»; tolto «bibliofilo radical chic»; numeri
    incoerenti 6 mln/23.000 rimossi (si usa la coppia coerente di Darnton 625/11 mln, 1989).
  - I testi definitivi sono la **fonte unica** `content/timeline_v7.json`.
- **Motion grafica professionale** (stessi colori del reel: osso `#F2EFE9`, verde acido `#A6FF00`,
  inchiostro `#0B0B0D`):
  - parole con *rise + fade + blur-in*; evidenziazione verde con **sottolineatura che si disegna**;
  - **cartelli-capitolo** (sottotitolo → riga dal centro → titolo lettera per lettera);
  - **citazioni fonte** a schermo (alto-dx) ed **etichette footage** (alto-sx, es. `Library
    Organization · USA · 1951`, `Bücherdeponie Plottendorf · 1991`).
- **Card CTA 16:9** dedicata (il poster newsletter è 9:16 e il cover-crop lo distruggerebbe).
- **Titoli di coda a scorrimento** con tutte le attribuzioni CC + Darnton.
- **Musica originale** (new wave, Am–F–C–G in minore, arp+delay, basso, pad, beat sobrio con
  sidechain), arrangiata sui 213,3s: intro → beat → ritiro dei tamburi sul finale emotivo.
  **100% nostra → zero Content-ID su YouTube.**

---

## 3. TODO / cosa resta aperto

- ⚠️ **Diritti dei filmati** (unico nodo non risolto, già in `assets/SOURCES.md`): prima di una
  pubblicazione pubblica su YouTube vanno chiariti **Plottendorf (KANAL X / Archiv
  Bürgerbewegung Leipzig e.V.)** e la **pubblicità Trabant 601 (1969)**. Le foto Katlenburg
  (CC BY-SA) e la musica sono a posto. L'audio è nostro.
- Possibili rifiniture (facoltative): una **linea melodica/lead** o un **breakdown** a metà nella
  musica; volume del letto sotto il testo; velocità dei titoli di coda; **copertina + descrizione
  YouTube**.
- La numerazione a schermo: microtesto `PAROLA NN/08` non è usato nella v7 (era della v6); qui
  non c'è contatore. Ok così.

---

## 4. File nuovi creati per la v7 (tutti nel progetto)

| File | Ruolo |
|---|---|
| `content/timeline_v7.json` | **Fonte unica** v7: testi, durate, shot, + campi nuovi `cite`, `label`, `chapter` |
| `scripts/captions16.html` | Pagina didascalie **16:9** con cartelli, citazioni, etichette e la motion grafica |
| `scripts/render_captions16.py` | Renderer PNG per la pagina 16:9 (copia di `render_captions.py`, `PAGE=captions16.html`) |
| `scripts/synth_newwave.py` | **Sintetizzatore** della colonna sonora (numpy). Rigenera `newwave.wav` |
| `scripts/make_credits_v7.py` | Genera `credits_tall.png` (immagine alta dei titoli di coda) |
| `scripts/assemble_v7.py` | **Ricompone il master** finale (crediti + concat + musica) con un comando |
| `assets/images/cta16-1080.png` | Card CTA 16:9 (registrata come `cta16` in `build_fullscreen.py`) |
| `dist/audio/newwave-lipsia.wav` / `.mp3` | La colonna sonora renderizzata (master + mp3) |
| `dist/discarica-dei-libri-v7-yt.mp4` | **Montaggio muto** 16:9 (corpo, senza musica/crediti) — intermedio pesante da riusare |
| `dist/discarica-dei-libri-v7-youtube.mp4` | **MASTER finale** (video + musica + titoli di coda) |
| `dist/captions/*.png` | 4445 PNG delle didascalie animate (rigenerabili) |

`scripts/build_fullscreen.py` è stato modificato in un punto: aggiunto l'id `cta16` a `IMAGE_SOURCES`.

> Nota: `dist/`, `assets/clips/`, `assets/raw/`, `assets/images/` sono **gitignorati** (binari pesanti):
> restano sulla chiavetta, non nel repo.

---

## 5. La pipeline v7 (16:9) — come funziona

```
content/timeline_v7.json                  fonte unica (testi, tempi, shot, cite/label/chapter)
        │
        ├─► scripts/captions16.html        pagina 1920×1080, animata, guidata da window.seek(t)
        │        scripts/render_captions16.py  →  dist/captions/frame_*.png (PNG con alpha)
        │
        └─► scripts/build_standup_html.py timeline_v7.json
                 footage cover-crop 16:9 (build_fullscreen.py) + PNG sovrapposte
                        →  dist/discarica-dei-libri-v7-yt.mp4   (MUTO)
                                     │
   scripts/synth_newwave.py  ─────┐  │
        → newwave.wav            │  │
   scripts/make_credits_v7.py ───┼──┤
        → credits_tall.png       │  │
                                 ▼  ▼
                    scripts/assemble_v7.py
             (scroll crediti + concat + letto musicale)
                        →  dist/discarica-dei-libri-v7-youtube.mp4   (MASTER)
```

I **cartelli-capitolo** fanno da transizione (dip-to-black); dentro le sezioni, tagli netti
(principio del metodo: su un video da leggere il glitch disturba). Vedi
`../../docs/metodo-reel-testo-animato.md` per il metodo generale.

---

## 6. Comandi per rigenerare

Due ambienti Python:
- **venv** (per Playwright/moviepy): `"C:/Users/web/Desktop/Critical Inventory - USB - 2026-09-11/.venv/Scripts/python.exe"`
- **python di sistema** (numpy/Pillow, per synth/crediti/CTA/assemble): `python`

Font richiesti (Windows): **Bodoni MT Condensed Bold** (`BOD_CB.TTF`) e la famiglia Bodoni,
**Consolas**, **Liberation Serif**, **DejaVu Sans Mono** (per le mono). Chrome installato
(Playwright usa `channel="chrome"`).

### A. Da zero (tutto)
```bash
VENV="C:/Users/web/Desktop/Critical Inventory - USB - 2026-09-11/.venv/Scripts/python.exe"
cd ".../PROGETTO/reels/reel-lipsia"

# 1) didascalie animate 16:9  (~13 min, Chrome headless)
"$VENV" scripts/render_captions16.py timeline_v7.json
#    prova rapida di geometria: aggiungi  --every 25

# 2) montaggio muto 16:9  (~20-25 min, moviepy)  -> dist/discarica-dei-libri-v7-yt.mp4
"$VENV" scripts/build_standup_html.py timeline_v7.json

# 3) musica originale (se va rigenerata)  -> newwave.wav (~45s)
python scripts/synth_newwave.py dist/audio/newwave-lipsia.wav

# 4) master finale (crediti + concat + musica)  -> dist/discarica-dei-libri-v7-youtube.mp4
python scripts/assemble_v7.py
```

### B. Solo ri-assemblaggio (se cambi musica/crediti/volume, NON i testi)
Il montaggio muto e le didascalie NON vanno rifatti:
```bash
python scripts/assemble_v7.py
```
- cambiare la **musica**: rilancia `synth_newwave.py` (modifica BPM/progressione/arrangiamento
  dentro lo script), poi `assemble_v7.py`.
- cambiare i **crediti**: modifica la lista `C` in `make_credits_v7.py`, poi `assemble_v7.py`.
- cambiare **volume/fondu** musica: i parametri sono in `assemble_v7.py` (step 4).

### C. Cambiare i TESTI
Modifica `content/timeline_v7.json` → rifai **A.1 + A.2 + A.4** (le didascalie e il montaggio,
poi l'assemblaggio). Se cambi solo gli `shot` (non il testo), salti A.1.

> Anteprima animazioni senza render lungo: `scratchpad/preview_anim.py` mostrava il metodo
> (render di una finestra temporale a 25fps per contact-sheet); non è nel progetto ma è
> ricostruibile in 30 righe con Playwright.

---

## 7. Fonti dei testi (fuori dal repo)

Nella cartella esterna `../../../nuovi materiali per reel libri lipsia/`:
- `I_censori_allopera.pdf` — Darnton, capitolo DDR «LA GERMANIA COMUNISTA» da **p.142**.
- `Ritratto - Il pastore del libro - ... SZ.de.pdf` — ritratto Weskott (refettorio XII sec.,
  Cassini, 150 viaggi, Brot für die Welt).
- `articolo manifesto.pdf` — il manifesto 30/4/1991 (fiera Lipsia, 340/89, Aufbau 180→55).

Tutte le attribuzioni e lo stato dei diritti sono in `assets/SOURCES.md` e
`assets/images/katlenburg/CREDITS.md`.

---

## 8. Gotcha / note

- **`cta_newsletter` e `marco_*` sono 9:16**: in 16:9 il cover-crop li distrugge → non usarli.
  Per la CTA c'è `cta16` (già in `IMAGE_SOURCES`).
- **La geometria delle didascalie in `captions16.html`** è tarata per 1920×1080
  (`--safe:1500`, `--bottom:60`, `MAX_LINES 3`, font 44–78). Per un altro formato vanno ritarati.
- **Log dei render** su file sono *buffered*: durante moviepy il `.log` può restare a 0 byte a
  lungo pur lavorando (guarda la RAM del processo o il crescere dell'mp4 in `dist/`).
- Il montaggio moviepy è **lento** (compone 4445 PNG maschera + footage): ~20-25 min. Normale.
- Intermedi dell'assemblaggio in `dist/_build/` (rigenerabili, cancellabili).
