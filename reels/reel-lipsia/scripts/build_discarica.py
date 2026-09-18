"""Assembla 'La discarica dei libri' da content/timeline.json.

Segue la grammatica visiva di brand-manual-v2.md (palette INK/BONE/ACID,
tipografia, safe area) adattata all'eccezione dichiarata in primo-montaggio.md:
footage 4:3 non deformato, centrato su fondo nero invece della finestra 16:9
di default. Testo (microheader, caption, title card, endcard, etichetta del
fermo immagine) e' renderizzato con PIL per poter colorare in ACID solo la
keyword indicata in ogni segmento, poi composito con moviepy.

Uso:
    .venv/Scripts/python.exe scripts/build_discarica.py
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
)

ROOT = Path(__file__).resolve().parent.parent

FONT_DIR = Path("C:/Windows/Fonts")
FONT_DISPLAY = str(FONT_DIR / "BOD_CB.TTF")       # Bodoni MT Condensed Bold
FONT_NARRATIVE = str(FONT_DIR / "segoeuib.ttf")   # Segoe UI Bold
FONT_MONO = str(FONT_DIR / "consolab.ttf")        # Consolas Bold

INK = (11, 11, 13)
BONE = (242, 239, 233)
ACID = (166, 255, 0)

SAFE_LEFT = 70
SAFE_RIGHT = 910
SAFE_WIDTH = SAFE_RIGHT - SAFE_LEFT

MICROHEADER_Y = 70
MEDIA_TOP = 160
CAPTION_TOP = 1080
SHOW_TITLE = "LA DISCARICA DEI LIBRI"


def wrap_words(draw, word_flags, font, max_width, space_w):
    lines = []
    current, current_w = [], 0
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


def split_highlight(text: str, highlight: str | None):
    if not highlight:
        return [(text, False)]
    idx = text.lower().find(highlight.lower())
    if idx == -1:
        return [(text, False)]
    return [
        (text[:idx], False),
        (text[idx: idx + len(highlight)], True),
        (text[idx + len(highlight):], False),
    ]


def text_image(
    text: str,
    font_path: str,
    max_font_size: int,
    max_width: int,
    highlight: str | None = None,
    color=BONE,
    accent=ACID,
    align: str = "left",
    min_font_size: int = 34,
    max_lines: int = 5,
):
    segments = split_highlight(text, highlight)
    word_flags = []
    for seg_text, is_hl in segments:
        for w in seg_text.split(" "):
            if w:
                word_flags.append((w, is_hl))

    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    font_size = max_font_size
    while True:
        font = ImageFont.truetype(font_path, font_size)
        space_w = tmp.textlength(" ", font=font)
        lines = wrap_words(tmp, word_flags, font, max_width, space_w)
        if len(lines) <= max_lines or font_size <= min_font_size:
            break
        font_size -= 4

    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * 1.18)
    img_w = max_width + 40
    img_h = line_h * len(lines) + 20
    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    space_w = draw.textlength(" ", font=font)

    y = 10
    for line in lines:
        line_w = sum(w for _, _, w in line) + space_w * (len(line) - 1)
        x = 0 if align == "left" else (img_w - line_w) / 2
        for word, is_hl, ww in line:
            draw.text((x, y), word, font=font, fill=(*(accent if is_hl else color), 255))
            x += ww + space_w
        y += line_h
    return img


def pil_to_clip(img: Image.Image, duration: float, pos):
    return ImageClip(np.array(img)).with_duration(duration).with_position(pos)


def microheader_clip(index: int, total: int, duration: float):
    img = text_image(
        f"{SHOW_TITLE} · {index:02d}/{total:02d}",
        FONT_MONO, 30, SAFE_WIDTH, color=BONE, align="left", max_lines=1,
    )
    return pil_to_clip(img, duration, (SAFE_LEFT, MICROHEADER_Y))


def caption_clip(caption: str, highlight, duration: float, top: int = CAPTION_TOP):
    img = text_image(
        caption, FONT_NARRATIVE, 60, SAFE_WIDTH,
        highlight=highlight, color=BONE, accent=ACID, align="left", max_lines=5,
    )
    return pil_to_clip(img, duration, (SAFE_LEFT, top))


def fit_4_3_on_canvas(clip, width=1080):
    resized = clip.resized(width=width)
    return resized


TITLE_TOP = 740


def build_title_segment(seg, width, height):
    duration = seg["duration"]
    bg = ColorClip(size=(width, height), color=INK).with_duration(duration)
    title_img = text_image(
        seg["title_text"], FONT_DISPLAY, 150, SAFE_WIDTH,
        color=ACID, align="center", max_lines=1, min_font_size=70,
    )
    title_clip = ImageClip(np.array(title_img)).with_duration(duration)
    title_clip = title_clip.with_position(("center", TITLE_TOP))
    cap_top = max(CAPTION_TOP, TITLE_TOP + title_img.height + 60)
    cap = caption_clip(seg["caption"], seg.get("highlight"), duration, top=cap_top)
    return CompositeVideoClip([bg, title_clip, cap], size=(width, height)).with_duration(duration)


def build_endcard_segment(seg, width, height):
    duration = seg["duration"]
    bg = ColorClip(size=(width, height), color=INK).with_duration(duration)
    title_img = text_image(
        seg["title_text"], FONT_DISPLAY, 130, SAFE_WIDTH,
        color=BONE, align="center", max_lines=1, min_font_size=60,
    )
    title_clip = ImageClip(np.array(title_img)).with_duration(duration).with_position(("center", TITLE_TOP))
    bar_top = TITLE_TOP + title_img.height + 30
    bar = ColorClip(size=(240, 8), color=ACID).with_duration(duration).with_position(("center", bar_top))
    cap_top = max(CAPTION_TOP, bar_top + 60)
    cap = caption_clip(seg["caption"], seg.get("highlight"), duration, top=cap_top)
    return CompositeVideoClip([bg, title_clip, bar, cap], size=(width, height)).with_duration(duration)


def build_clip_segment(seg, width, height, index, total):
    asset_path = (ROOT / "content" / seg["asset"]).resolve()
    raw = VideoFileClip(str(asset_path))
    duration = min(seg["duration"], raw.duration)

    bg = ColorClip(size=(width, height), color=INK).with_duration(duration)
    media = fit_4_3_on_canvas(raw, width=width).with_duration(duration).with_position((0, MEDIA_TOP))

    layers = [bg, media, microheader_clip(index, total, duration), caption_clip(seg["caption"], seg.get("highlight"), duration)]
    return CompositeVideoClip(layers, size=(width, height)).with_duration(duration)


def build_freeze_segment(seg, width, height, index, total):
    duration = seg["duration"]
    asset_path = (ROOT / "content" / seg["asset"]).resolve()
    bg = ColorClip(size=(width, height), color=INK).with_duration(duration)

    with VideoFileClip(str(asset_path)) as src:
        frame = src.get_frame(seg["freeze_at"])
    dimmed = (frame.astype(np.float32) * 0.55).astype(np.uint8)
    still = Image.fromarray(dimmed)
    still = still.resize((width, round(width * still.height / still.width)))
    media = pil_to_clip(still.convert("RGBA"), duration, (0, MEDIA_TOP))

    label_img = text_image(seg["label"], FONT_MONO, 32, SAFE_WIDTH, color=ACID, align="left", max_lines=1)
    label = pil_to_clip(label_img, duration, (SAFE_LEFT, MEDIA_TOP + still.height + 20))

    layers = [
        bg, media,
        microheader_clip(index, total, duration),
        label,
        caption_clip(seg["caption"], seg.get("highlight"), duration),
    ]
    return CompositeVideoClip(layers, size=(width, height)).with_duration(duration)


def main():
    data = json.loads((ROOT / "content" / "timeline.json").read_text(encoding="utf-8"))
    width, height, fps = data["width"], data["height"], data["fps"]
    segments = data["segments"]
    total = len(segments)

    clips = []
    for seg in segments:
        if seg["type"] == "title":
            clips.append(build_title_segment(seg, width, height))
        elif seg["type"] == "endcard":
            clips.append(build_endcard_segment(seg, width, height))
        elif seg["type"] == "clip":
            clips.append(build_clip_segment(seg, width, height, seg["id"], total))
        elif seg["type"] == "freeze":
            clips.append(build_freeze_segment(seg, width, height, seg["id"], total))
        else:
            raise ValueError(f"Tipo di segmento sconosciuto: {seg['type']}")

    final = concatenate_videoclips(clips, method="compose")

    audio_path = ROOT / "dist" / "audio" / "narrazione-discarica.wav"
    if audio_path.exists():
        narration = AudioFileClip(str(audio_path))
        final = final.with_audio(narration)
    else:
        print("Nessuna narrazione trovata in dist/audio/: esporto muto. "
              "Lancia prima scripts/generate_narration.py.")

    out_path = ROOT / "dist" / "discarica-dei-libri-v1.mp4"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(str(out_path), fps=fps, codec="libx264", audio_codec="aac")
    print(f"Draft salvato: {out_path}")


if __name__ == "__main__":
    main()
