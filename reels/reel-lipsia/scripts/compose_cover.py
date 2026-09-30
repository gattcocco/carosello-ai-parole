"""Compone copertine 1080x1920 per la griglia di Instagram.

La copertina non e' un fotogramma del reel: la griglia del profilo ritaglia
il 9:16, e il testo delle didascalie sta in basso, quindi sparirebbe. Qui il
titolo e' centrato verticalmente, cosi' sopravvive a qualunque ritaglio.

Il velo scuro si adatta alla luminosita' misurata dietro il blocco di testo:
su footage gia' buio resta leggero, su un fotogramma chiaro si alza. Serve a
non spegnere immagini che sono gia' scure di loro.

Uso:
    .venv/Scripts/python.exe scripts/compose_cover.py
"""

import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "copertine"
sys.path.insert(0, str(Path(__file__).resolve().parent))

W, H = 1080, 1920
BONE = (242, 239, 233)
ACID = (166, 255, 0)
INK = (11, 11, 13)
FONT_PATH = "C:/Windows/Fonts/BOD_CB.TTF"
SAFE = 900
TARGET_LUMA = 52          # luminosita' voluta dietro il testo

# (nome, sorgente, secondo, righe del titolo, tratto in verde)
COVERS = [
    ("lipsia-montagna", ("clip", "plo_0215", 2.0),
     ["LA DISCARICA", "DEI LIBRI", "DI LIPSIA"], "DI LIPSIA"),
    ("lipsia-massa", ("clip", "P1", 1.0),
     ["LA DISCARICA", "DEI LIBRI", "DI LIPSIA"], "DISCARICA"),
    ("lipsia-soffitta", ("clip", "plo_0245", 2.0),
     ["LA DISCARICA", "DEI LIBRI", "DI LIPSIA"], "DI LIPSIA"),
    ("pastore", ("image", "pastore", 0),
     ["LI HA SALVATI", "UN PRETE", "COL FURGONE"], "UN PRETE"),
]


def frame_from(kind, source, sec):
    if kind == "image":
        from build_fullscreen import IMAGE_SOURCES
        return Image.open(IMAGE_SOURCES[source]).convert("RGB")
    tmp = OUT / f"_{source}.png"
    subprocess.run(
        ["ffmpeg", "-v", "quiet", "-ss", str(sec),
         "-i", str(ROOT / "assets" / "clips" / f"{source}.mp4"),
         "-frames:v", "1", str(tmp), "-y"], check=True)
    img = Image.open(tmp).convert("RGB")
    tmp.unlink(missing_ok=True)
    return img


def cover_crop(img):
    s = max(W / img.width, H / img.height)
    r = img.resize((int(img.width * s) + 1, int(img.height * s) + 1), Image.LANCZOS)
    x, y = (r.width - W) // 2, (r.height - H) // 2
    return r.crop((x, y, x + W, y + H))


def fit_font(righe):
    size = 150
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    while size > 70:
        f = ImageFont.truetype(FONT_PATH, size)
        if max(d.textlength(r, font=f) for r in righe) <= SAFE:
            return f, size
        size -= 6
    return ImageFont.truetype(FONT_PATH, 70), 70


def veil_alpha(base, top, bottom):
    """Quanto velo serve per portare la fascia del testo a TARGET_LUMA."""
    band = np.asarray(base.convert("RGB"))[max(0, top):min(H, bottom)]
    luma = float((0.299 * band[:, :, 0] + 0.587 * band[:, :, 1] + 0.114 * band[:, :, 2]).mean())
    if luma <= TARGET_LUMA:
        return 60                      # gia' scuro: solo un tocco per staccare il testo
    a = 255 * (1 - TARGET_LUMA / luma)
    return int(max(60, min(205, a)))


def draw_line(d, testo, verde, font, y):
    """Disegna una riga colorando in verde il tratto evidenziato, se c'e'."""
    i = testo.find(verde) if verde else -1
    if i == -1:
        pezzi = [(testo, BONE)]
    else:
        pezzi = [(testo[:i], BONE), (verde, ACID), (testo[i + len(verde):], BONE)]
    larghezza = sum(d.textlength(t, font=font) for t, _ in pezzi)
    x = (W - larghezza) / 2
    for t, colore in pezzi:
        if not t:
            continue
        d.text((x, y), t, font=font, fill=(*colore, 255))
        x += d.textlength(t, font=font)


def make(name, src, righe, verde, kicker=None):
    """kicker: riga piccola sopra il titolo, es. "PARTE 2". Serve a far
    leggere due copertine come una serie nella griglia del profilo."""
    base = cover_crop(frame_from(*src))
    font, size = fit_font(righe)
    lh = int(size * 1.02)

    k_font = ImageFont.truetype(FONT_PATH, 52) if kicker else None
    k_gap = 46 if kicker else 0
    k_h = 52 if kicker else 0

    blocco = lh * len(righe) + k_h + k_gap
    top = (H - blocco) // 2            # centrato: sopravvive al ritaglio della griglia

    alpha = veil_alpha(base, top - 40, top + blocco + 40)
    card = Image.alpha_composite(base.convert("RGBA"),
                                 Image.new("RGBA", (W, H), (*INK, alpha)))
    d = ImageDraw.Draw(card)

    y = top
    if kicker:
        # spaziato, in verde: si legge come un'etichetta, non come titolo
        tracking = 14
        larghezza = sum(d.textlength(c, font=k_font) + tracking for c in kicker) - tracking
        x = (W - larghezza) / 2
        for c in kicker:
            d.text((x, y), c, font=k_font, fill=(*ACID, 255))
            x += d.textlength(c, font=k_font) + tracking
        y += k_h + k_gap

    for r in righe:
        draw_line(d, r, verde, font, y)
        y += lh

    out = OUT / f"cover-{name}.png"
    card.convert("RGB").save(out)
    return out, size, alpha


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, src, righe, verde in COVERS:
        p, size, alpha = make(name, src, righe, verde)
        print(f"{p.name:26} corpo {size}px   velo {alpha}/255")


if __name__ == "__main__":
    main()
