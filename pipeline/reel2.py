#!/usr/bin/env python3
# Reel v2 "Le parole nuove dell'AI" — stile Evangelion, 1080x1920 @30fps
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import os, sys

BASE = "/sessions/sharp-quirky-bohr/mnt/Carosello AI Parole"
V2 = os.path.join(BASE, "Nuove card stile evangelion")
GIFD = os.path.join(V2, "GIF")
FRAMES = "/tmp/reel2_frames"
os.makedirs(FRAMES, exist_ok=True)

W, H = 1080, 1920
FPS = 30
INK = (11, 11, 13)
BONE = (242, 239, 233)
ACID = (166, 255, 0)
EVA = (91, 62, 150)
NERV = (255, 77, 0)
ASH = (110, 110, 118)

FB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FMB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FCJK = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

def F(p, s):
    return ImageFont.truetype(p, s)

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
    while dr.textlength(text, font=f) > maxw and size > 30:
        size -= 6; f = F(path, size)
    return f

S = [
 dict(id="cover", kind="img", img="v2-cover.png", num="LESSICO AI — 8 PAROLE",
      big=[("LE PAROLE", FB), ("NUOVE DELL'AI", FB)], roman=None,
      defs=["8 parole."], credit="EPISODIO 01 — NEOLOGISMI",
      dur=4.4, gif=None),
 dict(id="vibe", kind="img", img="v2-vibe.png", num="PAROLA 01/08",
      big=[("VIBE", FB), ("CODING", FB)], roman=None,
      defs=["Programmare dicendo all'AI cosa vuoi.", "Del codice, chi se ne importa."],
      credit="WOTY COLLINS 2025 / KARPATHY", dur=4.6,
      gif=("vibe coding cat.gif", "IL CODICE SI SCRIVE DA SOLO. CIRCA.", 2.2)),
 dict(id="parrot", kind="img", img="v2-parrot.png", num="PAROLA 02/08",
      big=[("PAPPAGALLI", FB), ("STOCASTICI", FB)], roman=None,
      defs=["Ricuce frammenti di ciò che ha letto,", "senza sapere cosa significano."],
      credit="BENDER & GEBRU, 2021", dur=4.6,
      gif=("parrot GIF.gif", "RIPETE. CON STILE.", 2.0)),
 dict(id="halluc", kind="img", img="v2-hallucination.png", num="PAROLA 03/08",
      big=[("ALLUCINAZIONE", FB)], roman=None,
      defs=["Quando il modello inventa,", "con totale sicurezza."],
      credit="WOTY CAMBRIDGE 2023", dur=4.4,
      gif=("serpente allucinato.gif", "IL MODELLO NE È SICURISSIMO.", 2.0)),
 dict(id="jail", kind="img", img="v2-jailbreak.png", num="PAROLA 04/08",
      big=[("JAILBREAK", FB)], roman=None,
      defs=["Convincere l'AI a fare ciò", "che le è stato vietato."],
      credit="DAL TERMINE PER IPHONE E KINDLE SBLOCCATI", dur=4.4,
      gif=("break prison GIF.gif", "LA GABBIA, VISTA DA DENTRO.", 2.0)),
 dict(id="slop", kind="img", img="v2-slop.png", num="PAROLA 05/08",
      big=[("SLOP", FB)], roman=None,
      defs=["La brodaglia che nessuno ha chiesto", "e nessuno leggerà."],
      credit="WOTY MERRIAM-WEBSTER 2025", dur=4.4,
      gif=("slop.gif", "E NE ARRIVA ANCORA.", 2.0)),
 dict(id="clank", kind="type", img=None, num="PAROLA 06/08",
      big=[("CLANKER", FB)], roman="«FERRAGLIA», «SECCHIO DI BULLONI»",
      defs=["Il dispregiativo per i chatbot.", "Rubato a Star Wars."],
      credit="TERMINE VIRALE SU TIKTOK, 2025", dur=4.4,
      gif=("Star Wars Doom GIF.gif", "LA FERRAGLIA IN QUESTIONE.", 2.0)),
 dict(id="blues", kind="img", img="v2-pen.png", num="PAROLA 07/08",
      big=[("AI BLUES", FB)], roman=None,
      defs=["Generi, ma non stai creando.", "Nostalgia dell'analogico."],
      credit="L'HO INVENTATA IO", dur=4.8,
      gif=("nostalgia analogico inserimento tape.gif", "RICORDI QUANDO SI RIAVVOLGEVA?", 2.2)),
 dict(id="debt", kind="img", img="v2-mountain.png", num="PAROLA 08/08",
      big=[("AI READING", FB), ("DEBT", FB)], roman=None,
      defs=["Più testo di quanto", "ne leggerai mai."],
      credit="L'HO INVENTATA IO", dur=4.8,
      gif=("reading debt.gif", "IL NON-LETTO TI GUARDA.", 2.0)),
 dict(id="cta", kind="img", img="v2-bubbles.png", num="FINE — TOCCA A TE",
      big=[("E TU?", FB)], roman=None,
      defs=["Ne hai inventata una tua?", "Scrivila nei commenti ↓"],
      credit="", dur=4.4, gif=None),
 dict(id="follow", kind="type", img=None, num="LA SERIE CONTINUA",
      big=[("SEGUIMI", FB)], roman=None,
      defs=["Strumenti, pratiche e percorsi alternativi", "per chi scrive e per chi sviluppa."],
      credit="", dur=4.2, gif=None, inline_gif="seguimi.gif"),
]

def gif_frames(name, target_w=880):
    im = Image.open(os.path.join(GIFD, name))
    out = []
    for f in ImageSequence.Iterator(im):
        fr = f.convert("RGB")
        k = target_w / fr.width
        fr = fr.resize((target_w, int(fr.height * k)), Image.NEAREST)
        out.append(fr)
    return out

def draw_insert(gframes, gfr_idx, caption, label=None):
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    g = gframes[gfr_idx % len(gframes)]
    gx, gy = (W - g.width) // 2, (H - g.height) // 2 - 60
    # scanline sul gif
    gg = g.copy()
    px = gg.load()
    for yy in range(0, gg.height, 3):
        for xx in range(gg.width):
            r, gr, b = px[xx, yy]
            px[xx, yy] = (int(r * .72), int(gr * .72), int(b * .72))
    img.paste(gg, (gx, gy))
    # cornice
    d.rectangle([gx - 4, gy - 4, gx + g.width + 4, gy + g.height + 4], outline=BONE, width=4)
    L = 46
    for cx, cy, dx, dy in [(gx-4, gy-4, 1, 1), (gx+g.width+4, gy-4, -1, 1),
                           (gx-4, gy+g.height+4, 1, -1), (gx+g.width+4, gy+g.height+4, -1, -1)]:
        d.line([cx, cy, cx + L * dx, cy], fill=ACID, width=6)
        d.line([cx, cy, cx, cy + L * dy], fill=ACID, width=6)
    if label:
        mono_row(d, (70, 300), label, F(FMB, 26), NERV, 4)
    fm = F(FM, 30)
    tw = sum(d.textlength(c, font=fm) + 4 for c in caption)
    mono_row(d, ((W - tw) / 2, gy + g.height + 60), caption, fm, BONE, 4)
    return img

def render_scene(si, sc, frame_start):
    tmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    nfr_content = int(sc["dur"] * FPS)
    gframes, ins_n, caption = None, 0, ""
    if sc["gif"]:
        gname, caption, gdur = sc["gif"]
        if os.path.exists(os.path.join(GIFD, gname)):
            gframes = gif_frames(gname)
            ins_n = int(gdur * FPS)
        else:
            print(f"  ! gif mancante: {gname} — scena senza insert")

    # asset immagine
    ill = None
    if sc["img"]:
        src = Image.open(os.path.join(V2, sc["img"])).convert("RGB")
        bh = 850
        k = min(900 / src.width, bh / src.height)
        ill = src.resize((int(src.width * k), int(src.height * k)), Image.LANCZOS)

    # gif inline (dentro la scena, sotto il testo)
    inline = None
    if sc.get("inline_gif") and os.path.exists(os.path.join(GIFD, sc["inline_gif"])):
        inline = gif_frames(sc["inline_gif"], target_w=620)
        # scanline pre-applicata una volta sola
        import numpy as _np
        proc = []
        for g in inline:
            a = _np.array(g).astype(_np.float32)
            a[::3] *= 0.72
            proc.append(Image.fromarray(a.astype('uint8')))
        inline = proc

    # font titolo
    is_type = sc["kind"] == "type"
    nb = len(sc["big"])
    bigfonts = []
    for line, fpath in sc["big"]:
        base = (300 if fpath == FCJK else 240) if is_type else (150 if nb == 1 else 118)
        if is_type and fpath == FCJK and len(line) >= 4:
            base = 230
        bigfonts.append(fit(tmp, line, fpath, base, 940))

    # layer titolo pre-renderizzato (per lo slam)
    tl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dt = ImageDraw.Draw(tl)
    if is_type:
        total_h = sum(f.size + 24 for f in bigfonts)
        ty = 620 if nb == 1 else 540
    else:
        ty = 1155 if nb == 1 else 1085
    yy = ty
    for (line, _), f in zip(sc["big"], bigfonts):
        dt.text((70, yy), line, font=f, fill=BONE)
        yy += int(f.size * 1.02)
    title_bottom = yy

    fd = F(FB, 50 if is_type else 44)
    fcred = F(FM, 24)
    fnum = F(FMB, 26)

    for fr in range(nfr_content + ins_n):
        idx = frame_start + fr
        # ---- fase insert ----
        if fr >= nfr_content:
            gi = (fr - nfr_content) // 2  # gif a ~15fps
            draw_insert(gframes, gi, caption, sc.get("gif_label")).save(
                os.path.join(FRAMES, f"f{idx:05d}.jpg"), quality=90)
            continue

        img = Image.new("RGBA", (W, H), INK + (255,))
        d = ImageDraw.Draw(img)

        # immagine di fondo (scene img): entra con taglio secco a fr=0
        if ill is not None:
            img.paste(ill, ((W - ill.width) // 2, 300 + (850 - ill.height) // 2))

        # flash frame prima dello slam del titolo
        if fr == 4:
            d.rectangle([0, 0, W, H], fill=(255, 255, 255, 210))
        if fr == 5:
            d.rectangle([0, 0, W, H], fill=ACID + (70,))

        # titolo: slam scala 1.3 -> 1.0 in 5 frame
        p_t = ph(fr, 5, 5)
        if p_t > 0:
            s = 1.3 - 0.3 * ease_out(p_t)
            if s != 1.0:
                nw, nh = int(W * s), int(H * s)
                lay = tl.resize((nw, nh), Image.BILINEAR)
                ox = int(70 - 70 * s)
                oy = int(ty - ty * s)
                img.alpha_composite(lay, (ox, oy))
            else:
                img.alpha_composite(tl)

        # microtesto typewriter
        n_chars = int(ph(fr, 0, 18) * len(sc["num"]))
        mono_row(d, (70, 268), sc["num"], fnum, ACID, 4, n=n_chars)

        # roman (solo type card) — più in basso se il titolo è CJK
        roman_gap = 150 if sc["big"][0][1] == FCJK else 40
        if sc["roman"]:
            p = ph(fr, 14, 8)
            if p > 0:
                fro = F(FM, 28)
                mono_row(d, (70, title_bottom + roman_gap), sc["roman"], fro,
                         tuple(int(c * p) for c in ACID), 3)

        # barra NERV: wipe
        p_r = ease_out(ph(fr, 12, 10))
        if p_r > 0:
            ry = (title_bottom + roman_gap + (70 if sc["roman"] else 0)) if is_type else 1385
            d.rectangle([70, ry, 70 + int(540 * p_r), ry + 12], fill=NERV)

        # definizioni: comparsa secca riga per riga
        base_dy = (title_bottom + roman_gap + (70 if sc["roman"] else 0) + 70) if is_type else 1430
        for li, line in enumerate(sc["defs"]):
            if fr >= 20 + li * 7:
                d.text((70, base_dy + li * (66 if is_type else 58)), line, font=fd, fill=BONE)

        # credit mono
        if sc["credit"] and fr >= 38:
            cy = base_dy + len(sc["defs"]) * (66 if is_type else 58) + 40
            mono_row(d, (70, cy), sc["credit"], fcred, ASH, 3)

        # gif inline sotto il testo
        if inline and fr >= 30:
            g = inline[((fr - 30) // 2) % len(inline)]
            gy = base_dy + len(sc["defs"]) * (66 if is_type else 58) + 70
            gx = (W - g.width) // 2
            img.paste(g, (gx, gy))
            d.rectangle([gx - 4, gy - 4, gx + g.width + 4, gy + g.height + 4],
                        outline=BONE, width=4)
            L = 36
            for cx, cy, dx, dy2 in [(gx-4, gy-4, 1, 1), (gx+g.width+4, gy-4, -1, 1),
                                    (gx-4, gy+g.height+4, 1, -1), (gx+g.width+4, gy+g.height+4, -1, -1)]:
                d.line([cx, cy, cx + L * dx, cy], fill=ACID, width=6)
                d.line([cx, cy, cx, cy + L * dy2], fill=ACID, width=6)

        # contatore basso a destra
        cnt = f"{si+1:02d} / {len(S):02d}"
        mono_row(d, (W - 200, 1800), cnt, F(FMB, 28), ASH, 3)

        img.convert("RGB").save(os.path.join(FRAMES, f"f{idx:05d}.jpg"), quality=90)

    return nfr_content + ins_n

# clanker/botshit: se l'immagine v2 esiste, la scena diventa card immagine
for sc in S:
    if sc["id"] == "clank" and os.path.exists(os.path.join(V2, "v2-clanker.png")):
        sc["kind"], sc["img"], sc["roman"] = "img", "v2-clanker.png", None
    if sc["id"] == "botshit" and os.path.exists(os.path.join(V2, "v2-botshit.png")):
        sc["kind"], sc["img"], sc["roman"] = "img", "v2-botshit.png", None

# le gif mancanti non contano nelle durate
for sc in S:
    if sc["gif"] and not os.path.exists(os.path.join(GIFD, sc["gif"][0])):
        sc["gif"] = None

# durate cumulative
lens = []
for sc in S:
    n = int(sc["dur"] * FPS) + (int(sc["gif"][2] * FPS) if sc["gif"] else 0)
    lens.append(n)
starts = [sum(lens[:i]) for i in range(len(S))]

ONLY = int(sys.argv[1]) if len(sys.argv) > 1 else None
if ONLY is not None and ONLY >= 0:
    render_scene(ONLY, S[ONLY], starts[ONLY])
    print(f"scena {ONLY} ok, {lens[ONLY]} frame, start {starts[ONLY]}")
elif ONLY == -1:
    # passata glitch identica alla v1
    import numpy as np
    rng = np.random.default_rng(7)
    GL = 6
    def glitch_mix(cur_p, nxt_p, t):
        cur = np.array(Image.open(cur_p)).astype(np.uint8)
        nxt = np.array(Image.open(nxt_p)).astype(np.uint8)
        out = cur.copy()
        h, w, _ = out.shape
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
        nxt = os.path.join(FRAMES, f"f{s+70:05d}.jpg")
        for i in range(GL, 0, -1):
            t = (GL - i + 1) / GL
            p = os.path.join(FRAMES, f"f{s-i:05d}.jpg")
            glitch_mix(p, nxt, t).save(p, quality=90)
    print("glitch ok, tot frame:", sum(lens), "=", sum(lens) / FPS, "s")
