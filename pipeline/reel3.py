#!/usr/bin/env python3
# Reel "Kokushobi" v2 — divulgativo, con GIF per scena. 1080x1920 @30fps
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import os, sys

BASE = "/sessions/sharp-quirky-bohr/mnt/Carosello AI Parole"
V2 = os.path.join(BASE, "Nuove card stile evangelion")
GIFD = os.path.join(V2, "GIF")
FRAMES = "/tmp/reel3_frames"
os.makedirs(FRAMES, exist_ok=True)

W, H = 1080, 1920
FPS = 30
INK = (11, 11, 13)
BONE = (242, 239, 233)
ACID = (166, 255, 0)
NERV = (255, 77, 0)
ASH = (110, 110, 118)

FB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FMB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FCJK = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

def F(p, s): return ImageFont.truetype(p, s)
def ease_out(t): return 1 - (1 - t) ** 3
def ph(fr, start, dur):
    if fr < start: return 0.0
    if fr >= start + dur: return 1.0
    return (fr - start) / dur

def mono_row(d, xy, text, f, fill, tracking=4, n=None):
    x, y = xy
    shown = text if n is None else text[:n]
    for ch in shown:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tracking

def fit(dr, text, path, size, maxw):
    f = F(path, size)
    while dr.textlength(text, font=f) > maxw and size > 26:
        size -= 4; f = F(path, size)
    return f

def draw_text_alpha(base, text, f, y, fill, alpha, dy=0, x=None):
    if alpha <= 0: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    w = d.textlength(text, font=f)
    xx = (W - w) / 2 if x is None else x
    d.text((xx, y + dy), text, font=f, fill=fill + (int(255 * alpha),))
    base.alpha_composite(ov)

def gif_frames(name, box_w, box_h):
    p = os.path.join(GIFD, name)
    if not os.path.exists(p):
        return None
    im = Image.open(p)
    out = []
    for f in ImageSequence.Iterator(im):
        fr = f.convert("RGB")
        k = min(box_w / fr.width, box_h / fr.height)
        out.append(fr.resize((int(fr.width * k), int(fr.height * k)), Image.NEAREST))
    # scanline pre-applicata
    import numpy as np
    proc = []
    for g in out:
        a = np.array(g).astype(np.float32); a[::3] *= 0.72
        proc.append(Image.fromarray(a.astype('uint8')))
    return proc

def paste_framed(img, d, g, cx, cy_top):
    gx = cx - g.width // 2
    img.paste(g, (gx, cy_top))
    d.rectangle([gx - 4, cy_top - 4, gx + g.width + 4, cy_top + g.height + 4],
                outline=BONE, width=4)
    L = 36
    for px, py, dx, dy in [(gx-4, cy_top-4, 1, 1), (gx+g.width+4, cy_top-4, -1, 1),
                           (gx-4, cy_top+g.height+4, 1, -1), (gx+g.width+4, cy_top+g.height+4, -1, -1)]:
        d.line([px, py, px + L * dx, py], fill=ACID, width=6)
        d.line([px, py, px, py + L * dy], fill=ACID, width=6)

def draw_insert_frame(g, caption):
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    paste_framed(img, d, g, W // 2, (H - g.height) // 2 - 60)
    fm = F(FM, 30)
    tw = sum(d.textlength(c, font=fm) + 4 for c in caption)
    mono_row(d, ((W - tw) / 2, (H + g.height) // 2 + 20), caption, fm, BONE, 4)
    return img

S = [
 dict(id="hook", kind="gifcard", gif="kok-hook.gif", num="STORIA VERA — 50 SECONDI",
      big=[("FA COSÌ CALDO IN GIAPPONE", FB), ("CHE SERVE UNA PAROLA NUOVA", FB)],
      defs=[], credit="", dur=4.5),
 dict(id="scala", kind="scala", num="LA SCALA UFFICIALE DEL CALDO", dur=5.5,
      rows=[("夏日", "GIORNO D'ESTATE · PIÙ DI 25°"),
            ("真夏日", "PIENA ESTATE · PIÙ DI 30°"),
            ("猛暑日", "CALDO FEROCE · PIÙ DI 35°")],
      finale="E PER I 40 GRADI? NIENTE.",
      gifafter=("kok-scala.gif", "LA SCALA FINIVA QUI.", 1.5)),
 dict(id="problema", kind="quiet", gif="kok-problema.gif", num="LA SCALA SI FERMAVA A 35",
      lines=["Nel 2025 trenta città hanno superato i 40 gradi.", "Il record: quasi 42, a Isesaki."],
      dur=5.0),
 dict(id="decisione", kind="gifcard", gif="kok-decisione.gif", num="COME SI SCEGLIE UNA PAROLA?",
      big=[("HANNO CHIESTO", FB), ("A TUTTI", FB)],
      defs=["Un sondaggio nazionale, come un'elezione:", "tredici parole candidate, una sola vincitrice."],
      credit="PRIMAVERA 2026", dur=5.0),
 dict(id="reveal", kind="type", num="LA VINCITRICE",
      big=[("酷暑日", FCJK)], roman="SI LEGGE: KOKUSHOBI",
      defs=["Vuol dire \"giorno di caldo atroce\".", "È la parola ufficiale per i giorni oltre i 40°."],
      credit="UFFICIALE DAL 17 APRILE 2026", dur=5.5,
      gifafter=("kok-reveal.gif", "DA OGGI SI DICE COSÌ.", 1.5)),
 dict(id="secondo", kind="type", num="SECONDA CLASSIFICATA",
      big=[("超猛暑日", FCJK)], roman="SI LEGGE: CHŌ-MŌSHOBI",
      defs=["Voleva dire solo \"super caldo feroce\":", "la parola vecchia con un \"super\" davanti."],
      credit="~65.000 VOTI, NON SONO BASTATI", dur=5.0,
      gifafter=("kok-secondo.gif", "LA SCORCIATOIA NON HA VINTO.", 1.5)),
 dict(id="libere", kind="type", num="LE PROPOSTE LIBERE",
      big=[("サウナ日", FCJK)], roman="SI LEGGE: SAUNA-BI",
      defs=["Qualcuno ha proposto \"giorno-sauna\",", "qualcun altro \"giorno di stare a casa\"."],
      credit="LE PAROLE NASCONO COSÌ", dur=5.0,
      gifafter=("kok-libere.gif", "LA FANTASIA DELLA GENTE.", 1.5)),
 dict(id="precedente", kind="gifcard", gif="kok-precedente.gif", num="NON È LA PRIMA VOLTA",
      big=[("2007", FB)],
      defs=["Anche la parola per i 35 gradi fu inventata:", "insieme a quella per il colpo di calore."],
      credit="IL PERICOLO E IL DANNO, BATTEZZATI INSIEME", dur=5.0),
 dict(id="tesi1", kind="quiet", gif="kok-tesi1.gif", num="LA COSA IMPORTANTE",
      lines=["Il caldo lo sentivano tutti,", "anche senza la parola."], dur=4.5),
 dict(id="tesi2", kind="quiet", gif="kok-tesi2.gif", num="21 LUGLIO 2026 — IL PRIMO KOKUSHOBI VERO",
      lines=["Ma con la parola giusta,", "l'allarme corre più veloce."], dur=5.0),
 dict(id="cta", kind="img", img="v2-bubbles.png", num="TOCCA A TE",
      big=[("E L'ITALIANO?", FB)],
      defs=["Che parola inventeresti", "per il caldo di casa nostra?"],
      credit="SCRIVILA NEI COMMENTI ↓", dur=4.5),
 dict(id="follow", kind="type", num="LA SERIE CONTINUA",
      big=[("SEGUIMI", FB)],
      defs=["Strumenti, pratiche e percorsi alternativi", "per chi scrive e per chi sviluppa."],
      credit="", dur=4.2, inline_gif="seguimi.gif"),
]

def render_scene(si, sc, frame_start):
    tmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    nfr = int(sc["dur"] * FPS)
    fnum = F(FMB, 26)
    counter = f"{si+1:02d} / {len(S):02d}"

    # insert dopo la scena
    after, aft_n = None, 0
    if sc.get("gifafter"):
        gname, caption, gdur = sc["gifafter"]
        gfr = gif_frames(gname, 880, 700)
        if gfr:
            after = (gfr, caption)
            aft_n = int(gdur * FPS)
        else:
            print(f"  ! gif mancante: {gname} — niente insert")

    def save(img, fr):
        img.convert("RGB").save(os.path.join(FRAMES, f"f{frame_start+fr:05d}.jpg"), quality=90)

    total = nfr + aft_n

    # ---------- SCALA ----------
    if sc["kind"] == "scala":
        fk = F(FCJK, 118); fg = F(FM, 27); ff = fit(tmp, sc["finale"], FB, 64, 940)
        for fr in range(total):
            if fr >= nfr:
                gi = (fr - nfr) // 2
                save(Image.fromarray(__import__('numpy').array(
                    draw_insert_frame(after[0][gi % len(after[0])], after[1]))), fr)
                continue
            img = Image.new("RGBA", (W, H), INK + (255,))
            d = ImageDraw.Draw(img)
            n_chars = int(ph(fr, 0, 18) * len(sc["num"]))
            mono_row(d, (70, 268), sc["num"], fnum, ACID, 4, n=n_chars)
            y = 480
            for ri, (kanji, gloss) in enumerate(sc["rows"]):
                p = ease_out(ph(fr, 14 + ri * 22, 12))
                if p > 0:
                    draw_text_alpha(img, kanji, fk, y, BONE, p, dy=int(30 * (1 - p)), x=70)
                    p2 = ph(fr, 22 + ri * 22, 10)
                    if p2 > 0:
                        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                        d2 = ImageDraw.Draw(ov)
                        xg = 70
                        for ch in gloss:
                            d2.text((xg, y + 150), ch, font=fg, fill=ACID + (int(255 * p2),))
                            xg += d2.textlength(ch, font=fg) + 3
                        img.alpha_composite(ov)
                y += 230
            p = ease_out(ph(fr, 94, 10))
            if p > 0:
                if fr == 94:
                    d.rectangle([0, 0, W, H], fill=(255, 255, 255, 255))
                draw_text_alpha(img, sc["finale"], ff, y + 20, NERV, p, dy=int(40 * (1 - p)), x=70)
            mono_row(d, (W - 200, 1800), counter, fnum, ASH, 3)
            save(img, fr)
        return total

    # ---------- QUIET (con gif piccola in alto) ----------
    if sc["kind"] == "quiet":
        gtop = gif_frames(sc["gif"], 620, 440) if sc.get("gif") else None
        for fr in range(nfr):
            img = Image.new("RGBA", (W, H), INK + (255,))
            d = ImageDraw.Draw(img)
            n_chars = int(ph(fr, 8, 26) * len(sc["num"]))
            mono_row(d, (70, 268), sc["num"], F(FMB, 24), ASH, 3, n=n_chars)
            if gtop:
                g = gtop[(fr // 2) % len(gtop)]
                paste_framed(img, d, g, W // 2, 380)
            f1 = fit(tmp, sc["lines"][0], FB, 54, 940)
            f2 = fit(tmp, sc["lines"][1], FB, 54, 940)
            draw_text_alpha(img, sc["lines"][0], f1, 1000, BONE, ph(fr, 15, 30))
            draw_text_alpha(img, sc["lines"][1], f2, 1120, BONE, ph(fr, 60, 30))
            mono_row(d, (W - 200, 1800), counter, fnum, ASH, 3)
            save(img, fr)
        return nfr

    # ---------- GIFCARD / TYPE / IMG ----------
    ill, gslot = None, None
    if sc.get("img"):
        src = Image.open(os.path.join(V2, sc["img"])).convert("RGB")
        k = min(900 / src.width, 850 / src.height)
        ill = src.resize((int(src.width * k), int(src.height * k)), Image.LANCZOS)
    if sc["kind"] == "gifcard" and sc.get("gif"):
        gslot = gif_frames(sc["gif"], 820, 620)
        if not gslot:
            print(f"  ! gif mancante: {sc['gif']} — scena senza finestra")

    inline = None
    if sc.get("inline_gif"):
        inline = gif_frames(sc["inline_gif"], 620, 400)

    is_type = sc["kind"] == "type"
    nb = len(sc["big"])
    bigfonts = []
    for line, fpath in sc["big"]:
        if fpath == FCJK:
            base = 300 if len(line) <= 3 else 230
        else:
            base = (240 if nb == 1 else 130) if is_type else (150 if nb == 1 else 108)
        bigfonts.append(fit(tmp, line, fpath, base, 940))

    tl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dt = ImageDraw.Draw(tl)
    ty = (620 if nb == 1 else 480) if is_type else (1155 if nb == 1 else 1085)
    yy = ty
    for (line, _), f in zip(sc["big"], bigfonts):
        dt.text((70, yy), line, font=f, fill=BONE)
        yy += int(f.size * 1.08)
    title_bottom = yy
    is_cjk = sc["big"][0][1] == FCJK
    roman_gap = 150 if is_cjk else 40
    fdef = F(FB, 50 if is_type else 44)
    fcred = F(FM, 24)

    for fr in range(total):
        if fr >= nfr:
            gi = (fr - nfr) // 2
            save(draw_insert_frame(after[0][gi % len(after[0])], after[1]).convert("RGBA"), fr)
            continue
        img = Image.new("RGBA", (W, H), INK + (255,))
        d = ImageDraw.Draw(img)
        if ill is not None:
            img.paste(ill, ((W - ill.width) // 2, 300 + (850 - ill.height) // 2))
        if gslot:
            g = gslot[(fr // 2) % len(gslot)]
            paste_framed(img, d, g, W // 2, 320 + (620 - g.height) // 2)
        if fr == 4:
            d.rectangle([0, 0, W, H], fill=(255, 255, 255, 255))
        if fr == 5:
            d.rectangle([0, 0, W, H], fill=ACID + (255,))
        p_t = ph(fr, 5, 5)
        if p_t > 0:
            s = 1.3 - 0.3 * ease_out(p_t)
            if s != 1.0:
                lay = tl.resize((int(W * s), int(H * s)), Image.BILINEAR)
                img.alpha_composite(lay, (int(70 - 70 * s), int(ty - ty * s)))
            else:
                img.alpha_composite(tl)
        n_chars = int(ph(fr, 0, 18) * len(sc["num"]))
        mono_row(d, (70, 268), sc["num"], fnum, ACID, 4, n=n_chars)
        if sc.get("roman"):
            p = ph(fr, 14, 8)
            if p > 0:
                fro = F(FM, 28)
                ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                d2 = ImageDraw.Draw(ov)
                xg = 70
                for ch in sc["roman"]:
                    d2.text((xg, title_bottom + roman_gap), ch, font=fro, fill=ACID + (int(255 * p),))
                    xg += d2.textlength(ch, font=fro) + 3
                img.alpha_composite(ov)
        p_r = ease_out(ph(fr, 12, 10))
        ry = (title_bottom + roman_gap + (70 if sc.get("roman") else 0)) if is_type else 1385
        if p_r > 0:
            d.rectangle([70, ry, 70 + int(540 * p_r), ry + 12], fill=NERV)
        base_dy = (ry + 70) if is_type else 1430
        for li, line in enumerate(sc["defs"]):
            if fr >= 20 + li * 7:
                d.text((70, base_dy + li * (66 if is_type else 58)), line, font=fdef, fill=BONE)
        if sc["credit"] and fr >= 38:
            cy = base_dy + len(sc["defs"]) * (66 if is_type else 58) + 40
            mono_row(d, (70, cy), sc["credit"], fcred, ASH, 3)
        if inline and fr >= 30:
            g = inline[((fr - 30) // 2) % len(inline)]
            gy = base_dy + len(sc["defs"]) * 66 + 70
            paste_framed(img, d, g, W // 2, gy)
        mono_row(d, (W - 200, 1800), counter, fnum, ASH, 3)
        save(img, fr)
    return total

lens = []
for sc in S:
    n = int(sc["dur"] * FPS)
    if sc.get("gifafter") and os.path.exists(os.path.join(GIFD, sc["gifafter"][0])):
        n += int(sc["gifafter"][2] * FPS)
    lens.append(n)
starts = [sum(lens[:i]) for i in range(len(S))]

ONLY = int(sys.argv[1]) if len(sys.argv) > 1 else None
if ONLY is not None and ONLY >= 0:
    n = render_scene(ONLY, S[ONLY], starts[ONLY])
    print(f"scena {ONLY} ok, {n} frame")
elif ONLY == -1:
    import numpy as np
    rng = np.random.default_rng(11)
    GL = 6
    def glitch_mix(cur_p, nxt_p, t):
        cur = np.array(Image.open(cur_p)).astype(np.uint8)
        nxt = np.array(Image.open(nxt_p)).astype(np.uint8)
        out = cur.copy(); h, w, _ = out.shape
        for _ in range(int(3 + 12 * t)):
            y0 = int(rng.integers(0, h - 40)); bh = int(rng.integers(12, 90))
            sh = int(rng.integers(-int(60 + 220 * t), int(60 + 220 * t)))
            src = nxt if rng.random() < 0.5 * t + 0.2 else cur
            out[y0:y0 + bh] = np.roll(src[y0:y0 + bh], sh, axis=1)
        out[..., 0] = np.roll(out[..., 0], max(1, int(14 * t)), axis=1)
        out[..., 2] = np.roll(out[..., 2], -max(1, int(9 * t)), axis=1)
        for _ in range(int(6 * t)):
            y = int(rng.integers(0, h - 3))
            out[y:y + 2] = (out[y:y + 2] * 0.55).astype(np.uint8)
        return Image.fromarray(out)
    for s in starts[1:]:
        nxt = os.path.join(FRAMES, f"f{s+60:05d}.jpg")
        for i in range(GL, 0, -1):
            t = (GL - i + 1) / GL
            p = os.path.join(FRAMES, f"f{s-i:05d}.jpg")
            glitch_mix(p, nxt, t).save(p, quality=90)
    print("glitch ok, tot:", sum(lens), "frame =", round(sum(lens) / FPS, 1), "s")
