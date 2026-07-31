# Carosello AI Parole

Pipeline per contenuti IG della serie «Le parole nuove dell'AI»: carosello, reel v1 (stile risograph crema) e reel v2 (stile Evangelion). Testi, brand manual, prompt di generazione immagini e script di montaggio.

## Struttura

- `pipeline/` — script Python di montaggio
  - `monta_card.py` — carosello 9 card 1080×1350 (brand v1)
  - `reel.py` — reel v1, 9 scene con glitch di transizione
  - `reel2.py` — reel v2 (attuale): scene 9:16 stile Eva, kanji card, insert GIF, endcard SEGUIMI
  - `styleframes.py` — style-frame di validazione del brand v2
- `Nuove card stile evangelion/` — asset generati (PNG soggetti su nero + `GIF/` per gli insert)
- `card finali/` — carosello montato (brand v1)
- `brand-manual-v2.md` — identità visiva corrente (palette, tipografia, montaggio, regole anti-slop)
- `pipeline-immagini-v2.md` — prompt ChatGPT per generare gli asset (style lock + soggetti)
- `reel-parole-ai-v2.mp4` — output corrente (non versionato: si rigenera, vedi sotto)
- `testi/` — testi della serie: bibliografia ragionata, piano di letture per il blog, post Substack, piano del carosello con caption
- `GOATS/` — soggetti del reel v3 (`v3-*.png`) + reference
- `Screenshots/` — screenshot di gioco per le type card del reel v3
- `B-Roll/` — **non versionato**: 9 clip 1920×1080 dal press kit ufficiale di *Titanium Court* (Fellow Traveller). Materiale di terzi, va riscaricato dal press kit dell'editore. Lo storyboard in `testi/storyboard-reel-mountain-goats.md` cita le clip per nome (`Game Intro.mov`, `Dragon Fight.mov`, …): servono con quei nomi esatti dentro `B-Roll/` per montare il reel v3.

## Come si rigenera il reel

Requisiti: Python 3 + Pillow + numpy, ffmpeg, font Liberation Serif e Noto Serif CJK.

```bash
# 1. rendering scene (una alla volta o in loop)
for i in 0 1 2 3 4 5 6 7 8 9 10; do python3 pipeline/reel2.py $i; done
# 2. passata glitch sulle transizioni
python3 pipeline/reel2.py -1
# 3. encoding
ffmpeg -framerate 30 -i /tmp/reel2_frames/f%05d.jpg -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart reel-parole-ai-v2.mp4
```

Gli asset seguono la naming convention di `pipeline-immagini-v2.md` (`v2-<soggetto>.png`, GIF in `Nuove card stile evangelion/GIF/`). Lo script aggancia automaticamente ciò che trova: GIF mancante = scena senza insert; `v2-clanker.png` presente = la scena passa da card tipografica a card immagine.

## Workflow

1. Nuove parole → verifica fonti → testi in `reel2.py` (lista `SCENES`)
2. Immagini → prompt in `pipeline-immagini-v2.md` → ChatGPT → cartella asset
3. GIF insert → GIPHY/Pexels → cartella `GIF/`
4. Render → controllo frame → pubblicazione (audio in tendenza dall'app IG)
