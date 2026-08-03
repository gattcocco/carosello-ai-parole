# Ripresa lavori — reel kokushobi

Punto della situazione al 3 agosto 2026, branch `reel/kokushobi`. Serve a ripartire senza rileggersi tutto: cosa c'è, cosa manca, cosa si rompe se lanci il render adesso.

---

## Dove siamo

Il reel «In Giappone fa così caldo che serve una parola nuova» è **completo sulla carta e completo di asset**. Non è mai stato renderizzato.

- Storyboard: [storyboard-reel-kokushobi.md](storyboard-reel-kokushobi.md) — 12 scene, 4 insert GIF, **64,7s** totali (target era ~65s, ci siamo).
- Script di montaggio: `pipeline/reel3.py` — 1080×1920 @30fps, stessa struttura di `reel2.py`.
- GIF: tutte e 10 in `Nuove card stile evangelion/GIF/`, con i nomi `kok-*.gif` che lo script si aspetta. Verificate: GIF89a valide, tutte animate.
- Altri asset: `v2-bubbles.png` (scena 11 CTA) e `seguimi.gif` (scena 12 endcard) sono già in cartella.

Non manca nessun file. Quello che manca è il primo render.

---

## Prima cosa da fare: sbloccare il render

`reel3.py` è stato scritto in una sessione remota e i path sono rimasti quelli. **Così com'è non parte in locale.** Tre righe da sistemare:

| Riga | Valore attuale | Problema |
|---|---|---|
| [reel3.py:6](../pipeline/reel3.py#L6) | `BASE = "/sessions/sharp-quirky-bohr/mnt/Carosello AI Parole"` | path di sandbox, non esiste sulla macchina |
| [reel3.py:20-23](../pipeline/reel3.py#L20-L23) | `/usr/share/fonts/truetype/...` | font Linux: servono i path di Liberation Serif Bold, DejaVu Sans Mono (+ Bold) e Noto Serif CJK Bold |
| [reel3.py:9](../pipeline/reel3.py#L9) | `FRAMES = "/tmp/reel3_frames"` | ok da Git Bash, da rivedere se lanci da PowerShell |

Il font CJK non è opzionale: le scene 05, 06 e 07 sono kanji card (酷暑日, 超猛暑日, サウナ日). Senza Noto Serif CJK i glifi escono vuoti.

Poi si monta come il v2:

```bash
# 1. rendering scene (0..11)
for i in 0 1 2 3 4 5 6 7 8 9 10 11; do python3 pipeline/reel3.py $i; done
# 2. passata glitch sulle transizioni
python3 pipeline/reel3.py -1
# 3. encoding
ffmpeg -framerate 30 -i /tmp/reel3_frames/f%05d.jpg -c:v libx264 -pix_fmt yuv420p \
  -crf 20 -movflags +faststart reel-kokushobi.mp4
```

L'mp4 non si versiona (regola `.gitignore`).

---

## Cosa guardare al primo render

Tre cose emerse controllando le GIF. Nessuna è un errore: sono scelte da confermare guardando i frame.

1. **`kok-decisione.gif` e `kok-scala.gif` non si vedranno per intero.** Lo script avanza un frame GIF ogni due frame video ([reel3.py:210](../pipeline/reel3.py#L210), [reel3.py:268](../pipeline/reel3.py#L268)), cioè ~15fps effettivi. Un giro completo richiederebbe 18,5s e 9,9s, ma le scene durano 5,0s e 1,5s: si vedrà circa il 27% e il 15% iniziale. Se il momento buono dell'animazione è a metà, non ci arriva — va tagliata la GIF o allungata la scena.
2. **`kok-tesi1.gif` è un loop da 6 frame** (0,4s a 15fps): nella scena 09 da 4,5s si ripete ~11 volte. Rischia lo sfarfallio.
3. **RAM:** `gif_frames()` ([reel3.py:54](../pipeline/reel3.py#L54)) tiene in memoria tutti i frame ridimensionati più una copia numpy. Su `kok-decisione` (277 frame) sono ~800MB di picco per quella scena sola. Se il render si pianta, l'indiziato è quello.

Inoltre le **didascalie dei 4 insert sono provvisorie**: scritte senza aver visto le GIF, vanno riviste guardando il render (lo dice anche lo storyboard in fondo).

---

## Verifiche aperte sul contenuto

- Lettura di 超猛暑日 (`CHŌ-MŌSHOBI` nella scena 06) — da confermare.
- Registro 酷暑 vs 猛暑: la differenza va spiegata bene o la scena 06 non si capisce.
- Il dato dei 470k voti resta **fuori** dal reel: non confermato. I ~65.000 voti della seconda classificata invece ci sono (scena 06).
- Fonte primaria: [comunicato JMA](https://www.jma.go.jp/jma/press/2602/27a/20260227_40degree.html).

---

## Piccolo debito

Il [README](../README.md) descrive `reel2.py` come lo script "attuale" e non cita né `reel3.py` né i file kokushobi. Da aggiornare quando il reel è chiuso.

---

## Stato git

Branch `reel/kokushobi`, due commit sopra `main`, allineato con origin:

- `6ccae9f` — storyboard, `reel3.py`, riepilogo sessione
- `1074978` — le 10 GIF di scena

PR non ancora aperta: https://github.com/gattcocco/carosello-ai-parole/pull/new/reel/kokushobi
