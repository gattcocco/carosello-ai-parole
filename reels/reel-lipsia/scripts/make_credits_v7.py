#!/usr/bin/env python3
# Titoli di coda "da film" per il reel Lipsia — immagine alta 1920px per lo scroll verticale.
from PIL import Image, ImageDraw, ImageFont

W = 1920
BG = (8, 8, 10)
BONE = (242, 239, 233)
ACID = (166, 255, 0)
GREY = (155, 155, 160)
DIM = (120, 120, 126)

FONTS = "C:/Windows/Fonts/"
def f(name, size): return ImageFont.truetype(FONTS + name, size)
# Bodoni MT cuts
BOD_B   = "BOD_B.TTF"     # bold
BOD_CB  = "BOD_CB.TTF"    # condensed bold
BOD_I   = "BOD_I.TTF"     # italic
BOD_CR  = "BOD_CR.TTF"    # condensed regular
# fallback con glifi sicuri (umlaut, guillemet)
LIB_I   = "LiberationSerif-Italic.ttf"
LIB_R   = "LiberationSerif-Regular.ttf"

tmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))

def w_tracked(text, fnt, tr):
    return sum(tmp.textlength(c, font=fnt) + tr for c in text) - tr

# blocchi: (kind, text)
C = [
 ("gap", 40),
 ("title", "LA DISCARICA DEI LIBRI"),
 ("subtitle", "Lipsia, 1991  —  Katlenburg, oggi"),
 ("gap", 46), ("rule", 0), ("gap", 46),

 ("header", "RICERCA · TESTO · MONTAGGIO"),
 ("name", "Critical Inventory"),
 ("gap", 46), ("rule", 0), ("gap", 46),

 ("header", "FILMATI D'ARCHIVIO"),
 ("name", "Library Organization"),
 ("detail", "Coronet Instructional Films, 1951"),
 ("detail", "Internet Archive / Prelinger Archives"),
 ("gap", 30),
 ("name", "Bücherdeponie Plottendorf"),
 ("detail", "KANAL X — Archiv Bürgerbewegung Leipzig e.V."),
 ("detail", "22 luglio 1991"),
 ("gap", 30),
 ("name", "Trabant 601 — Advertising Film"),
 ("detail", "1969 — Internet Archive"),
 ("gap", 46), ("rule", 0), ("gap", 46),

 ("header", "FOTOGRAFIE · KATLENBURG"),
 ("detail", "Kassandro · Migebert · Bernhard Hanakam · Jan Stubenitzky"),
 ("detail", "CC BY-SA 3.0 — via Wikimedia Commons"),
 ("detail", "Veduta del 1654: Matthäus Merian — pubblico dominio"),
 ("gap", 30),
 ("header", "ALTRE IMMAGINI"),
 ("detail", "Banconote DDR — Internet Archive"),
 ("detail", "Ritratto di Martin Weskott · Copertina «Ich fahre einen Trabant»"),
 ("gap", 46), ("rule", 0), ("gap", 46),

 ("header", "FONTI"),
 ("detail", "«Frane nella terra dei lettori» — il manifesto, 30 aprile 1991"),
 ("detail", "«Il pastore del libro» — Süddeutsche Zeitung, 2017"),
 ("detail", "Robert Darnton, «I censori all'opera» — Adelphi, 2017"),
 ("gap", 46), ("rule", 0), ("gap", 46),

 ("header", "MUSICA"),
 ("name", "Colonna sonora originale"),
 ("detail", "New wave sintetizzata — Critical Inventory"),
 ("gap", 60), ("rule", 0), ("gap", 60),

 ("final", "Oggi a Katlenburg vivono circa un milione di libri."),
 ("final", "Ogni domenica se ne possono ancora portare via."),
 ("gap", 70),
 ("brand", "CRITICAL INVENTORY"),
 ("gap", 120),
]

# stili
def style(kind):
    return {
     "title":    (f(BOD_B, 96),  ACID, 0),
     "subtitle": (f(LIB_I, 42),  GREY, 0),
     "header":   (f(BOD_CB, 40), DIM,  8),   # tracked, uppercase
     "name":     (f(BOD_B, 58),  BONE, 0),
     "detail":   (f(LIB_I, 38),  GREY, 0),
     "final":    (f(BOD_B, 50),  BONE, 0),
     "brand":    (f(BOD_CB, 56), ACID, 12),
    }[kind]

# prima passata: altezza
LINE_EXTRA = {"title":18,"subtitle":14,"header":16,"name":14,"detail":12,"final":16,"brand":18}
def line_h(kind, fnt):
    asc, desc = fnt.getmetrics()
    return asc + desc + LINE_EXTRA[kind]

y = 0
for kind, txt in C:
    if kind == "gap": y += txt; continue
    if kind == "rule": y += 40; continue
    fnt, col, tr = style(kind)
    y += line_h(kind, fnt)
Htot = y

img = Image.new("RGB", (W, Htot), BG)
d = ImageDraw.Draw(img)
y = 0
for kind, txt in C:
    if kind == "gap": y += txt; continue
    if kind == "rule":
        cx = W // 2
        d.line([cx - 90, y + 20, cx + 90, y + 20], fill=DIM, width=2)
        y += 40; continue
    fnt, col, tr = style(kind)
    if tr:  # tracked, centrato
        tw = w_tracked(txt, fnt, tr)
        x = (W - tw) / 2
        for ch in txt:
            d.text((x, y), ch, font=fnt, fill=col)
            x += tmp.textlength(ch, font=fnt) + tr
    else:
        tw = d.textlength(txt, font=fnt)
        d.text(((W - tw) / 2, y), txt, font=fnt, fill=col)
    y += line_h(kind, fnt)

img.save("credits_tall.png")
print("credits_tall.png", img.size, "Htot=", Htot)
