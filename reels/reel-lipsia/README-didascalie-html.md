# Didascalie animate da pagina web

Aggiunta a `reel-lipsia`, non sostituzione: `build_standup.py` resta intatto e
continua a produrre la versione con le didascalie ferme disegnate in PIL.

## Perché

`caption_overlay()` in `build_standup.py` disegna **una PNG ferma** per beat e
la tiene immobile per tutta la sua durata. Su un reel in cui il testo *è* il
contenuto, questo è l'unico elemento che non si muove.

Per animarlo in PIL servirebbe ridisegnare ogni parola a ogni fotogramma, e
riscrivere a mano interpolazioni, easing e ritagli. Un browser fa già tutto
questo, e in `styleframe-promemoria.html` lo stavi già usando per progettare —
per poi ridisegnare lo stesso risultato a mano in `pipeline/styleframes.py`.
Questo pezzo elimina il secondo passaggio.

## Come funziona

```
content/timeline_v4.json        la stessa fonte unica di prima
        |
        +--> scripts/captions.html        pagina 1080x1920, sfondo trasparente
        |         window.seek(t) la porta a un istante e la lascia ferma li'
        |
        +--> scripts/render_captions.py   Chrome headless: seek -> screenshot,
        |         2385 volte               una PNG con alpha per fotogramma
        |
        +--> scripts/build_standup_html.py
                  montaggio di build_standup.py (Ken Burns, cover-crop 9:16)
                  + la sequenza PNG sovrapposta come maschera
                        |
                        v
                  dist/discarica-dei-libri-v5-html.mp4
```

La pagina non viene mai *riprodotta*: viene portata a un istante preciso e
fotografata. Nessuna animazione CSS, nessun `requestAnimationFrame` nel
render — ogni valore è funzione di `t`. Per questo lo stesso JSON produce
sempre gli stessi fotogrammi, anche su un computer lento, e correggendo una
parola il resto resta identico.

## Uso

```powershell
# 0. controlla la timeline prima di renderizzare (10 secondi)
.venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\check_timeline.py

# 1. anteprima nel browser, per regolare l'animazione senza renderizzare
.venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\render_captions.py --preview

# 2. prova rapida: un fotogramma al secondo
.venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\render_captions.py --every 25

# 3. sequenza completa (circa 5 minuti)
.venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\render_captions.py

# 4. montaggio
.venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\build_standup_html.py
```

## Cosa fa l'animazione

| Elemento | Comportamento |
|---|---|
| Blocco | dissolvenza in 0,22s, fuori in 0,18s |
| Parole | salgono di 0,55em con `easeOutCubic` in 0,30s, sfalsate |
| Sfasamento | si stringe da solo sui beat corti, non sfora mai il 60% del beat |
| Evidenziazione | il verde entra con una passata da sinistra sopra il testo già leggibile |

Le costanti sono in cima al blocco `<script>` di `captions.html`.

## Geometria: identica a PIL

Replicata da `caption_overlay()` per poter confrontare le due versioni:
larghezza utile 940px, scrim a tutta larghezza in `rgba(11,11,13,.647)`,
bordo inferiore a 260px dal fondo, corpo da 92px che scende di 4 in 4 fino a
52px finché il testo non sta in 4 righe, interlinea `(ascent+descent)*1.22`.

## Una correzione rispetto a PIL

`split_highlight()` spezza il testo sui confini dell'evidenziazione e
`wrap_words()` rimette uno spazio fra tutti i pezzi. Risultato nel v4: la
punteggiatura si stacca — «manuale della Trabant **?**», «la Trabant **.**».

`captions.html` evidenzia a livello di carattere dentro la parola: «Trabant?»
resta una parola sola, con «Trabant» in verde e «?» in osso.

Se vuoi correggerlo anche nella versione PIL, il punto è `split_highlight()`
in `build_standup.py`.

## Il controllo preventivo

`scripts/check_timeline.py` legge la timeline e si ferma prima del render.

Blocca (esce con codice 1):

- `highlight` che non esiste nel testo — altrimenti il verde sparisce in
  silenzio, senza nessun errore a runtime
- id immagine o clip inesistenti, con l'elenco di quelli disponibili
- `kind` sconosciuto, `duration` non valida, beat senza shot o senza testo
- testo che non entra in 4 righe nemmeno a 52px

Avvisa soltanto:

- oltre 25 caratteri al secondo: la battuta scorre troppo in fretta
- shot piu' corti di 0,6s: si leggono come un lampo
- meno di 0,8s di frase ferma dopo l'entrata dell'ultima parola
- asset presenti sul disco e mai usati nella timeline

L'impaginazione non e' stimata: la pagina viene aperta davvero in Chrome e
misurata, quindi corpo e numero di righe sono quelli che finiranno nel video.
Con `--no-browser` restano solo i controlli statici, senza avviare Chrome.

Le soglie editoriali sono costanti in cima al file: `MIN_SHOT_DUR`,
`MAX_CHARS_PER_SEC`, `MIN_READ_TAIL`.

## Dipendenze

`playwright` (nel venv) più il Chrome già installato — `channel="chrome"`,
nessun browser scaricato. Niente Node, niente `node_modules`, nessuna licenza
oltre a quelle che hai già.
