#!/usr/bin/env python3
# Style-frame v2 — direzione "Evangelion senza cosplay"
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
INK = (11, 11, 13)
BONE = (242, 239, 233)
ACID = (166, 255, 0)
EVA = (91, 62, 150)
NERV = (255, 77, 0)
ASH = (74, 74, 80)

FB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FMB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def F(p, s): return ImageFont.truetype(p, s)

def mono_spaced(d, xy, text, f, fill, tracking=6):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tracking

# ---------- FRAME 1: title card ----------
img = Image.new("RGB", (W, H), INK)
d = ImageDraw.Draw(img)

# microtesto log in alto
mono_spaced(d, (70, 270), "PAROLA 02/09 - LESSICO AI", F(FM, 26), ACID, 4)
d.rectangle([70, 320, 470, 323], fill=ASH)

# titolone che tocca i bordi, allineato a sinistra
t1, t2 = "VIBE", "CODING"
f_big = F(FB, 330)
d.text((55, 470), t1, font=f_big, fill=BONE)
f_big2 = F(FB, 252)
d.text((55, 810), t2, font=f_big2, fill=BONE)
# la parola "esce" dal frame: ripetizione tagliata a destra, tono cenere
d.text((W - 180, 470), t1, font=f_big, fill=(30, 30, 34))

# sottolineatura NERV
d.rectangle([70, 1130, 640, 1146], fill=NERV)

# definizione
fd = F(FB, 52)
d.text((70, 1230), "Programmare dicendo all'AI", font=fd, fill=BONE)
d.text((70, 1300), "cosa vuoi. Del codice,", font=fd, fill=BONE)
d.text((70, 1370), "chi se ne importa.", font=fd, fill=BONE)

# tag mono in basso
mono_spaced(d, (70, 1490), "WOTY COLLINS 2025 / KARPATHY", F(FM, 24), ASH, 3)

# barra diagonale rossa angolo alto-destro
for i in range(4):
    d.polygon([(W - 260 + i * 60, 0), (W - 200 + i * 60, 0),
               (W - 320 + i * 60, 190), (W - 380 + i * 60, 190)],
              fill=NERV if i % 2 == 0 else INK)

# contatore
mono_spaced(d, (W - 190, 1800), "02 / 09", F(FMB, 30), ASH, 3)

img.save("/sessions/sharp-quirky-bohr/mnt/outputs/styleframe1-titlecard.png")

# ---------- FRAME 2: definition card su viola ----------
img = Image.new("RGB", (W, H), EVA)
d = ImageDraw.Draw(img)

# blocco nero superiore con parola piccola mono
d.rectangle([0, 0, W, 430], fill=INK)
mono_spaced(d, (70, 280), "DEF. READING DEBT", F(FMB, 34), ACID, 5)
d.rectangle([70, 350, 240, 353], fill=ACID)

# definizione gigante su viola
fd = F(FB, 96)
lines = ["Più testo", "di quanto", "ne leggerai", "mai."]
y = 560
for ln in lines:
    d.text((70, y), ln, font=fd, fill=BONE)
    y += 125

# firma
mono_spaced(d, (70, 1180), "- L'HO INVENTATA IO", F(FM, 28), (200, 190, 225), 4)

# fascia nera inferiore con CTA
d.rectangle([0, 1580, W, H], fill=INK)
fc = F(FB, 54)
d.text((70, 1660), "Scrivila nei commenti", font=fc, fill=BONE)
d.rectangle([70, 1740, 480, 1752], fill=NERV)

# tacche laterali stile UI
for yy in range(470, 1540, 90):
    d.rectangle([W - 24, yy, W - 12, yy + 36], fill=(120, 95, 180))

img.save("/sessions/sharp-quirky-bohr/mnt/outputs/styleframe2-defcard.png")
print("ok")
