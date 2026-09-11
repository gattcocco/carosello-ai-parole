#!/usr/bin/env python3
"""Renderer legacy del primo draft di Extra Coin.

Genera il master v0.4 da 60 secondi usando la traccia conservata in
``content/archive/draft-01/text-track.srt``. Il paper edit v0.5 da 96 secondi
vive nei documenti correnti, ma non è ancora implementato nel renderer. Gli
asset grezzi restano fuori da Git; il render finisce in ``dist/`` e la cache
in ``.cache/``.
"""

from __future__ import annotations

import argparse
import bisect
import functools
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont, ImageOps, ImageSequence


PROJECT = Path(__file__).resolve().parent
# Nel repository il progetto vive in reels/extra-coin; la copia di lavoro sul
# Desktop usa invece direttamente la cartella Extra Coin - Reel.
REPO = PROJECT.parent.parent if PROJECT.parent.name.lower() == "reels" else PROJECT
ASSETS = PROJECT / "assets"
SHOTS = ASSETS / "screenshots"
RAW = ASSETS / "raw"
CONTENT = PROJECT / "content"
LEGACY_SRT = CONTENT / "archive" / "draft-01" / "text-track.srt"
CACHE = REPO / ".cache" / "extra-coin-draft"
DIST = PROJECT / "dist"

W, H = 1080, 1920
FPS = 30
TOTAL_FRAMES = 60 * FPS
FOOTAGE_FPS = 15

INK = (11, 11, 13)
BONE = (242, 239, 233)
ACID = (166, 255, 0)
EVA = (91, 62, 150)
NERV = (255, 77, 0)
ASH = (74, 74, 80)

FONT_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
FONT_TITLE = FONT_DIR / "BOD_CB.TTF"
FONT_COPY_BOLD = FONT_DIR / "constanb.ttf"
FONT_COPY = FONT_DIR / "constan.ttf"
FONT_MONO = FONT_DIR / "consolab.ttf"

MEDIA_BOX = (70, 385, 1010, 914)
MEME_BOX = (160, 450, 920, 1020)
SCENE_STARTS = [0.0, 4.0, 10.0, 15.0, 21.0, 26.0, 32.0, 38.0, 43.5, 49.5, 54.0, 57.0]
SCENE_ENDS = [4.0, 10.0, 15.0, 21.0, 26.0, 32.0, 38.0, 43.5, 49.5, 54.0, 57.0, 60.0]
SCENE_ACCENTS = [NERV, EVA, ACID, NERV, NERV, ACID, NERV, EVA, EVA, ASH, NERV, ACID]


@dataclass(frozen=True)
class Cue:
    index: int
    start: float
    end: float
    text: str
    role: str


ROLES = [
    "title", "title", "copy",
    "title", "copy",
    "title", "copy", "meme",
    "title", "copy", "copy",
    "title", "response", "copy",
    "title", "title", "copy", "meme",
    "title", "copy", "response",
    "title", "copy", "copy",
    "title", "copy",
    "title", "closing",
    "cta", "end",
]


def parse_timecode(value: str) -> float:
    hours, minutes, rest = value.split(":")
    seconds, millis = rest.split(",")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000


def read_cues() -> list[Cue]:
    blocks = re.split(r"\r?\n\s*\r?\n", LEGACY_SRT.read_text(encoding="utf-8").strip())
    cues: list[Cue] = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        start_raw, end_raw = [part.strip() for part in lines[1].split("-->")]
        cues.append(Cue(int(lines[0]), parse_timecode(start_raw), parse_timecode(end_raw), "\n".join(lines[2:]), ROLES[len(cues)]))
    if len(cues) != len(ROLES):
        raise RuntimeError(
            f"Attese {len(ROLES)} cue, trovate {len(cues)} in {LEGACY_SRT}"
        )
    if abs(cues[0].start) > 0.001 or abs(cues[-1].end - 60.0) > 0.001:
        raise RuntimeError("La traccia testuale deve coprire esattamente 00:00–01:00")
    return cues


def find_ffmpeg() -> Path:
    configured = os.environ.get("FFMPEG_BINARY")
    if configured and Path(configured).is_file():
        return Path(configured)
    in_path = shutil.which("ffmpeg")
    if in_path:
        return Path(in_path)

    for dep_dir in (REPO / ".cache" / "render-deps-local", REPO / ".cache" / "render-deps"):
        try:
            if dep_dir.is_dir():
                sys.path.insert(0, str(dep_dir))
        except OSError:
            pass
    try:
        import imageio_ffmpeg  # type: ignore

        return Path(imageio_ffmpeg.get_ffmpeg_exe())
    except (ImportError, OSError, AttributeError):
        pass

    raise RuntimeError(
        "FFmpeg non trovato. Installa imageio-ffmpeg==0.6.0 oppure imposta "
        "FFMPEG_BINARY con il percorso dell'eseguibile."
    )


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.is_file():
        raise FileNotFoundError(f"Font non trovato: {path}")
    return ImageFont.truetype(str(path), size)


def fit_inside(image: Image.Image, size: tuple[int, int], *, resample: Image.Resampling = Image.Resampling.LANCZOS) -> Image.Image:
    source = image.convert("RGB")
    ratio = min(size[0] / source.width, size[1] / source.height)
    result = source.resize(
        (max(1, int(round(source.width * ratio))), max(1, int(round(source.height * ratio)))),
        resample,
    )
    canvas = Image.new("RGB", size, INK)
    canvas.paste(result, ((size[0] - result.width) // 2, (size[1] - result.height) // 2))
    return canvas


def cover(image: Image.Image, size: tuple[int, int], *, centering: tuple[float, float] = (0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, Image.Resampling.LANCZOS, centering=centering)


def tracking_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, face: ImageFont.FreeTypeFont,
                  fill: tuple[int, int, int], tracking: int = 3, limit: int | None = None) -> None:
    x, y = xy
    shown = text if limit is None else text[:limit]
    for char in shown:
        draw.text((x, y), char, font=face, fill=fill)
        x += int(draw.textlength(char, font=face)) + tracking


def text_metrics(lines: list[str], face: ImageFont.FreeTypeFont, spacing: int) -> tuple[int, int]:
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    widths = [int(probe.textlength(line, font=face)) for line in lines]
    line_height = max(1, face.getbbox("Ag")[3] - face.getbbox("Ag")[1])
    return max(widths, default=0), line_height * len(lines) + spacing * max(0, len(lines) - 1)


def fit_face(path: Path, lines: list[str], start: int, minimum: int, max_width: int, max_height: int,
             spacing_ratio: float = 0.16) -> tuple[ImageFont.FreeTypeFont, int]:
    for size in range(start, minimum - 1, -2):
        face = font(path, size)
        spacing = max(6, int(size * spacing_ratio))
        width, height = text_metrics(lines, face, spacing)
        if width <= max_width and height <= max_height:
            return face, spacing
    face = font(path, minimum)
    return face, max(6, int(minimum * spacing_ratio))


def draw_block(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, face: ImageFont.FreeTypeFont,
               fill: tuple[int, int, int], spacing: int, *, stroke: int = 0) -> None:
    draw.multiline_text(xy, text, font=face, fill=fill, spacing=spacing, stroke_width=stroke,
                        stroke_fill=INK if stroke else None)


def add_corner_marks(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], accent: tuple[int, int, int]) -> None:
    x0, y0, x1, y1 = box
    length = 42
    width = 6
    for x, y, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        draw.line((x, y, x + dx * length, y), fill=accent, width=width)
        draw.line((x, y, x, y + dy * length), fill=accent, width=width)


class Renderer:
    def __init__(self, ffmpeg: Path) -> None:
        self.ffmpeg = ffmpeg
        self.cues = read_cues()
        self.cue_starts = [cue.start for cue in self.cues]
        self.images = {
            path.stem: Image.open(path).convert("RGB")
            for path in SHOTS.iterdir()
            if path.suffix.lower() in {".jpg", ".jpeg", ".png"}
        }
        self.media_stills = {
            name: fit_inside(image, (MEDIA_BOX[2] - MEDIA_BOX[0], MEDIA_BOX[3] - MEDIA_BOX[1]))
            for name, image in self.images.items()
        }
        self.hook = cover(self.images["sogno-mika"], (W, H), centering=(0.5, 0.5))
        self.gifs = {
            "a": self._load_gif(RAW / "memes" / "meme-a-scettico.gif", Image.Resampling.NEAREST),
            "b": self._load_gif(RAW / "memes" / "meme-b-esausto.gif", Image.Resampling.LANCZOS),
        }
        self.footage_dir = CACHE / "footage-15fps"
        self._ensure_footage_frames()
        self.footage_files = sorted(self.footage_dir.glob("frame-*.jpg"))
        if not self.footage_files:
            raise RuntimeError("Nessun frame estratto dal footage ufficiale")

    @staticmethod
    def display_text(cue: Cue) -> str:
        # A capo solo grafici: le parole restano identiche alla traccia SRT.
        overrides = {
            12: "TOTALE\nINCOMPETENZA DEGLI\nSVILUPPATORI?",
            15: "È UNA PERLA\nMETANARRATIVA.",
            22: "IL GIOCO\nFINALMENTE RESPIRA.",
            28: "BENVENUTA TRA GLI\nADULTI, MIKA.",
            30: "ALTRE STORIE DAI\nVIDEOGIOCHI\nSEGUIMI",
        }
        return overrides.get(cue.index, cue.text)

    def _load_gif(self, path: Path, resample: Image.Resampling) -> tuple[list[Image.Image], list[int], int]:
        if not path.is_file():
            raise FileNotFoundError(f"GIF mancante: {path}")
        source = Image.open(path)
        frames: list[Image.Image] = []
        durations: list[int] = []
        elapsed = 0
        target_size = (MEME_BOX[2] - MEME_BOX[0], MEME_BOX[3] - MEME_BOX[1])
        for source_frame in ImageSequence.Iterator(source):
            frame_image = fit_inside(source_frame.convert("RGB"), target_size, resample=resample)
            # Scanline leggera: la GIF resta leggibile ma vive dentro il layout.
            for y in range(0, frame_image.height, 4):
                strip = frame_image.crop((0, y, frame_image.width, min(y + 1, frame_image.height)))
                strip = ImageEnhance.Brightness(strip).enhance(0.78)
                frame_image.paste(strip, (0, y))
            duration = max(20, int(source_frame.info.get("duration", source.info.get("duration", 80))))
            elapsed += duration
            frames.append(frame_image)
            durations.append(elapsed)
        return frames, durations, elapsed

    def _ensure_footage_frames(self) -> None:
        source = RAW / "footage" / "extra-coin-official-footage.mp4"
        if not source.is_file():
            raise FileNotFoundError(f"Footage mancante: {source}")
        existing = list(self.footage_dir.glob("frame-*.jpg")) if self.footage_dir.is_dir() else []
        if len(existing) >= 300:
            return
        self.footage_dir.mkdir(parents=True, exist_ok=True)
        for old in existing:
            old.unlink()
        command = [
            str(self.ffmpeg), "-hide_banner", "-loglevel", "error", "-i", str(source),
            "-vf", f"fps={FOOTAGE_FPS},scale=1280:720:force_original_aspect_ratio=decrease,"
                   "pad=1280:720:(ow-iw)/2:(oh-ih)/2:black",
            "-q:v", "3", "-y", str(self.footage_dir / "frame-%04d.jpg"),
        ]
        subprocess.run(command, check=True)

    @functools.lru_cache(maxsize=72)
    def footage_media(self, index: int) -> Image.Image:
        index = max(0, min(index, len(self.footage_files) - 1))
        image = Image.open(self.footage_files[index]).convert("RGB")
        return fit_inside(image, (MEDIA_BOX[2] - MEDIA_BOX[0], MEDIA_BOX[3] - MEDIA_BOX[1]))

    def footage_at(self, seconds: float) -> Image.Image:
        return self.footage_media(int(max(0.0, seconds) * FOOTAGE_FPS))

    def cue_at(self, seconds: float) -> Cue:
        index = bisect.bisect_right(self.cue_starts, seconds) - 1
        return self.cues[max(0, min(index, len(self.cues) - 1))]

    def scene_at(self, seconds: float) -> int:
        return max(0, min(bisect.bisect_right(SCENE_STARTS, seconds) - 1, 11))

    def draw_ui(self, image: Image.Image, scene: int, seconds: float) -> None:
        draw = ImageDraw.Draw(image)
        accent = SCENE_ACCENTS[scene]
        label = f"RECENSIONE {scene + 1:02d} / 12 — EXTRA COIN"
        local = seconds - SCENE_STARTS[scene]
        count = min(len(label), int(max(0.0, local) * 30))
        tracking_text(draw, (70, 268), label, font(FONT_MONO, 26), accent, 2, count)
        draw.rectangle((70, 330, 70 + int(300 * min(1.0, max(0.0, local) * 4)), 338), fill=accent)
        draw.line((1006, 268, 938, 344), fill=accent, width=12)

    def draw_media(self, image: Image.Image, media: Image.Image, scene: int, *, footage_credit: bool = False) -> None:
        accent = SCENE_ACCENTS[scene]
        image.paste(media, (MEDIA_BOX[0], MEDIA_BOX[1]))
        draw = ImageDraw.Draw(image)
        draw.rectangle(MEDIA_BOX, outline=BONE, width=3)
        add_corner_marks(draw, MEDIA_BOX, accent)
        if footage_credit:
            label = "FOOTAGE: EXTRA COIN — CINIC GAMES"
            label_face = font(FONT_MONO, 21)
            width = int(draw.textlength(label, font=label_face)) + 28
            draw.rectangle((86, 856, 86 + width, 896), fill=INK)
            tracking_text(draw, (100, 864), label, label_face, BONE, 1)

    def draw_still(self, image: Image.Image, name: str, scene: int) -> None:
        self.draw_media(image, self.media_stills[name], scene)

    def draw_meme(self, image: Image.Image, which: str, seconds_into_cue: float, scene: int) -> None:
        frames, cumulative, total = self.gifs[which]
        millis = int(max(0.0, seconds_into_cue) * 1000) % max(1, total)
        frame_index = bisect.bisect_right(cumulative, millis)
        frame_index = min(frame_index, len(frames) - 1)
        image.paste(frames[frame_index], (MEME_BOX[0], MEME_BOX[1]))
        draw = ImageDraw.Draw(image)
        draw.rectangle(MEME_BOX, outline=BONE, width=4)
        add_corner_marks(draw, MEME_BOX, SCENE_ACCENTS[scene])

    def draw_triptych(self, image: Image.Image, scene: int) -> None:
        draw = ImageDraw.Draw(image)
        width, height, gap = 290, 163, 20
        x0, y0 = 70, 405
        for idx, name in enumerate(("palestra", "ron-cafe-01", "xy-street")):
            thumb = fit_inside(self.images[name], (width, height))
            x = x0 + idx * (width + gap)
            image.paste(thumb, (x, y0))
            draw.rectangle((x, y0, x + width, y0 + height), outline=BONE, width=2)
        add_corner_marks(draw, (x0, y0, x0 + 3 * width + 2 * gap, y0 + height), SCENE_ACCENTS[scene])

    def draw_visual(self, image: Image.Image, seconds: float, scene: int, cue: Cue) -> None:
        local = seconds - SCENE_STARTS[scene]
        if scene == 0:
            image.paste(self.hook)
            overlay = Image.new("RGB", (W, H), INK)
            image.paste(Image.blend(image, overlay, 0.52))
        elif scene == 1:
            self.draw_still(image, "casa-mika" if seconds < 6.0 else "stanza-mika", scene)
        elif scene == 2:
            if seconds >= 14.2:
                self.draw_meme(image, "a", seconds - 14.2, scene)
            elif seconds < 10.95:
                self.draw_media(image, self.footage_at(seconds - 10.0), scene)
            else:
                self.draw_still(image, "xy-street", scene)
        elif scene == 3:
            if seconds < 16.5:
                self.draw_still(image, "cinema-sala", scene)
            elif seconds < 17.15:
                self.draw_media(image, self.footage_at(12.4 + seconds - 16.5), scene)
            elif seconds < 18.0:
                self.draw_still(image, "palestra", scene)
            elif seconds < 18.7:
                self.draw_still(image, "ron-cafe-01", scene)
            elif seconds < 19.35:
                self.draw_media(image, self.footage_at(15.7 + seconds - 18.7), scene)
            elif seconds < 20.15:
                self.draw_still(image, "quiet-point", scene)
            else:
                self.draw_still(image, "xy-street", scene)
        elif scene == 4:
            self.draw_triptych(image, scene)
        elif scene == 5:
            if seconds >= 31.2:
                self.draw_meme(image, "b", seconds - 31.2, scene)
        elif scene == 6:
            if seconds < 33.2:
                self.draw_media(image, self.footage_at(6.4 + seconds - 32.0), scene, footage_credit=True)
            elif seconds < 34.0:
                pass
            elif seconds < 35.2:
                self.draw_media(image, self.footage_at(9.0 + seconds - 34.0), scene, footage_credit=True)
        elif scene == 7:
            if seconds < 39.7:
                self.draw_still(image, "ron-cafe-01", scene)
            elif seconds < 41.3:
                self.draw_still(image, "ron-cafe-02", scene)
            elif seconds < 42.7:
                self.draw_still(image, "quiet-point", scene)
            else:
                self.draw_media(image, self.footage_at(20.0 + seconds - 42.7), scene)
        elif scene == 8:
            self.draw_still(image, "sogno-mika", scene)
            ratio = min(0.88, max(0.0, local / 6.0) * 0.88)
            x0, y0, x1, y1 = MEDIA_BOX
            cover_width = int((x1 - x0) * ratio / 2)
            draw = ImageDraw.Draw(image)
            draw.rectangle((x0, y0, x0 + cover_width, y1), fill=INK)
            draw.rectangle((x1 - cover_width, y0, x1, y1), fill=INK)
        elif scene == 9:
            # Il fotogramma precedente sopravvive come una fessura che si chiude.
            self.draw_still(image, "sogno-mika", scene)
            ratio = 0.88 + min(0.11, local / 4.5 * 0.11)
            x0, y0, x1, y1 = MEDIA_BOX
            cover_width = int((x1 - x0) * ratio / 2)
            draw = ImageDraw.Draw(image)
            draw.rectangle((x0, y0, x0 + cover_width, y1), fill=INK)
            draw.rectangle((x1 - cover_width, y0, x1, y1), fill=INK)

    def text_position(self, scene: int, role: str) -> int:
        if role == "meme":
            return 1090
        if scene == 0:
            return 730 if role == "title" else 1160
        if scene in {4, 5, 9, 10, 11}:
            if scene == 9 and role == "closing":
                return 1050
            if role == "copy":
                return 1120
            if role == "response":
                return 810
            return 650
        if role == "copy":
            return 1190
        if role == "response":
            return 1090
        return 990

    def draw_cue(self, image: Image.Image, cue: Cue, seconds: float, scene: int) -> None:
        draw = ImageDraw.Draw(image)
        accent = SCENE_ACCENTS[scene]
        display_text = self.display_text(cue)
        lines = display_text.splitlines()
        y = self.text_position(scene, cue.role)

        if cue.role in {"copy", "closing"}:
            path, start, minimum, max_height = FONT_COPY_BOLD, 66, 48, 260
            fill = BONE
        elif cue.role == "meme":
            path, start, minimum, max_height = FONT_TITLE, 112, 76, 180
            fill = BONE
        elif cue.role == "response":
            path, start, minimum, max_height = FONT_TITLE, 176, 92, 300
            fill = accent
        elif cue.role in {"cta", "end"}:
            path, start, minimum, max_height = FONT_TITLE, 154, 76, 560
            fill = BONE
        else:
            path, start, minimum, max_height = FONT_TITLE, 154, 78, 460
            fill = BONE

        max_width = 830 if cue.role != "meme" else 760
        face, spacing = fit_face(path, lines, start, minimum, max_width, max_height)

        # Le cue da 0,8 s devono essere ferme dal primo frame.
        elapsed_frames = int(round((seconds - cue.start) * FPS))
        x = 70 if cue.role != "meme" else 160
        if cue.role in {"title", "cta", "end"} and cue.end - cue.start > 0.8:
            if elapsed_frames == 0:
                x -= 25
                face = font(path, max(minimum, int(face.size * 1.06)))
            elif elapsed_frames == 1:
                x -= 8
            elif elapsed_frames == 2:
                x += 3

        if scene == 5 and cue.index == 16 and 0 <= elapsed_frames < 3:
            # Piccola frattura di ASSOLUZIONE, poi il testo torna perfettamente fermo.
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            layer_draw = ImageDraw.Draw(layer)
            draw_block(layer_draw, (x, y), display_text, face, fill, spacing)
            split = y + 80
            image.paste(layer.crop((0, 0, W, split)).convert("RGB"), (10, 0), layer.crop((0, 0, W, split)).getchannel("A"))
            image.paste(layer.crop((0, split, W, H)).convert("RGB"), (-10, split), layer.crop((0, split, W, H)).getchannel("A"))
        else:
            draw_block(draw, (x, y), display_text, face, fill, spacing)

        width, height = text_metrics(lines, face, spacing)
        bar_y = min(1510, y + height + 28)
        draw.rectangle((x, bar_y, x + min(width, 420), bar_y + 10), fill=accent)

    def apply_glitch(self, image: Image.Image, frame_index: int) -> Image.Image:
        transition_frames = {int(round(end * FPS)) - 1 for end in SCENE_ENDS[:-1]}
        distance = min((abs(frame_index - pivot) for pivot in transition_frames), default=99)
        if distance > 2:
            return image
        amount = 10 - distance * 3
        red, green, blue = image.split()
        red = ImageChops.offset(red, amount, 0)
        blue = ImageChops.offset(blue, -amount, 0)
        result = Image.merge("RGB", (red, green, blue))
        draw = ImageDraw.Draw(result)
        y = 420 + ((frame_index * 97) % 880)
        draw.rectangle((0, y, W, y + 10 + amount), fill=SCENE_ACCENTS[self.scene_at(frame_index / FPS)])
        return result

    def render_frame(self, frame_index: int) -> Image.Image:
        seconds = frame_index / FPS
        scene = self.scene_at(seconds)
        cue = self.cue_at(seconds)
        if frame_index < 2:
            return Image.new("RGB", (W, H), BONE)
        image = Image.new("RGB", (W, H), INK)
        self.draw_visual(image, seconds, scene, cue)
        self.draw_ui(image, scene, seconds)
        self.draw_cue(image, cue, seconds, scene)
        return self.apply_glitch(image, frame_index)

    def preview(self, output: Path) -> None:
        times = [2.6, 7.5, 14.45, 19.6, 24.3, 28.2, 34.5, 42.85, 47.4, 52.7, 55.4, 58.5]
        output.mkdir(parents=True, exist_ok=True)
        thumbs: list[Image.Image] = []
        for scene, seconds in enumerate(times, 1):
            frame = self.render_frame(int(round(seconds * FPS)))
            frame.save(output / f"scene-{scene:02d}.png", optimize=True)
            thumbs.append(frame.resize((270, 480), Image.Resampling.LANCZOS))
        sheet = Image.new("RGB", (1080, 1440), INK)
        for index, thumb in enumerate(thumbs):
            sheet.paste(thumb, ((index % 4) * 270, (index // 4) * 480))
        sheet.save(output / "contact-sheet.jpg", quality=94)
        for name, seconds in (("meme-a", 14.45), ("assoluzione", 28.2), ("meme-b", 31.45)):
            self.render_frame(int(round(seconds * FPS))).save(output / f"detail-{name}.png", optimize=True)
        print(f"Anteprima: {output / 'contact-sheet.jpg'}", flush=True)

    def video(self, output: Path, *, preset: str = "veryfast", crf: int = 20) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        command = [
            str(self.ffmpeg), "-hide_banner", "-loglevel", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s:v", f"{W}x{H}",
            "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
            "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(output),
        ]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        assert process.stdin is not None
        try:
            for frame_index in range(TOTAL_FRAMES):
                process.stdin.write(self.render_frame(frame_index).tobytes())
                if frame_index % 150 == 0:
                    print(f"Render {frame_index / FPS:05.1f}s / 60.0s", flush=True)
        except BrokenPipeError as exc:
            raise RuntimeError("FFmpeg ha interrotto la codifica") from exc
        finally:
            process.stdin.close()
        return_code = process.wait()
        if return_code:
            raise RuntimeError(f"FFmpeg terminato con codice {return_code}")
        print(f"Video: {output}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render del reel Extra Coin")
    parser.add_argument("--preview", action="store_true", help="genera 12 frame e un contact sheet")
    parser.add_argument("--output", type=Path, default=DIST / "extra-coin-draft-01.mp4")
    parser.add_argument("--preset", default="veryfast", choices=("ultrafast", "veryfast", "faster", "fast", "medium"))
    parser.add_argument("--crf", type=int, default=20)
    args = parser.parse_args()

    ffmpeg = find_ffmpeg()
    print(f"FFmpeg: {ffmpeg}", flush=True)
    renderer = Renderer(ffmpeg)
    if args.preview:
        renderer.preview(CACHE / "preview")
    else:
        renderer.video(args.output, preset=args.preset, crf=args.crf)


if __name__ == "__main__":
    main()
