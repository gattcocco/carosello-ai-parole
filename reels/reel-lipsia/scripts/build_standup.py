"""Assembla 'La discarica dei libri' — versione stand-up, solo testo.

Terzo approccio (sostituisce build_fullscreen.py per questa versione):
- niente audio: la musica la aggiunge l'autore da Instagram in fase di
  pubblicazione;
- il testo in overlay E' il contenuto (non ci sono sottotitoli aggiunti
  dopo): battute brevi, in stile stand-up, con hook iniziale e struttura
  "parti dalla fine";
- montaggio artistico: un beat di testo puo' restare a schermo mentre le
  inquadrature sotto si accostano (biblioteca vs discarica), invece di
  cambiare testo a ogni taglio. Niente transizioni glitch: su un video
  fatto per essere letto, il glitch disturba la lettura piu' di quanto
  aggiunga in stile — tagli netti, e basta.

Legge content/timeline_v3.json. Riusa le utility di build_fullscreen.py
per il footage a tutto schermo.

Uso:
    .venv/Scripts/python.exe scripts/build_standup.py
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ColorClip, CompositeVideoClip, ImageClip, concatenate_videoclips

from build_fullscreen import build_clip_shot, image_kenburns_clip

ROOT = Path(__file__).resolve().parent.parent

FONT_PATH = "C:/Windows/Fonts/BOD_CB.TTF"
BONE = (242, 239, 233)
ACID = (166, 255, 0)
INK = (11, 11, 13)

SAFE_WIDTH = 940
MAX_FONT = 92
MIN_FONT = 52


def wrap_words(draw, word_flags, font, max_width, space_w):
    lines, current, current_w = [], [], 0
    for word, is_hl in word_flags:
        ww = draw.textlength(word, font=font)
        added = ww if not current else ww + space_w
        if current and current_w + added > max_width:
            lines.append(current)
            current, current_w = [(word, is_hl, ww)], ww
        else:
            current.append((word, is_hl, ww))
            current_w += added
    if current:
        lines.append(current)
    return lines


def split_highlight(text, highlight):
    if not highlight:
        return [(text, False)]
    idx = text.lower().find(highlight.lower())
    if idx == -1:
        return [(text, False)]
    return [(text[:idx], False), (text[idx:idx + len(highlight)], True), (text[idx + len(highlight):], False)]


def caption_overlay(text, highlight, width, height, duration):
    segments = split_highlight(text, highlight)
    word_flags = [(w, is_hl) for seg, is_hl in segments for w in seg.split(" ") if w]

    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    font_size = MAX_FONT
    while True:
        font = ImageFont.truetype(FONT_PATH, font_size)
        space_w = tmp.textlength(" ", font=font)
        lines = wrap_words(tmp, word_flags, font, SAFE_WIDTH, space_w)
        if len(lines) <= 4 or font_size <= MIN_FONT:
            break
        font_size -= 4

    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * 1.22)
    text_h = line_h * len(lines)
    pad_x, pad_y = 60, 50
    scrim_h = text_h + pad_y * 2

    img = Image.new("RGBA", (width, scrim_h), (0, 0, 0, 0))
    scrim = Image.new("RGBA", (width, scrim_h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(scrim)
    sdraw.rectangle([0, 0, width, scrim_h], fill=(*INK, 165))
    img = Image.alpha_composite(img, scrim)
    draw = ImageDraw.Draw(img)

    y = pad_y
    for line in lines:
        line_w = sum(w for _, _, w in line) + space_w * (len(line) - 1)
        x = (width - line_w) / 2
        for word, is_hl, ww in line:
            draw.text((x, y), word, font=font, fill=(*(ACID if is_hl else BONE), 255))
            x += ww + space_w
        y += line_h

    y_pos = height - scrim_h - 260
    return ImageClip(np.array(img)).with_duration(duration).with_position((0, y_pos))


def build_visual_shot(shot, duration, width, height, fps):
    if shot["kind"] == "clip":
        return build_clip_shot(shot["source"], shot.get("seek", 0), duration, width, height)
    if shot["kind"] == "image":
        return image_kenburns_clip(shot["source"], duration, width, height, shot.get("zoom", 1.1), fps)
    if shot["kind"] == "solid":
        return ColorClip(size=(width, height), color=INK).with_duration(duration)
    raise ValueError(f"kind sconosciuto: {shot['kind']}")


def main():
    timeline_name = sys.argv[1] if len(sys.argv) > 1 else "timeline_v3.json"
    data = json.loads((ROOT / "content" / timeline_name).read_text(encoding="utf-8"))
    width, height, fps = data["width"], data["height"], data["fps"]

    # 1) flatten shots (splitting each beat's duration evenly across its shots)
    flat_shots = []
    caption_layers = []  # (start_time, duration, text, highlight)
    t_cursor = 0.0
    for beat in data["beats"]:
        n = len(beat["shots"])
        per_shot_dur = beat["duration"] / n
        for shot in beat["shots"]:
            flat_shots.append({**shot, "duration": per_shot_dur})
        caption_layers.append((t_cursor, beat["duration"], beat["text"], beat.get("highlight")))
        t_cursor += beat["duration"]

    total_duration = t_cursor
    print(f"Beat: {len(data['beats'])} · shot: {len(flat_shots)} · durata totale: {total_duration:.2f}s")

    # 2) build each visual shot
    shot_clips = [build_visual_shot(s, s["duration"], width, height, fps) for s in flat_shots]
    base = concatenate_videoclips(shot_clips, method="chain")

    # 3) captions, one per beat, persisting across its shot(s) — tagli netti,
    # niente glitch: su un video da leggere il glitch disturba la lettura.
    overlays = []
    for start, dur, text, highlight in caption_layers:
        cap = caption_overlay(text, highlight, width, height, dur).with_start(start)
        overlays.append(cap)

    final = CompositeVideoClip([base] + overlays, size=(width, height)).with_duration(total_duration)

    out_name = data.get("out_name", "discarica-dei-libri-v3-standup.mp4")
    out_path = ROOT / "dist" / out_name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(str(out_path), fps=fps, codec="libx264", audio=False)
    print(f"Draft salvato: {out_path}")


if __name__ == "__main__":
    main()
