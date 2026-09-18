"""Compone le banconote della DDR in card verticali 1080x1920.

Le scansioni originali sono quasi quadrate (fronte e retro impilati su fondo
bianco): il cover-crop 9:16 del builder ne taglierebbe via meta' larghezza,
perdendo taglio e ritratto. Qui la banconota viene ritagliata dal suo margine
bianco, scalata e appoggiata intera sul fondo del brand, cosi' il builder puo'
trattarla come una normale immagine con zoom 1.0 senza tagliare niente.

La posizione verticale tiene conto della fascia delle didascalie, che occupa
all'incirca da 1400 a 1660: il blocco resta sopra.

Uso:
    .venv/Scripts/python.exe scripts/compose_banknotes.py
"""

from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "images" / "ddr-marchi"
OUT = SRC / "card"

W, H = 1080, 1920
INK = (11, 11, 13)
NOTE_WIDTH = 920        # larghezza del blocco banconota sulla card
CENTER_Y = 820          # centro verticale del blocco, sopra la fascia del testo
WHITE_CUT = 233         # sopra questo valore il pixel e' considerato margine


def trim_white(img: Image.Image) -> Image.Image:
    """Toglie il margine bianco attorno alla scansione."""
    a = np.asarray(img.convert("RGB"))
    mask = (a < WHITE_CUT).any(axis=2)
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if not len(rows) or not len(cols):
        return img
    pad = 6
    top, bottom = max(0, rows[0] - pad), min(a.shape[0], rows[-1] + pad)
    left, right = max(0, cols[0] - pad), min(a.shape[1], cols[-1] + pad)
    return img.crop((left, top, right, bottom))


def make_card(src: Path, dest: Path):
    note = trim_white(Image.open(src).convert("RGB"))
    scale = NOTE_WIDTH / note.width
    note = note.resize((NOTE_WIDTH, int(note.height * scale)), Image.LANCZOS)

    card = Image.new("RGB", (W, H), INK)
    x = (W - note.width) // 2
    y = CENTER_Y - note.height // 2
    # se la scansione e' molto alta, la si alza per non entrare nella fascia
    y = max(60, min(y, 1380 - note.height))
    card.paste(note, (x, y))
    card.save(dest)
    return note.size, (x, y)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for src in sorted(SRC.glob("*.jpg")):
        if src.name.startswith("_"):
            continue
        slug = (src.stem.lower()
                .replace("1971-1989 ddr ", "")
                .replace("1964 ddr ", "1964-")
                .replace(" mark banknotes", "")
                .replace(" marks", "")
                .replace(" ", "-"))
        dest = OUT / f"marco-{slug}.png"
        size, pos = make_card(src, dest)
        print(f"{dest.name:28} banconota {size[0]}x{size[1]} a y={pos[1]}")


if __name__ == "__main__":
    main()
