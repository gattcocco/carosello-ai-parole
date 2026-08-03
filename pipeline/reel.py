#!/usr/bin/env python3
# Reel "Le parole nuove dell'AI" — 1080x1920, 30fps, testi animati
from PIL import Image, ImageDraw, ImageFont
import os, math

SRC = "/sessions/sharp-quirky-bohr/mnt/Carosello AI Parole"
FRAMES = "/tmp/reel_frames"
os.makedirs(FRAMES, exist_ok=True)

W, H = 1080, 1920
FPS = 30
NAVY = (27, 42, 74)
CREAM = (245, 239, 224)
ORANGE = (232, 99, 44)
POWDER = (143, 184, 216)

FB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FR = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FI = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

def F(path, size): return ImageFont.truetype(path, size)

def ease_out(t):  # cubic
    return 1 - (1 - t) ** 3

def phase(fr, start, dur):
    """0..1 nell'intervallo [start, start+dur] (in frame)"""
    if fr < start: return 0.0
    if fr >= start + dur: return 1.0
    return (fr - start) / dur

# Safe zone IG reels: testo tra y=250 e y=1550 circa
ILL_TOP, ILL_H = 210, 950          # area illustrazione
TITLE_Y = 1250                      # baseline top del titolo
RULE_Y = 1360
DEF_Y = 1415
CRED_Y = 1560

SCENES = [
    dict(file="prima libro aperto.png", dark=False, dur=3.5,
         title=["LE PAROLE NUOVE", "DELL'AI"],
         defs=["7 termini nati con l'intelligenza artificiale", "+ 2 inventati da me"],
         credit=""),
    dict(file="seconda omino seduto in relax.png", dark=False, dur=4.0,
         title=["VIBE CODING"],
         defs=["Programmare dicendo all'AI cosa vuoi,", "dimenticando che il codice esista."],
         credit="Parola dell'anno Collins 2025"),
    dict(file="Pappagallo in collage variopinta.png", dark=False, dur=4.0,
         title=["PAPPAGALLI", "STOCASTICI"],
         defs=["Ricuce frammenti di ciò che ha letto,", "senza sapere cosa significano."],
         credit="Bender & Gebru, 2021"),
    dict(file="Robot pittore e scala impossibile.png", dark=False, dur=4.0,
         title=["ALLUCINAZIONE"],
         defs=["Quando il modello inventa,", "con totale sicurezza."],
         credit="Parola dell'anno Cambridge 2023"),
    dict(file="Ai che esce dalla gabbia.png", dark=False, dur=4.0,
         title=["JAILBREAK"],
         defs=["Convincere l'AI a fare ciò", "che le è stato vietato."],
         credit="Rubata agli iPhone sbloccati"),
    dict(file="Telefono-fonderia di idee straripanti.png", dark=False, dur=4.0,
         title=["SLOP"],
         defs=["La brodaglia che nessuno ha chiesto", "e nessuno leggerà."],
         credit="Parola dell'anno Merriam-Webster 2025"),
    dict(file="Penna arancione sotto la lampada.png", dark=True, dur=4.2,
         title=["AI BLUES"],
         defs=["Generi, ma non stai creando.", "Nostalgia dell'analogico."],
         credit="— l'ho inventata io"),
    dict(file="{_title___Montagna di pratiche sul laptop_}.png", dark=False, dur=4.2,
         title=["READING DEBT"],
         defs=["Più testo di quanto ne leggerai mai."],
         credit="— l'ho inventata io"),
    dict(file="{_title___Nuvola di fumetti colorati_}.png", dark=False, dur=5.0,
         title=["E TU?"],
         defs=["Ne hai inventata una tua?", "Scrivila nei commenti ↓"],
         credit="Salva il reel per la prossima call"),
]

def draw_text_alpha(base, text, f, xy_center_y, fill, alpha, dy=0):
    if alpha <= 0: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, xy_center_y + dy), text, font=f,
           fill=fill + (int(255 * alpha),))
    base.alpha_composite(ov)

import sys
ONLY = int(sys.argv[1]) if len(sys.argv) > 1 else None

frame_idx = 0
for si, sc in enumerate(SCENES):
    nfr_scene = int(sc["dur"] * FPS)
    if ONLY is not None and si != ONLY:
        frame_idx += nfr_scene
        continue
    src = Image.open(os.path.join(SRC, sc["file"])).convert("RGB")
    bg = src.getpixel((15, 15))
    dark = sc["dark"]
    # su scena scura: sfondo navy, testi crema; altrove sfondo crema del file
    canvas_bg = NAVY if dark else bg
    tcol_title = CREAM
    tcol_def = CREAM if dark else NAVY
    tcol_cred = POWDER if dark else ORANGE

    # illustrazione ridimensionata (una volta)
    k = min(900 / src.width, ILL_H / src.height)
    iw, ih = int(src.width * k), int(src.height * k)
    ill = src.resize((iw, ih), Image.LANCZOS)
    ix, iy = (W - iw) // 2, ILL_TOP + (ILL_H - ih) // 2

    # titolo: dimensiona
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    tsz = 96 if len(sc["title"]) == 1 else 84
    tfonts = []
    for line in sc["title"]:
        s = tsz
        f = F(FB, s)
        while tmp.textlength(line, font=f) > 940 and s > 40:
            s -= 4; f = F(FB, s)
        tfonts.append(f)
    fdef = F(FR, 46)
    fcred = F(FI, 36)

    nfr = int(sc["dur"] * FPS)
    for fr in range(nfr):
        img = Image.new("RGBA", (W, H), canvas_bg + (255,))

        # illustrazione: fade + settle (scala 1.04 -> 1.00)
        p_ill = ease_out(phase(fr, 0, 14))
        if p_ill > 0:
            s = 1.04 - 0.04 * p_ill
            if s != 1.0:
                nw2, nh2 = int(iw * s), int(ih * s)
                il2 = ill.resize((nw2, nh2), Image.BILINEAR)
                px, py = (W - nw2) // 2, iy - (nh2 - ih) // 2
            else:
                il2, px, py = ill, ix, iy
            il2a = il2.convert("RGBA")
            il2a.putalpha(int(255 * p_ill))
            img.alpha_composite(il2a, (px, py))

        # titolo: slide-up + fade
        ty = TITLE_Y if len(sc["title"]) == 1 else TITLE_Y - 55
        for li, line in enumerate(sc["title"]):
            p = ease_out(phase(fr, 8 + li * 5, 16))
            col = CREAM if dark else NAVY
            if li == 1: col = ORANGE
            draw_text_alpha(img, line, tfonts[li], ty + li * 105, col, p, dy=int(60 * (1 - p)))

        # riga arancio che cresce
        p_r = ease_out(phase(fr, 20, 12))
        if p_r > 0:
            d = ImageDraw.Draw(img)
            half = int(80 * p_r)
            ry = RULE_Y if len(sc["title"]) == 1 else RULE_Y + 50
            d.rectangle([W // 2 - half, ry, W // 2 + half, ry + 8], fill=ORANGE)

        # definizioni
        dy0 = DEF_Y if len(sc["title"]) == 1 else DEF_Y + 50
        for li, line in enumerate(sc["defs"]):
            p = ease_out(phase(fr, 32 + li * 10, 16))
            draw_text_alpha(img, line, fdef, dy0 + li * 62, tcol_def, p, dy=int(30 * (1 - p)))

        # credit: ancorato SOTTO le definizioni (mai sovrapposto)
        if sc["credit"]:
            p = ease_out(phase(fr, 56, 16))
            cy = dy0 + len(sc["defs"]) * 62 + 46
            draw_text_alpha(img, sc["credit"], fcred, cy, tcol_cred, p)

        # progress dots (9 scene) in alto, dentro safe zone
        d = ImageDraw.Draw(img)
        total = len(SCENES); dot_r = 7; gap = 34
        x0 = W // 2 - (total - 1) * gap // 2
        for j in range(total):
            col = ORANGE if j == si else ((143, 184, 216, 120) if not dark else (245, 239, 224, 90))
            if j == si:
                d.ellipse([x0 + j * gap - dot_r, 150 - dot_r, x0 + j * gap + dot_r, 150 + dot_r], fill=ORANGE)
            else:
                d.ellipse([x0 + j * gap - 4, 150 - 4, x0 + j * gap + 4, 150 + 4], fill=col)

        img.convert("RGB").save(os.path.join(FRAMES, f"f{frame_idx:05d}.jpg"), quality=90)
        frame_idx += 1
    print(f"scena {si+1} ok ({nfr} frame)")

print("TOT frame:", frame_idx)

# ---- PASSATA GLITCH: transizione tra le scene ----
if ONLY is None or ONLY == -1:
    import numpy as np
    rng = np.random.default_rng(42)
    GLITCH_N = 6  # frame di glitch all'inizio di ogni scena (tranne la prima)

    # indici di inizio scena
    starts, acc = [], 0
    for sc in SCENES:
        starts.append(acc)
        acc += int(sc["dur"] * FPS)

    def glitch_mix(cur_p, prev_p, t):
        """t: intensità 1..0"""
        cur = np.array(Image.open(cur_p)).astype(np.uint8)
        prev = np.array(Image.open(prev_p)).astype(np.uint8)
        out = cur.copy()
        h, w, _ = out.shape
        # bande orizzontali: alcune dalla scena precedente, spostate
        for _ in range(int(3 + 12 * t)):
            y0 = int(rng.integers(0, h - 40))
            bh = int(rng.integers(12, 90))
            shift = int(rng.integers(-int(60 + 220 * t), int(60 + 220 * t)))
            src = prev if rng.random() < 0.5 * t + 0.2 else cur
            out[y0:y0 + bh] = np.roll(src[y0:y0 + bh], shift, axis=1)
        # separazione canali RGB
        cs = max(1, int(14 * t))
        out[..., 0] = np.roll(out[..., 0], cs, axis=1)
        out[..., 2] = np.roll(out[..., 2], -max(1, int(9 * t)), axis=1)
        # sottili scanline scure
        for _ in range(int(6 * t)):
            y = int(rng.integers(0, h - 3))
            out[y:y + 2] = (out[y:y + 2] * 0.55).astype(np.uint8)
        return Image.fromarray(out)

    # glitch SOLO in coda alla scena uscente, mescolando con la scena
    # successiva già composta (frame s+70): la nuova scena parte pulita
    for s in starts[1:]:
        nxt_p = os.path.join(FRAMES, f"f{s+70:05d}.jpg")
        for i in range(GLITCH_N, 0, -1):
            t = (GLITCH_N - i + 1) / GLITCH_N  # cresce verso il taglio
            cur_p = os.path.join(FRAMES, f"f{s-i:05d}.jpg")
            glitch_mix(cur_p, nxt_p, t).save(cur_p, quality=90)
    print("glitch ok")
