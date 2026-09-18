"""Assembla 'La discarica dei libri' — versione a tutto schermo.

Nuovo approccio (sostituisce build_discarica.py):
- footage d'archivio a piena schermata (cover-crop 9:16, niente fondo nero);
- voce reale dell'autore (non TTS) come unica traccia audio;
- nessun sottotitolo/testo in overlay: verranno aggiunti dall'app di Instagram;
- transizioni glitch (RGB split + slice orizzontali) tra ogni taglio.

Legge content/timeline_v2.json: ogni "beat" del testo pesa sulla durata in
proporzione alle sue parole, poi tutto viene rinormalizzato sulla durata
reale della voce.

Uso:
    .venv/Scripts/python.exe scripts/build_fullscreen.py
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image
from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    VideoClip,
    VideoFileClip,
    concatenate_videoclips,
)
from moviepy.video.fx import Loop

ROOT = Path(__file__).resolve().parent.parent


def cover_resize_crop(clip, width, height):
    scale = max(width / clip.w, height / clip.h)
    resized = clip.resized(scale)
    x_center, y_center = resized.w / 2, resized.h / 2
    return resized.cropped(width=width, height=height, x_center=x_center, y_center=y_center)


def build_clip_shot(source: str, seek: float, duration: float, width: int, height: int):
    path = ROOT / "assets" / "clips" / f"{source}.mp4"
    if not path.exists():
        raise FileNotFoundError(f"Asset clip mancante per l'id '{source}': {path}")
    raw = VideoFileClip(str(path))
    needed = seek + duration
    if raw.duration < needed:
        raw = raw.with_effects([Loop(duration=needed)])
    sub = raw.subclipped(seek, needed)
    return cover_resize_crop(sub, width, height).with_duration(duration)


IMAGES_DIR = ROOT / "assets" / "images"
KATLENBURG_DIR = IMAGES_DIR / "katlenburg"
BRAND_DIR = ROOT.parent.parent / "brand" / "loghi"
MARCHI_DIR = ROOT / "assets" / "images" / "ddr-marchi" / "card"

IMAGE_SOURCES = {
    # Non versionati (diritti di terzi, vedi assets/SOURCES.md sez. D):
    # stanno nell'episodio ma restano fuori da git.
    "trabant": IMAGES_DIR / "trabant-manuale-copertina.webp",
    "pastore": IMAGES_DIR / "martin-weskott.avif",
    "kat_burgberg": KATLENBURG_DIR / "katlenburg-burgberg-nordest-916.jpg",
    "kat_merian": KATLENBURG_DIR / "katlenburg-merian-1654.jpg",
    "kat_chiesa": KATLENBURG_DIR / "katlenburg-st-johannes-916.jpg",
    "kat_cripta": KATLENBURG_DIR / "katlenburg-cripta-romanica.jpg",
    "kat_refettorio": KATLENBURG_DIR / "katlenburg-ex-refettorio.jpg",
    "kat_granaio": KATLENBURG_DIR / "katlenburg-granaio-in-pietra.jpg",
    "kat_libri": KATLENBURG_DIR / "katlenburg-granaio-interno-libri.jpg",
    # Card finale: e' gia' 941x1672, cioe' 9:16 esatto, e porta la sua CTA.
    # Va usata con zoom 1.0 e senza didascalia, altrimenti la fascia del testo
    # copre "Iscriviti" e "Link in bio".
    "cta_newsletter": BRAND_DIR / "Poster per newsletter tra idee e strumenti.png",

    # Banconote della DDR, gia' composte in 1080x1920 da compose_banknotes.py.
    # Le scansioni originali sono quasi quadrate e il cover-crop ne taglierebbe
    # meta' larghezza: qui la banconota e' gia' intera sul fondo del brand,
    # quindi vanno usate con zoom 1.0.
    "marco_10":  MARCHI_DIR / "marco-10.png",    # Clara Zetkin / operaia al banco
    "marco_20":  MARCHI_DIR / "marco-20.png",    # Goethe / aula scolastica
    "marco_50":  MARCHI_DIR / "marco-50.png",    # impianto industriale
    "marco_100": MARCHI_DIR / "marco-100.png",   # Marx / edifici
    "marco_200": MARCHI_DIR / "marco-200.png",   # scena sociale
    "marco_500": MARCHI_DIR / "marco-500.png",
    "marco_100_1964": MARCHI_DIR / "marco-1964-100.png",  # Marx / Porta di Brandeburgo
}


def image_kenburns_clip(source: str, duration: float, width: int, height: int, zoom: float, fps: int):
    if source not in IMAGE_SOURCES:
        raise KeyError(f"Nessun asset immagine registrato per l'id '{source}'. "
                        f"Id disponibili: {sorted(IMAGE_SOURCES)}")
    image_path = IMAGE_SOURCES[source]
    if not image_path.exists():
        raise FileNotFoundError(f"Asset mancante per l'id '{source}': {image_path}")
    img = Image.open(image_path).convert("RGB")

    # cover-crop to an oversized canvas (width*zoom x height*zoom), then zoom
    # in toward the native 1:1 crop over the duration of the shot.
    big_w, big_h = int(width * zoom), int(height * zoom)
    scale = max(big_w / img.width, big_h / img.height)
    resized = img.resize((int(img.width * scale) + 1, int(img.height * scale) + 1))
    x0 = (resized.width - big_w) // 2
    y0 = (resized.height - big_h) // 2
    big = np.array(resized.crop((x0, y0, x0 + big_w, y0 + big_h)))

    def frame_function(t):
        frac = min(max(t / duration, 0), 1)
        crop_w = int(big_w - (big_w - width) * frac)
        crop_h = int(big_h - (big_h - height) * frac)
        cx0 = (big_w - crop_w) // 2
        cy0 = (big_h - crop_h) // 2
        crop = big[cy0:cy0 + crop_h, cx0:cx0 + crop_w]
        frame = np.array(Image.fromarray(crop).resize((width, height)))
        return frame

    return VideoClip(frame_function=frame_function, duration=duration).with_fps(fps)


def make_glitch_overlay(frame_a: np.ndarray, frame_b: np.ndarray, duration: float, fps: int):
    h, w = frame_a.shape[:2]
    n_slices = 8
    slice_h = max(1, h // n_slices)

    def frame_function(t):
        frac = t / duration
        base = frame_a if frac < 0.5 else frame_b
        rng = np.random.default_rng(int(t * 1000))
        out = base.copy()
        for s in range(n_slices):
            y0 = s * slice_h
            y1 = min(h, y0 + slice_h)
            if rng.random() < 0.6:
                shift = int(rng.integers(-60, 60))
                out[y0:y1] = np.roll(out[y0:y1], shift, axis=1)
        shift_r = 10
        glitched = out.copy()
        glitched[:, :, 0] = np.roll(out[:, :, 0], shift_r, axis=1)
        if out.shape[2] > 2:
            glitched[:, :, 2] = np.roll(out[:, :, 2], -shift_r, axis=1)
        if rng.random() < 0.15:
            glitched = 255 - glitched
        return glitched

    return VideoClip(frame_function=frame_function, duration=duration).with_fps(fps)


def main():
    data = json.loads((ROOT / "content" / "timeline_v2.json").read_text(encoding="utf-8"))
    width, height, fps = data["width"], data["height"], data["fps"]
    min_shot = data["min_shot_seconds"]
    glitch_dur = data["glitch_seconds"]

    voice_path = (ROOT / "content" / data["voice_source"]).resolve()
    voice = AudioFileClip(str(voice_path))
    trim_start = data.get("voice_trim_start", 0)
    if trim_start:
        voice = voice.subclipped(trim_start, voice.duration)
    target_total = voice.duration

    # 1) raw weights -> per-shot durations
    flat_shots = []
    for beat in data["beats"]:
        words = len(beat["weight_text"].split())
        n = len(beat["shots"])
        per_shot_weight = words / n
        for shot in beat["shots"]:
            flat_shots.append({**shot, "weight": per_shot_weight})

    total_weight = sum(s["weight"] for s in flat_shots)
    for s in flat_shots:
        s["duration"] = max(min_shot, target_total * s["weight"] / total_weight)

    # rescale so the sum matches the voice track exactly
    raw_total = sum(s["duration"] for s in flat_shots)
    scale = target_total / raw_total
    for s in flat_shots:
        s["duration"] *= scale

    print(f"Voce: {target_total:.2f}s su {len(flat_shots)} shot (media {target_total/len(flat_shots):.2f}s/shot)")

    # 2) build each shot clip
    shot_clips = []
    for s in flat_shots:
        if s["kind"] == "clip":
            clip = build_clip_shot(s["source"], s.get("seek", 0), s["duration"], width, height)
        else:
            clip = image_kenburns_clip(s["source"], s["duration"], width, height, s.get("zoom", 1.1), fps)
        shot_clips.append(clip)

    base = concatenate_videoclips(shot_clips, method="chain")

    # 3) glitch overlays at each internal cut
    overlays = []
    t_cursor = 0.0
    for i in range(len(shot_clips) - 1):
        t_cursor += shot_clips[i].duration
        frame_a = shot_clips[i].get_frame(max(0, shot_clips[i].duration - 1 / fps))
        frame_b = shot_clips[i + 1].get_frame(0)
        glitch = make_glitch_overlay(frame_a, frame_b, glitch_dur, fps)
        glitch = glitch.with_start(t_cursor - glitch_dur / 2)
        overlays.append(glitch)

    final = CompositeVideoClip([base] + overlays, size=(width, height)).with_duration(base.duration)
    final = final.with_audio(voice)

    out_path = ROOT / "dist" / "discarica-dei-libri-v2-fullscreen.mp4"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(str(out_path), fps=fps, codec="libx264", audio_codec="aac")
    print(f"Draft salvato: {out_path}")


if __name__ == "__main__":
    main()
