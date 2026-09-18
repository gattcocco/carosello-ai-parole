# Reel Lipsia — fiera del libro, 1991

Pipeline separata dagli altri reel (che usano il template Kdenlive): qui
l'audio è generato via Gemini TTS e il video assemblato con moviepy,
interamente da script Python.

## Stato

- Struttura e script pronti e testati (draft di verifica generato con
  asset placeholder e durate di fallback da 3s).
- **Testo reale della narrazione ancora da inserire** in `content/slides.json`
  (ogni voce `"text"` è un TODO). Puoi abbozzarlo prima in `content/narrazione.md`.
- **Asset placeholder**: le gif/immagini in `slides.json` sono prese da
  materiale già nel repo (`Nuove card stile evangelion/GIF`, `reels/buco-nero`,
  `brand/poster`) solo per bloccare il timing. Vanno sostituite con i
  materiali storici veri sulla fiera di Lipsia 1991 quando disponibili.

## Setup

```powershell
# dalla root del pacchetto (Critical Inventory - USB - 2026-09-11)
.venv\Scripts\python.exe -m pip install -r PROGETTO\reels\reel-lipsia\requirements.txt
```

La chiave API è letta da `.env` alla root del pacchetto (`GEMINI_API_KEY`).

## Flusso di lavoro

1. Scrivi/incolla il testo definitivo di ogni slide in `content/slides.json`
   (campo `"text"`), sostituendo i placeholder `TODO: ...`.
2. Genera l'audio, una clip per slide (così la durata visiva combacia
   esattamente con la narrazione):
   ```powershell
   .venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\generate_audio.py
   ```
   Salva in `dist/audio/slide-01.wav`, `slide-02.wav`, ecc. Le slide con
   testo ancora `TODO` vengono saltate.
3. Sostituisci gli asset placeholder in `slides.json` con i materiali veri
   (path relativo a `content/`, `asset_type` = `"image"` o `"gif"`/`"video"`).
4. Genera il draft video (1080×1920, 30fps):
   ```powershell
   .venv\Scripts\python.exe PROGETTO\reels\reel-lipsia\scripts\build_video.py
   ```
   Output: `dist/reel-lipsia-draft.mp4`. Se manca l'audio di una slide,
   usa una durata di fallback di 3s così puoi comunque rivedere il montaggio
   visivo prima che l'audio sia pronto.

## File

| File | Ruolo |
|---|---|
| `content/slides.json` | Fonte unica letta dagli script: testo, voce, asset per slide |
| `content/narrazione.md` | Brutta copia libera del testo, non letta dagli script |
| `scripts/generate_audio.py` | TTS Gemini, una chiamata per slide |
| `scripts/build_video.py` | Assemblaggio moviepy: resize/crop 9:16, loop/trim asset sulla durata audio, concatenazione |
| `dist/audio/` | Clip audio generate (ignorato da Git) |
| `dist/reel-lipsia-draft.mp4` | Draft video (ignorato da Git) |
