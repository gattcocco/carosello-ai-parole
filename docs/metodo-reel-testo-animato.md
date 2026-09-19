# Metodo — reel a testo animato

Come sono fatti i reel di Critical Inventory dalla versione «discarica dei
libri» in poi. Non è la documentazione di un singolo episodio: è il metodo,
scritto perché il prossimo reel non debba riscoprirlo.

Nato lavorando su `reels/reel-lipsia`, settembre 2026.

---

## 1. L'architettura in una riga

Il testo animato è **una pagina web fotografata fotogramma per fotogramma**,
sovrapposta a un montaggio moviepy.

```
content/timeline_vN.json          fonte unica: testo, tempi, inquadrature
        |
        +--> scripts/check_timeline.py        10 secondi, prima di tutto
        |
        +--> scripts/captions.html            pagina 1080x1920, sfondo trasparente
        |         window.seek(t) la porta a un istante e la lascia ferma
        |
        +--> scripts/render_captions.py       Chrome headless: seek -> screenshot
        |         una PNG con alpha per ogni fotogramma
        |
        +--> scripts/build_standup_html.py    montaggio (Ken Burns, cover-crop 9:16)
                  + la sequenza PNG come maschera
                        |
                        v
                  dist/discarica-dei-libri-vN-html.mp4
```

### Perché una pagina web e non PIL

La versione precedente (`build_standup.py`, ancora presente e funzionante)
disegnava le didascalie con Pillow: una PNG ferma per beat, immobile per tutta
la sua durata. Su un reel in cui **il testo è il contenuto**, quello era
l'unico elemento che non si muoveva.

Per animarlo in PIL bisognerebbe ridisegnare ogni parola a ogni fotogramma e
riscrivere a mano interpolazioni, easing, ritagli, andata a capo e auto-fit del
corpo. `wrap_words()` e il ciclo `font_size -= 4` in `build_standup.py` sono
esattamente questo: CSS riscritto in Python, una proprietà per volta.

Il browser fa già tutto, e in `styleframe-promemoria.html` lo stavamo già
usando per progettare — per poi ridisegnare lo stesso risultato a mano in
`pipeline/styleframes.py`. La pipeline HTML elimina quel secondo passaggio.

### Il principio che tiene in piedi tutto: il determinismo

La pagina **non viene mai riprodotta**. Non c'è una sola animazione CSS, non
c'è `requestAnimationFrame` nel percorso di render. C'è una funzione:

```js
window.seek = function (t) {
  const p = easeOutCubic(clamp01((local - node.delay) / WORD_DUR));
  node.inner.style.transform = "translateY(" + ((1 - p) * RISE_EM) + "em)";
  node.inner.style.opacity = p;
}
```

Ogni valore è funzione di `t`. Conseguenze pratiche:

- lo stesso JSON produce sempre gli stessi fotogrammi, anche su un computer
  lento: il motore aspetta che ogni screenshot sia pronto prima di avanzare;
- correggendo una parola, tutto il resto resta identico bit per bit;
- una registrazione dello schermo non avrebbe nessuna di queste due proprietà.

È lo stesso principio di Remotion, ottenuto in 240 righe di HTML senza
dipendenze e senza vincoli di licenza.

---

## 2. I comandi

```powershell
# 0. controlla la timeline prima di spendere venti minuti
.venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\check_timeline.py timeline_v6.json

# 1. anteprima nel browser, per regolare l'animazione senza renderizzare
.venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\render_captions.py timeline_v6.json --preview

# 2. prova rapida: un fotogramma al secondo
.venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\render_captions.py timeline_v6.json --every 25

# 3. sequenza completa (circa 7 minuti per 140 secondi di reel)
.venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\render_captions.py timeline_v6.json

# 4. montaggio (circa 12 minuti)
.venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\build_standup_html.py timeline_v6.json
```

**Quando serve rifare cosa.** Se cambi `text`, `highlight` o `duration`
servono entrambi i render. Se cambi solo gli `shots` — quale clip, `zoom`,
`seek` — le didascalie non cambiano: salti il passo 3 e risparmi sette minuti.

Tutti e tre gli script prendono il nome della timeline come argomento
posizionale.

---

## 3. Il formato della timeline

```json
{
  "text": "Oggi sono un milione. Ogni domenica si possono ancora portare via.",
  "highlight": "un milione",
  "duration": 4.1,
  "shots": [
    { "source": "kat_libri", "kind": "image", "zoom": 1.1 },
    { "source": "pastore",   "kind": "image", "zoom": 1.05 }
  ]
}
```

| Campo | Regola |
|---|---|
| `text` | La battuta a schermo. `null` o vuoto = beat muto, nessuna fascia scura |
| `highlight` | Sottostringa **esatta** di `text`, oppure `null` |
| `duration` | Secondi. La somma è la durata del reel |
| `shots` | Uno o più. Si dividono la `duration` in parti uguali |
| `kind` | `image` (Ken Burns), `clip` (video, con `seek`), `solid` (nero pieno) |
| `zoom` | Solo `image`: 1.04 lento, 1.10 marcato, **1.0 per le card grafiche** |

Gli id degli asset stanno in `IMAGE_SOURCES` dentro `build_fullscreen.py`, e
le clip sono i nomi dei file in `assets/clips/*.mp4`.

---

## 4. Le regole editoriali, e da dove vengono

Nessuna di queste è teorica: ognuna è nata da un difetto visto nel video.

### Il codice colore

Il bianco e nero non è un ripiego, è un significato:

```
BIANCO E NERO  =  il sistema, il piano, l'astrazione
COLORE         =  le cose vere, i luoghi, gli oggetti
```

Nel reel Lipsia il bianco e nero è un film didattico americano del 1951
sull'organizzazione di una biblioteca — cioè **l'immagine di un sistema che si
racconta come vorrebbe essere**, che è esattamente il tema del blocco sulla
DDR. Il colore è il filmato vero della discarica.

Finché l'alternanza è casuale lo spettatore la legge come riempitivo. Con una
regola, diventa una cosa che sente senza saperla.

**Corollario che vale più della regola**: il materiale migliore non si usa per
riempire. Nella v5 il filmato della discarica compariva dal beat 13, e
ventisei secondi dopo il testo annunciava la discarica come se fosse una
rivelazione. Non lo era più: l'avevamo già mostrata sotto frasi che parlavano
d'altro.

### Le soglie di leggibilità

Sono costanti in cima a `check_timeline.py`, modificabili:

| Soglia | Valore | Perché |
|---|---|---|
| Caratteri al secondo | 25 | Sopra, la battuta scorre troppo per essere letta |
| Durata minima di uno shot | 0,6s | Sotto, l'inquadratura è un lampo |
| Coda di lettura | 0,8s | Secondi di frase ferma dopo l'entrata dell'ultima parola |
| Righe massime | 4 | Oltre, il corpo scende sotto i 52px |

**Il ritmo reale**: su 45 beat, la distribuzione sana è 2-3 righe. I beat a 4
righe vanno tenuti sotto i cinque, e non devono coincidere con i concetti più
astratti. La combinazione peggiore è l'idea più difficile nel blocco di testo
più fitto: è il caso in cui conviene spezzare in due beat da due righe.

Struttura che funziona nello spezzare: **affermazione, poi spiegazione.**

```
E la censura finiva per fare da pubblicità.
Se un libro riusciva a uscire, qualcosa doveva dire.
```

Tenendo i due beat sulla stessa clip con `seek` diversi, la scena continua e
le due righe si leggono come un pensiero solo invece che come due stacchi.

### Scrivere per lo schermo

- **Niente parole ambigue.** «Un libro critico» in italiano vuol dire due
  cose. Se l'ostacolo si può mettere nel verbo — «un libro che riusciva a
  uscire» — l'aggettivo non serve.
- **Niente metafore a due passaggi.** «La censura faceva da ufficio stampa»
  chiede di sapere cosa fa un ufficio stampa e poi di ribaltarlo. Quattro
  secondi non bastano.
- **Le card grafiche non portano didascalia.** La card finale della newsletter
  ha già la sua CTA: un overlay coprirebbe «Iscriviti». Si usa `"text": null`.

---

## 5. I controlli automatici

`check_timeline.py` gira in dieci secondi e ha salvato più volte un giro di
render da venti minuti. Ogni controllo è nato da un difetto reale.

**Bloccanti** (esce con codice 1):

| Controllo | Difetto che previene |
|---|---|
| `highlight` non presente nel testo | Il verde sparisce **in silenzio**, nessun errore a runtime |
| Id immagine o clip inesistente | Montaggio che muore a metà |
| Testo che non entra in 4 righe a 52px | Testo tagliato |
| `duration` ≤ 0, `kind` sconosciuto, beat senza shot | Crash |

**Avvisi**: velocità di lettura, shot troppo corti, coda di lettura, asset mai
usati, e — il più insidioso — **`seek` + durata dello shot oltre la durata
della clip**: `build_clip_shot` la rimanda da capo e a metà inquadratura si
vede un salto. Era successo in una versione già montata e guardata.

Il controllo dell'impaginazione **non è una stima**: apre `captions.html` in
Chrome, chiama `window.measure()` e legge corpo e numero di righe dal browser.
Quello che dice è quello che finirà nel video, perché non c'è un secondo
motore di layout che possa divergere.

---

## 6. La ricerca delle fonti

Il metodo che ha funzionato, in ordine.

**Partire da una fonte primaria in mano.** Per Lipsia: lo scan del *manifesto*
del 30 aprile 1991. Da lì escono i numeri verificabili — sei milioni di libri
l'anno, tiratura media ventitremila, 340 case editrici dall'ovest e 89
dall'est.

**Cercare la formulazione, non solo il dato.** Il passaggio più difficile del
reel — il rapporto fra Stato, censura e scrittori — è rimasto illeggibile
finché non è saltata fuori la frase della fonte: *pubblicati o non pubblicati,
gli scrittori venivano presi sul serio*. Quando un passaggio non funziona,
spesso la frase giusta è già nella fonte e non è stata cercata.

**Le recensioni valgono i saggi.** Di Darnton, *I censori all'opera*, le
recensioni integrali del *Giornale* e del *manifesto* hanno dato la tesi, il
metodo e il dato più forte — il piano editoriale del 1989 — senza bisogno del
volume.

**Distinguere sempre la prima dalla seconda mano.** I 625 titoli e gli 11
milioni di copie li abbiamo da Darnton *citato dal Giornale*. In didascalia va
scritto così.

**Il dettaglio più utile è quello che collega.** Il piano del 1989 prevedeva
cento titoli in più dell'anno prima — crescita pianificata nell'ultimo anno di
esistenza del paese. Non è una curiosità: è ciò che carica la quinta legge di
Ranganathan alla fine del reel. Un dato che non collega niente si taglia.

---

## 7. Diritti

Regola operativa: **ogni asset ha una provenienza scritta prima di entrare nel
montaggio**, in `assets/SOURCES.md` o in un `CREDITS.md` di cartella.

| Fonte | Stato |
|---|---|
| Wikimedia Commons, CC BY-SA | Pulito. Attribuzione in didascalia |
| Internet Archive con licenza dichiarata | Pulito |
| Internet Archive **senza** licenza, con dichiarazione dell'uploader | Da valutare caso per caso |
| Giphy | Da evitare: quasi tutto sono spezzoni di film caricati da utenti |

Attenzione alle dichiarazioni del tipo *«l'azienda statale non esiste più,
quindi è pubblico dominio»*: **è un ragionamento sbagliato.** L'estinzione di
un'impresa non estingue il diritto d'autore, che passa ai successori. Per i
filmati DDR i diritti sono spesso della DEFA-Stiftung.

E controllare sempre l'inquadratura prima di fidarsi: un filmato «DDR 1989»
trovato su Internet Archive aveva il logo di un'emittente tedesca attuale in
sovrimpressione — non era materiale d'epoca pulito, era la registrazione di
una trasmissione recente.

---

## 8. Trappole tecniche

**`MAX_PATH` su Windows.** Un progetto Node vuole una cartella con un percorso
**sotto i 100 caratteri**: il limite di sistema è 260 e il resto serve a
`node_modules`. Oltre, `CreateProcess` fallisce con un `ENOENT` che mente —
dice «file non trovato» su file presenti e funzionanti. L'impostazione di
registro `LongPathsEnabled` non risolve: non si applica alla creazione di
processi. Questa pipeline non usa Node e quindi non ha il problema, ma è la
ragione per cui non usa Node.

**Risoluzione degli asset.** Prima di adottare materiale d'archivio, misurarlo.
Per riempire 1080×1920 un 320×240 va ingrandito 8 volte ed è inutilizzabile a
tutto schermo; il materiale di Plottendorf è 720×540 e regge. Un candidato va
scartato se sgrana più di quello che già si usa.

**Immagini che non sono 9:16.** Le scansioni delle banconote sono quasi
quadrate: il cover-crop ne taglierebbe metà larghezza. Vanno pre-composte in
card 1080×1920 con `compose_banknotes.py` e usate con `zoom: 1.0`. Effetto
collaterale gradito: sul fondo nero del brand la fascia scura delle didascalie
diventa invisibile e il testo sembra appoggiato direttamente sulla card.

**La punteggiatura in PIL.** `split_highlight()` in `build_standup.py` spezza
il testo sui confini dell'evidenziazione e `wrap_words()` rimette uno spazio
fra tutti i pezzi: risultato, «manuale della Trabant **?**» con lo spazio. In
`captions.html` l'evidenziazione è a livello di carattere dentro la parola e
il problema non esiste. Se si usa ancora la versione PIL, il difetto è lì.

**Console Windows in cp1252.** Niente caratteri non-ASCII nelle `print()`
degli script: il `·` e la freccia fanno crashare. Nei file di testo va bene,
sullo standard output no.

---

## 9. Pubblicazione

Tre cose che si decidono dopo il render e che il video non contiene.

### La copertina non e' un fotogramma del reel

La griglia del profilo **ritaglia** il 9:16. La fascia delle didascalie sta in
basso, quindi qualunque fotogramma preso dal video perde il testo nel ritaglio.
E l'ultimo fotogramma — la card della newsletter — e' la scelta peggiore: nella
griglia dice «pubblicita'» a chi non ha ancora guardato niente.

`compose_cover.py` costruisce copertine apposta, con tre accorgimenti:

- **titolo centrato verticalmente**, cosi' sopravvive a qualunque ritaglio;
- **velo scuro calcolato**, non fisso: misura la luminosita' dietro il blocco di
  testo e la porta al valore leggibile. Su footage gia' buio resta a 60/255, su
  un fotogramma chiaro sale a 130. Un velo fisso spegneva le immagini scure;
- **etichetta «PARTE 1 / PARTE 2»** in verde spaziato sopra il titolo, quando il
  pezzo e' diviso: nella griglia si legge che sono una coppia.

Scegliere lo sfondo guardandolo **in miniatura**, non a piena risoluzione. Un
campo largo della discarica a dimensione griglia diventa carta astratta; una
foto con una figura umana si legge subito.

E la parola in verde va sul cortocircuito, non sull'informazione: «LA
**DISCARICA** DEI LIBRI DI LIPSIA» ferma lo scroll, «DI LIPSIA» in verde no.

### Dividere in due parti

Se il pezzo supera il minuto e mezzo conviene spezzarlo: due reel sono due
occasioni di distribuzione, e ciascuno sta meglio nel formato.

**Il taglio va al confine esatto di un beat**, cosi' nessuna didascalia viene
mozzata. Le durate si leggono dalla timeline, e il taglio si fa con ffmpeg sul
montaggio finito: **non serve rifare i render**.

```powershell
ffmpeg -i reel.mp4 -t 75.0 -c:v libx264 -crf 18 -an parte1.mp4
ffmpeg -ss 75.0 -i reel.mp4 -c:v libx264 -crf 18 -an parte2.mp4
```

Il punto giusto non e' la meta': e' **una domanda gia' presente nel testo**.
Nel reel Lipsia la parte 1 chiude su «E i libri che restano invenduti?» e la
parte 2 apre su «Finiscono in una discarica». Il cliffhanger non va inventato,
va trovato.

La parte 2 pero' resta senza contesto per chi ci capita sopra: il rimando alla
prima va nella didascalia, e se il pezzo gira vale la pena rifarla con tre
secondi di richiamo iniziale.

### La musica

Si aggiunge da Instagram in pubblicazione, perche' il montaggio esce muto.

La regola di partenza e' **strumentale**: 140 secondi di testo da leggere piu'
un testo cantato sono due flussi di parole in competizione. Ma la regola ha
un'eccezione utile: **una lingua che il pubblico non processa come lingua** non
compete. Per un pubblico italiano il tedesco funziona — e se il brano appartiene
al mondo del pezzo, smette di essere accompagnamento e diventa fonte.

Tempo intorno agli 80-100 BPM, registro documentario e non epico, traccia
uniforme senza stacchi: il pezzo ha gia' la sua struttura, e un crescendo
cadrebbe nel punto sbagliato. Volume basso.

**La musica di Instagram vale solo su Instagram.** Il file in `dist/` resta
muto, quindi per la newsletter, LinkedIn o il sito servirebbe una traccia a
licenza libera aggiunta al montaggio. Oggi la pipeline non lo fa: `audio=False`.

## 10. Cosa manca

**Il motore è dentro un episodio.** `captions.html`, `render_captions.py`,
`build_standup_html.py` e `check_timeline.py` non hanno niente di specifico
per Lipsia, ma stanno in `reels/reel-lipsia/scripts/`. Il prossimo reel li
copierebbe — che è esattamente la duplicazione già vista fra
`styleframe-promemoria.html` e `pipeline/styleframes.py`.

Vanno estratti in una cartella condivisa — `pipeline/reel-html/` o
`templates/reel-html/` — con i singoli episodi che la richiamano. Da fare
**prima** del secondo reel, non dopo il terzo.

**Riferimenti fuori dal repo — risolto.** `build_fullscreen.py` risolveva due
immagini con `ROOT.parent.parent.parent`, cioe' fuori dall'albero versionato.
Ora stanno in `assets/images/` e la pipeline non esce piu' dalla cartella
dell'episodio. Restano escluse da git per i diritti, e `SOURCES.md` sezione D
dice quali sono e da dove vengono.

Gli script legacy escono ancora: `generate_narration.py` cerca il `.env` tre
livelli sopra, `timeline_v2.json` punta a una traccia audio esterna, e
`build_standup.py` e `build_discarica.py` hanno il font a `C:/Windows/Fonts`.
Non toccano la pipeline a testo animato, ma vanno sistemati se qualcuno prova
a rieseguirli.

**Il formato feed.** La geometria delle didascalie è tarata sul 9:16:
`--bottom: 260px` e `--safe: 940px` in `captions.html`. Per un 1080×1350 non
basta cambiare `width` e `height` nella timeline: quei due valori vanno
ricalcolati.
