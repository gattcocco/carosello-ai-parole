#!/usr/bin/env python3
# Montaggio carosello "Le parole nuove dell'AI" — 9 card 1080x1350
from PIL import Image, ImageDraw, ImageFont
import os

SRC = "/sessions/sharp-quirky-bohr/mnt/Carosello AI Parole"
OUT = os.path.join(SRC, "card finali")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1350
BAND_H = 340
BAND_Y = H - BAND_H
NAVY = (27, 42, 74)
CREAM = (245, 239, 224)
ORANGE = (232, 99, 44)
POWDER = (143, 184, 216)

FB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FR = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FI = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def fit_text(draw, text, path, size, max_w):
    f = font(path, size)
    while draw.textlength(text, font=f) > max_w and size > 18:
        size -= 2
        f = font(path, size)
    return f

def center(draw, text, y, f, fill, tracking=0):
    w = draw.textlength(text, font=f)
    draw.text(((W - w) / 2, y), text, font=f, fill=fill)

CARDS = [
    dict(file="prima libro aperto.png", mode="full", num="1/9",
         title=["LE PAROLE NUOVE", "DELL'AI"],
         defs=["7 termini per dire cose che vivevi già", "+ 2 coniati da me"],
         credit="Swipe →"),
    dict(file="seconda omino seduto in relax.png", mode="full", num="2/9",
         title=["VIBE CODING"],
         defs=["Programmare dicendo all'AI cosa vuoi,", "dimenticando che il codice esista."],
         credit="Andrej Karpathy, 2025 · Parola dell'anno Collins"),
    dict(file="Pappagallo in collage variopinta.png", mode="fit", num="3/9",
         title=["PAPPAGALLI STOCASTICI"],
         defs=["Un modello ricuce frammenti di ciò che ha letto,", "senza sapere cosa significano."],
         credit="Dal paper di Bender, Gebru e colleghe (2021)"),
    dict(file="Robot pittore e scala impossibile.png", mode="full", num="4/9",
         title=["ALLUCINAZIONE"],
         defs=["Quando il modello inventa,", "con totale sicurezza."],
         credit="Parola dell'anno Cambridge 2023"),
    dict(file="Ai che esce dalla gabbia.png", mode="full", num="5/9",
         title=["JAILBREAK"],
         defs=["Convincere l'AI a fare ciò", "che le è stato vietato."],
         credit="Termine rubato agli iPhone sbloccati"),
    dict(file="Telefono-fonderia di idee straripanti.png", mode="fit", num="6/9",
         title=["SLOP"],
         defs=["La brodaglia generata che nessuno ha chiesto", "e nessuno leggerà."],
         credit="Parola dell'anno Merriam-Webster 2025"),
    dict(file="Penna arancione sotto la lampada.png", mode="full", num="7/9",
         title=["AI BLUES"],
         defs=["Quando generi ma non hai la sensazione di creare.", "Nostalgia di qualcosa che la comodità ti ha tolto."],
         credit="— coniata da me"),
    dict(file="{_title___Montagna di pratiche sul laptop_}.png", mode="fit", num="8/9",
         title=["READING DEBT"],
         defs=["L'AI produce più testo di quanto ne leggerai mai:", "il non-letto si accumula e matura interessi."],
         credit="— coniata da me"),
    dict(file="{_title___Nuvola di fumetti colorati_}.png", mode="full", num="9/9",
         title=["E TU?"],
         defs=["Ne conosci altre, o ne hai coniate di tue?", "Le migliori finiscono nel pezzo di settembre."],
         credit="Commenta ↓ · Post completo su Substack, link in bio"),
]

for i, c in enumerate(CARDS, 1):
    src = Image.open(os.path.join(SRC, c["file"])).convert("RGB")
    bg = src.getpixel((15, 15))  # colore di fondo campionato nell'angolo
    canvas = Image.new("RGB", (W, H), bg)

    if c["mode"] == "full":
        canvas.paste(src.resize((W, H), Image.LANCZOS), (0, 0))
    else:  # fit: illustrazione intera sopra la fascia
        avail_h = BAND_Y - 30
        k = min(W / src.width, avail_h / src.height)
        nw, nh = int(src.width * k), int(src.height * k)
        img = src.resize((nw, nh), Image.LANCZOS)
        canvas.paste(img, ((W - nw) // 2, (avail_h - nh) // 2 + 15))

    d = ImageDraw.Draw(canvas)
    # fascia blu notte + filo arancio
    d.rectangle([0, BAND_Y, W, H], fill=NAVY)
    d.rectangle([0, BAND_Y, W, BAND_Y + 5], fill=ORANGE)

    two_lines = len(c["title"]) == 2
    if two_lines:
        f1 = fit_text(d, c["title"][0], FB, 58, 960)
        f2 = fit_text(d, c["title"][1], FB, 58, 960)
        center(d, c["title"][0], BAND_Y + 34, f1, CREAM)
        center(d, c["title"][1], BAND_Y + 100, f2, ORANGE)
        dy = 178
    else:
        ft = fit_text(d, c["title"][0], FB, 64, 960)
        center(d, c["title"][0], BAND_Y + 52, ft, CREAM)
        # trattino arancio sotto il titolo
        d.rectangle([W/2 - 35, BAND_Y + 140, W/2 + 35, BAND_Y + 146], fill=ORANGE)
        dy = 168

    fd = font(FR, 31)
    for j, line in enumerate(c["defs"]):
        fdj = fit_text(d, line, FR, 31, 940)
        center(d, line, BAND_Y + dy + j * 44, fdj, CREAM)

    fc = fit_text(d, c["credit"], FI, 24, 900)
    center(d, c["credit"], BAND_Y + 282, fc, POWDER)

    fn = font(FR, 22)
    nw_ = d.textlength(c["num"], font=fn)
    d.text((W - 48 - nw_, H - 42), c["num"], font=fn, fill=POWDER)

    out = os.path.join(OUT, f"0{i}-{c['title'][0].lower().replace(' ', '-').replace('?', '')}.png")
    canvas.save(out, "PNG")
    print("ok", out)
