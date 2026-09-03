# Storyboard — BUCO NERO

**Formato:** Instagram Reel 1080×1920, 30 fps  
**Durata target:** 53–55 secondi
**Audio:** musica minimale/tensione crescente + pochi effetti sonori; nessun voice-over  
**Visual principale:** `ghostty-blackhole.mp4` (conversione della demo ufficiale)  
**Fonte:** https://github.com/s0xDk/ghostty-blackhole

## Nota di fact-check

Nel draft originale «dopo mezz’ora cresce» e «dopo quasi un’ora diventa
gigantesca» sembrano due soglie precise. Nel progetto, invece, la modalità
Pomodoro fa crescere progressivamente il buco nero durante 55 minuti di lavoro,
lo fa collassare nell’ultimo minuto e lo mantiene piccolo durante 5 minuti di
pausa. Se l’utente smette di digitare, il buco nero comincia a sparire dopo 90
secondi. Esiste anche una modalità che lega la crescita al riempimento della
context window di Claude Code.

La frase «un developer si dimenticava sempre di fare pausa» funziona come hook,
ma non è presentata come storia personale dell’autore nel README ufficiale.

## Discorso continuo

Questo è il testo sorgente del reel. Nel montaggio viene diviso nelle schermate
della timeline, ma deve funzionare anche letto di seguito senza immagini.

```text
Un developer dimenticava sempre di fare pausa.
La soluzione? Un buco nero nel terminale.

No, sul serio.
Ghostty Blackhole è uno shader ray-traced per Ghostty.

In modalità Pomodoro parte da una piccola singolarità.
Poi cresce per 55 minuti e deforma davvero il testo.

Il terminale ti sta dicendo: «Fratello, alzati.»

Se smetti di digitare, il buco nero si rimpicciolisce.
Se continui a lavorare, resta lì. A fissarti.

Può anche crescere insieme alla context window di Claude Code.
È open source. Si chiama Ghostty Blackhole.

Perché usare un timer, quando puoi piegare lo spazio-tempo?
```

Totale: circa 94 parole in 48 secondi, media 1,96 parole al secondo.

## Timeline, testo a schermo e GIF

| # | Timecode | Testo a schermo | Visual | GIF |
|---:|:---|:---|:---|:---|
| 01 | 00:00–00:03.5 | `UN DEVELOPER DIMENTICAVA / SEMPRE DI FARE PAUSA.` | Terminale quasi nero; cursore che lampeggia. Testo osso, grande ma non da title card. | Nessuna. L’apertura deve creare attesa. |
| 02 | 00:03.5–00:07.0 | `LA SOLUZIONE? / UN BUCO NERO NEL TERMINALE.` | Title card con entrata a scatto. `BUCO NERO` è l’unica riga in verde terminale. | Nessuna. |
| 03 | 00:07.0–00:09.0 | `NO, SUL SERIO.` | Mezzo secondo quasi nero, poi appare la piccola singolarità. | **GIF 01 — demo ufficiale**, già presente come `ghostty-blackhole.gif`; usare la versione MP4. Il testo resta sopra la GIF fino al taglio. |
| 04 | 00:09.0–00:13.0 | `Ghostty Blackhole è uno shader ray-traced / per Ghostty.` | Demo ufficiale dentro una finestra 4:3, con crop sul terminale e sul buco nero. Etichetta: `FOOTAGE UFFICIALE · GHOSTTY BLACKHOLE`. | **GIF 01**, tratto in cui il buco nero è ancora piccolo. Avviare la GIF dopo 0,5 s di testo fermo. |
| 05 | 00:13.0–00:17.5 | `In modalità Pomodoro parte / da una piccola singolarità.` | Punch-in sull’angolo in cui compare il buco nero. Microtesto: `MODE_POMODORO`. | Continua **GIF 01**, senza stacco comico. |
| 06 | 00:17.5–00:22.0 | `Poi cresce per 55 minuti / e deforma davvero il testo.` | Progressione piccolo → medio → grande; chiudere sul momento più leggibile della lente gravitazionale. Contatore mono `00 → 30 → 55 MIN`. | **GIF 01**, tre estratti ordinati per dimensione. Il testo resta in un’area non deformata. |
| 07 | 00:22.0–00:26.0 | `IL TERMINALE TI STA DICENDO: / «FRATELLO, ALZATI.»` | Testo completo su nero; `ALZATI` passa al rosso-arancio dopo 1,5 s. La reaction entra soltanto alla fine. | **GIF 02 selezionata — uomo immerso nelle sabbie mobili**: `Sinking Days Of Our Lives GIF by Global Entertainment.gif`. Inserire da 00:24.8 a 00:26.0, dentro una finestra orizzontale. Crop stretto su testa, mano e spruzzo a sinistra; evitare di ingrandirla oltre il necessario perché la sorgente ha una texture VHS evidente. |
| 08 | 00:26.0–00:31.0 | `Se smetti di digitare, / il buco nero si rimpicciolisce.` | Demo che torna piccola o scompare; cursore fermo. Microtesto `IDLE → FADE`. | **GIF 01**, segmento di shrink/fade. Il testo appare entro 00:26.3 e resta fermo. |
| 09 | 00:31.0–00:35.5 | `Se continui a lavorare, resta lì. / A fissarti.` | Torna il buco nero, fermo in alto. Negli ultimi 1,1 s compare il controcampo. | **GIF 03 selezionata — primo piano verticale del gatto nero**: `Suspicious Black Cat GIF.gif`. Inserire da 00:34.4 a 00:35.5; crop centrale sugli occhi, senza caption. Può occupare una finestra più alta della GIF 02, ma non deve coprire `A fissarti.` |
| 10 | 00:35.5–00:40.0 | `Può anche crescere insieme / alla context window di Claude Code.` | Barra `CONTEXT 12% → 100%`; il buco nero aumenta in sincrono. | **GIF 01**, tratto che mostra la modalità token. Nessun meme: è informazione nuova. |
| 11 | 00:40.0–00:43.5 | `È OPEN SOURCE. / SI CHIAMA GHOSTTY BLACKHOLE.` | Scheda repo: `s0xDk / ghostty-blackhole` + icona GitHub. | Nessuna GIF. Usare screenshot pulito del repository oppure title card tipografica. |
| 12 | 00:43.5–00:48.0 | `PERCHÉ USARE UN TIMER, / QUANDO PUOI PIEGARE / LO SPAZIO-TEMPO?` | Title card finale; `SPAZIO-TEMPO` in verde terminale. Microtesto: `LINK IN CAPTION`. | **GIF 04 opzionale — macchina di Rube Goldberg** da 00:46.9 a 00:48.0. Usarla solo se non ostacola la lettura; la scelta consigliata è tipografia pura. |
| 13 | 00:48.0–00:55.0 | `Giornalismo e codice: / full-stack writer. / Curo la newsletter Critical Inventory, / per chi scrive e sviluppa. / Iscriviti al link in bio` | Schermata personale con ritratto line art, logo Critical Inventory e glitch RGB contenuto. | Nessuna GIF. |

## Lista asset GIF

### Già disponibile

- `ghostty-blackhole.gif` — demo ufficiale, 520×391, circa 20,9 secondi.
- `ghostty-blackhole.mp4` — versione consigliata per il montaggio.

La demo ufficiale va riutilizzata in più punti con selezioni diverse: piccolo,
crescita, distorsione, riduzione e modalità context window. Non serve cercare
cinque GIF tecniche diverse.

### Da reperire

1. **GIF 02 — uomo nelle sabbie mobili: selezionata**, scena 07. File locale:
   `Sinking Days Of Our Lives GIF by Global Entertainment.gif`; massimo 1,2
   secondi.
2. **GIF 03 — primo piano del gatto nero: selezionata**, scena 09. File locale:
   `Suspicious Black Cat GIF.gif`; massimo 1,1 secondi.
3. **GIF 04 — Rube Goldberg**: opzionale sulla battuta finale, scena 12,
   massimo 1 secondo.

Per gli innesti comici preferire stock riutilizzabile. Se si usa GIPHY/Tenor,
salvare URL, autore e condizioni d’uso in un file fonti prima del render.

## Indicazioni di montaggio

- Palette: nero inchiostro, bianco osso e verde terminale. Il rosso-arancio può
  comparire solo nella title card `FRATELLO, ALZATI`, senza convivere col verde.
- La demo non va mostrata full-screen per tutto il reel: alternare finestra,
  crop ravvicinato e title card per darle peso.
- Il corpo narrativo entra per riga in 6–10 frame; niente animazione parola per
  parola. Il testo rimane fermo per almeno il 90% della scena.
- Le reaction entrano soltanto dopo che la frase è già leggibile e restano
  sotto 1,2 secondi. Il testo non scompare quando arriva la GIF.
- Corpo narrativo 62–68 px; title card 120–150 px; microtesti monospaziati.
- Safe-zone del testo: y 250–1550, verificata su schermo telefonico.
- Nessuna dissolvenza incrociata; usare tagli netti, flash frame e un solo
  micro-glitch prima della scena 06.
- Conservare un momento quasi vuoto prima di `FRATELLO.`: è il respiro visivo
  del reel.

## Gate prima del render

- [ ] Verificare sulla demo i cinque stati: piccolo, crescita, distorsione,
  shrink/fade e crescita legata alla context window.
- [x] GIF 02 e GIF 03 salvate localmente; GIF 04 resta facoltativa.
- [ ] Registrare fonti e diritti degli innesti esterni.
- [ ] Controllare che nessuna reaction copra il testo o superi 1,2 secondi.
- [ ] Guardare il reel senza audio e verificare che ogni schermata si legga una
  sola volta, senza dover mettere in pausa.
- [ ] Approvare cinque frame: hook, demo piccola, distorsione, reaction e CTA.
