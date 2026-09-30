"""Compone le banconote della DDR in card verticali 1080x1920.

Le scansioni originali sono quasi quadrate (fronte e retro impilati su fondo
bianco): il cover-crop 9:16 del builder ne taglierebbe via meta' larghezza,
perdendo taglio e ritratto. Qui la banconota viene ritagliata dal suo margine
bianco, scalata e appoggiata intera sul fondo del brand, cosi' il builder puo'
trattarla come una normale immagine con zoom 1.0 senza tagliare niente.

La posizione verticale tiene conto della fascia delle didascalie, che occupa
all'incirca da 1400 a 1660: il blocco resta sopra.

Con --16x9 compone invece card 1920x1080 per la pipeline YouTube (v7+):
solo il fronte della banconota, grande, sopra la fascia delle didascalie.
Escono in card16/ e sono registrate come marco16_* in build_fullscreen.py.

Uso:
    .venv/Scripts/python.exe scripts/compose_banknotes.py
    .venv/Scripts/python.exe scripts/compose_banknotes.py --16x9
    .venv/Scripts/python.exe scripts/compose_banknotes.py --16x9 --retro   # retro -> card16-retro/
"""

import sys

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


def trim_flat(img: Image.Image, tol: float = 12.0) -> Image.Image:
    """Toglie bordi uniformi (bianchi o neri) guardando la varianza di righe e colonne."""
    g = np.asarray(img.convert("L"), dtype=float)
    rows = np.where(g.std(axis=1) > tol)[0]
    cols = np.where(g.std(axis=0) > tol)[0]
    if not len(rows) or not len(cols):
        return img
    return img.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))


def front_only(note: Image.Image) -> Image.Image:
    """Separa il fronte dal retro: la riga piu' uniforme nella fascia centrale."""
    g = np.asarray(note.convert("L"), dtype=float)
    std = g.std(axis=1)
    h = len(std)
    mid = np.arange(int(h * 0.35), int(h * 0.65))
    gap = mid[np.argmin(std[mid])]
    return trim_flat(note.crop((0, 0, note.width, gap)))


def back_only(note: Image.Image) -> Image.Image:
    """Il retro (scene di vita, edifici): la meta' sotto la fascia centrale."""
    g = np.asarray(note.convert("L"), dtype=float)
    std = g.std(axis=1)
    h = len(std)
    mid = np.arange(int(h * 0.35), int(h * 0.65))
    gap = mid[np.argmin(std[mid])]
    return trim_flat(note.crop((0, gap, note.width, h)))


W16, H16 = 1920, 1080
NOTE16_WIDTH = 1380     # il fronte occupa buona parte del frame
CENTER16_Y = 430        # sopra la fascia didascalie (in basso, ~760-1020)


def make_card16(src: Path, dest: Path, side=front_only):
    note = side(trim_flat(Image.open(src).convert("RGB")))
    scale = NOTE16_WIDTH / note.width
    note = note.resize((NOTE16_WIDTH, int(note.height * scale)), Image.LANCZOS)
    card = Image.new("RGB", (W16, H16), INK)
    x = (W16 - note.width) // 2
    y = max(50, CENTER16_Y - note.height // 2)
    card.paste(note, (x, y))
    card.save(dest)
    return note.size, (x, y)


def main():
    wide = "--16x9" in sys.argv
    back = "--retro" in sys.argv          # con --16x9: il retro invece del fronte
    out = SRC / ("card16-retro" if back else "card16") if wide else OUT
    if wide:
        make = (lambda s, d: make_card16(s, d, back_only)) if back else make_card16
    else:
        make = make_card
    out.mkdir(parents=True, exist_ok=True)
    for src in sorted(SRC.glob("*.jpg")):
        if src.name.startswith("_"):
            continue
        slug = (src.stem.lower()
                .replace("1971-1989 ddr ", "")
                .replace("1964 ddr ", "1964-")
                .replace(" mark banknotes", "")
                .replace(" marks", "")
                .replace(" ", "-"))
        dest = out / f"marco-{slug}.png"
        size, pos = make(src, dest)
        print(f"{dest.name:28} banconota {size[0]}x{size[1]} a y={pos[1]}")


if __name__ == "__main__":
    main()
