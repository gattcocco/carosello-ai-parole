# Buco Nero

Reel muto su Ghostty Blackhole: **1080×1920, 30 fps, 55 secondi**.
[Storyboard](storyboard.md) · [Prova Kdenlive condivisa](../../templates/reel-v1/README.md).

Dal secondo 48 al 55 la chiusura mostra la [locandina Critical Inventory](../../brand/poster/critical-inventory.png)
intera e ferma, senza ritratto o testo sovrapposto. Questo renderer conserva
la chiusura approvata; quella tipografica del template è un esperimento separato.

## Rigenerare su Windows

Dalla root del repository, con Python 3.10+, i font Windows usati dal renderer
(Bodoni MT Condensed Bold, Segoe UI, Consolas) e FFmpeg disponibile:

```powershell
python -m pip install -r reels/buco-nero/requirements-render.txt
# Solo se ffmpeg non è nel PATH: indica un eseguibile realmente installato.
$env:FFMPEG_BINARY = 'C:\percorso\kdenlive\bin\ffmpeg.exe'
python reels/buco-nero/render.py --preview
python reels/buco-nero/render.py --output dist/buco-nero-draft-03.mp4
```

L'anteprima contiene tutte le 13 scene in `.cache/buco-nero/preview/`.
L'output predefinito senza `--output` è `dist/buco-nero-draft-01.mp4`;
scegli un nome nuovo per conservare un render precedente.

Il renderer usa `ghostty-blackhole.mp4` se presente, altrimenti la GIF sorgente
versionata. [Provenienza e conversione della demo](scarica-ghostty-blackhole-video.md).
Le GIF e le illustrazioni conservano i nomi originali di questa produzione.

Il vecchio render locale `dist/buco-nero-draft-02.mp4` è stato conservato nella
cartella dell'episodio; i video non sono inclusi nel clone GitHub.
