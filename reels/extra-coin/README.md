# Extra Coin

Reel-recensione muto e ultra-discorsivo sul gioco di CINIC Games. Il paper edit
v0.5 dura 52 secondi: prima identifica l'opera e spiega protagonista,
obiettivo e gameplay; poi racconta il conflitto fra la noia coerente con la
prigione narrativa del Loop e una noia che resta comunque poco divertente da
giocare.

## Stato

- [x] Recensione sorgente preservata in `content/review-source.docx`
- [x] Nove screenshot 16:9, key art e frame di Mika ordinati in `assets/screenshots/`
- [x] Recensione riletta integralmente e dati di uscita verificati
- [x] Template ultra-discorsivo definito in `content/template-discorsivo.md`
- [x] Narrazione continua v0.5 aggiornata a 172 parole
- [x] Storyboard, copy e SRT riallineati al paper edit da 52 secondi
- [x] Formato bloccato: master muto + testo on-screen, senza voice-over
- [x] Footage ufficiale CINIC Games scaricato e inventariato localmente
- [x] Due GIF meme selezionate, rinominate e inventariate
- [ ] Scelta della musica su Instagram e caption
- [x] Renderer legacy e primo draft 1080×1920 da 60 secondi conservati
- [x] Paper edit approvato e QA dei 15 style frame v0.5
- [x] Renderer adattato al template ultra-discorsivo v0.5
- [x] Secondo draft esportato come master muto da 97 secondi
- [x] Sistema di sottotitoli animati verificato su motion test
- [x] Draft 03 esportato con testo animato, conservando il draft 02 statico
- [x] Scene 11–13 riscritte e riallineate per il draft 04
- [x] Timeline compressa e ripetizione eliminata per il draft 05
- [x] Ritmo calibrato sulla slide 10 a 3,5 secondi per il draft 06
- [ ] Copertina e versione finale dopo la revisione del draft 06

## Direzione visiva

Si usa il sistema del brand v2: nero inchiostro, bianco osso e un solo accento
acido per frame. Screenshot, key art, footage e GIF restano in finestre 16:9
incorniciate; il testo principale vive nella zona sicura `x 70–910` e usa un
massimo di tre righe. `sogno-mika.jpg` torna soltanto nel passaggio emotivo
finale, mentre il hook usa Mika esausta sul divano.

## Cartelle

- `content/` — recensione, narrazione continua, template, storyboard e SRT.
- `content/archive/draft-01/` — traccia v0.4 usata dal renderer legacy.
- `assets/screenshots/` — undici immagini di gioco già disponibili.
- `assets/raw/press-kit/` — da riempire localmente con il press kit.
- `assets/raw/footage/` — footage video ufficiale, ignorato da Git.
- `assets/raw/memes/` — due GIF selezionate e rinominate, ignorate da Git.
- `assets/SOURCES.md` — registro di fonti, crediti e licenze.
- `render.py` — renderer legacy del draft 01 da 60 secondi.
- `render_v05.py` — renderer corrente del paper edit da 52 secondi.

## Stato dei draft

Il primo master di lavoro è `dist/extra-coin-draft-01.mp4`: 1080×1920,
30 fps, 60 secondi, H.264 e nessuna traccia audio. È il test v0.4, viene
conservato come confronto e non deve essere sovrascritto. `dist/` è ignorata
da Git.

Il secondo master di lavoro è `dist/extra-coin-draft-02.mp4`: 1080×1920,
30 fps, 97 secondi, H.264 progressivo e nessuna traccia audio. È stato generato
il 1 settembre 2026 dopo il controllo dei 15 style frame; resta un draft da
rivedere, non il file finale per la pubblicazione.

Il terzo master di lavoro è `dist/extra-coin-draft-03.mp4`: conserva testo,
timing e immagini del draft 02, ma anima soltanto i layer testuali. Le righe
entrano dal basso con un breve stagger, la keyword passa al colore d'accento e
l'uscita avviene negli ultimi sette frame. Glitch, media e microheader non
trascinano più il testo.

Il quarto master di lavoro è `dist/extra-coin-draft-04.mp4`: conserva durata,
immagini e animazioni del draft 03, aggiornando le scene 11–13 con il passaggio
sui personaggi, sulle scelte morali e sulla scoperta che anche i genitori
possono sbagliare e arrendersi. Il draft 03 resta disponibile per confronto.

Il quinto master di lavoro è `dist/extra-coin-draft-05.mp4`: riduce la durata
da 97 a 83 secondi senza cambiare i 15 passaggi narrativi. Tutte le cue restano
entro 2,4 parole al secondo; la scena 10 termina con `boss, amicizie e scelte`,
lasciando `scelte morali` soltanto alla scena 11. I draft precedenti restano
disponibili per confronto.

Il sesto master di lavoro è `dist/extra-coin-draft-06.mp4`: usa la slide 10,
la più carica fra corpo, paratesto e cambi visuali, come riferimento da 3,5
secondi. Le altre cue vengono scalate fra 2,5 e 4 secondi; la durata complessiva
scende a 52 secondi senza eliminare passaggi narrativi.

Il renderer richiede Python 3.9 o successivo e le dipendenze elencate in
`requirements-render.txt`. Dalla root del repository:

```powershell
python -m pip install -r reels/extra-coin/requirements-render.txt
python reels/extra-coin/render_v05.py --preview
python reels/extra-coin/render_v05.py --motion-test
python reels/extra-coin/render_v05.py --motion
```

Nella copia autonoma `Extra Coin - Reel` sul Desktop, eseguire invece gli
stessi comandi direttamente dalla cartella:

```powershell
python -m pip install -r requirements-render.txt
python render_v05.py --preview
python render_v05.py --motion-test
python render_v05.py --motion
```

`--preview` genera 15 fotogrammi di controllo e un contact sheet nella cache
senza codificare l'intero video. Le scene 07 e 09 vengono campionate mentre le
GIF sono visibili, così si controllano insieme meme e testo. Se FFmpeg non è
nel `PATH`, il renderer usa automaticamente il binario incluso da
`imageio-ffmpeg`.

`--motion-test` genera una prova muta da 17 secondi con le cue 02, 07, 09, 14
e 15. `--motion` esporta il draft 06 completo; senza questa opzione il renderer
genera una variante statica del draft 06.
