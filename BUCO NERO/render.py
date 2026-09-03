#!/usr/bin/env python3
"""Render del reel muto "Ghostty Blackhole".

Il renderer usa Pillow per comporre i frame e FFmpeg per decodificare gli asset
e codificare il master verticale. Cache e output rimangono fuori dalla cartella
editoriale.
"""

from __future__ import annotations

import argparse
import bisect
import functools
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont, ImageOps


PROJECT = Path(__file__).resolve().parent
REPO = PROJECT.parent
CACHE = REPO / ".cache" / "buco-nero"
DIST = REPO / "dist"

BLACKHOLE = PROJECT / "ghostty-blackhole.mp4"
QUICKSAND = PROJECT / "Sinking Days Of Our Lives GIF by Global Entertainment.gif"
CAT = PROJECT / "Suspicious Black Cat GIF.gif"
PORTRAIT = PROJECT / "davide-fumetto-trasparente.png"
CRITICAL_INVENTORY = PROJECT / "Adesivo editoriale Critical Inventory.png"

W, H = 1080, 1920
FPS = 30
DURATION = 55.0

INK = (11, 11, 13)
BONE = (242, 239, 233)
ACID = (166, 255, 0)
NERV = (255, 77, 0)
ASH = (74, 74, 80)
MUTED = (166, 164, 160)

FONT_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
FONT_TITLE = FONT_DIR / "BOD_CB.TTF"
FONT_BODY = FONT_DIR / "seguisb.ttf"
FONT_BODY_BOLD = FONT_DIR / "segoeuib.ttf"
FONT_MONO = FONT_DIR / "consolab.ttf"

SAFE_LEFT, SAFE_RIGHT = 70, 1010
MEDIA_BOX = (70, 405, 1010, 1113)
TEXT_Y = 1200
PROGRESS_Y = 1570


@dataclass(frozen=True)
class Scene:
    index: int
    start: float
    end: float
    text: tuple[str, ...]
    mode: str
    accent_line: int | None = None


SCENES = (
    Scene(1, 0.0, 3.5, ("UN DEVELOPER DIMENTICAVA", "SEMPRE DI FARE PAUSA."), "title"),
    Scene(2, 3.5, 7.0, ("LA SOLUZIONE?", "UN BUCO NERO", "NEL TERMINALE."), "title", 1),
    Scene(3, 7.0, 9.0, ("NO, SUL SERIO.",), "small-title"),
    Scene(4, 9.0, 13.0, ("Ghostty Blackhole è uno shader", "ray-traced per Ghostty."), "media"),
    Scene(5, 13.0, 17.5, ("In modalità Pomodoro parte", "da una piccola singolarità."), "media"),
    Scene(6, 17.5, 22.0, ("Poi cresce per 55 minuti", "e deforma davvero il testo."), "media", 1),
    Scene(7, 22.0, 26.0, ("IL TERMINALE TI STA DICENDO:", "«FRATELLO, ALZATI.»"), "reaction", 1),
    Scene(8, 26.0, 31.0, ("Se smetti di digitare,", "il buco nero si rimpicciolisce."), "media"),
    Scene(9, 31.0, 35.5, ("Se continui a lavorare, resta lì.", "A fissarti."), "reaction"),
    Scene(10, 35.5, 40.0, ("Può anche crescere insieme", "alla context window di Claude Code."), "media", 1),
    Scene(11, 40.0, 43.5, ("È OPEN SOURCE.", "SI CHIAMA", "GHOSTTY BLACKHOLE."), "repo", 2),
    Scene(12, 43.5, 48.0, ("PERCHÉ USARE UN TIMER,", "QUANDO PUOI PIEGARE", "LO SPAZIO-TEMPO?"), "final", 2),
    Scene(13, 48.0, 55.0, ("Giornalismo e codice:", "full-stack writer.", "Curo la newsletter Critical Inventory,", "per chi scrive e sviluppa.", "Iscriviti al link in bio"), "about"),
)


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def ease_out(value: float) -> float:
    value = clamp01(value)
    return 1.0 - (1.0 - value) ** 3


@functools.lru_cache(maxsize=128)
def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.is_file():
        raise FileNotFoundError(f"Font mancante: {path}")
    return ImageFont.truetype(str(path), size)


def find_ffmpeg() -> Path:
    configured = os.environ.get("FFMPEG_BINARY")
    if configured and Path(configured).is_file():
        return Path(configured)
    found = shutil.which("ffmpeg")
    if found:
        return Path(found)
    candidates = (
        REPO / ".cache" / "render-deps-local" / "imageio_ffmpeg" / "binaries",
        REPO / ".cache" / "render-deps-local" / "imageio_ffmpeg" / "binaries",
    )
    for directory in candidates:
        if directory.is_dir():
            binaries = list(directory.glob("ffmpeg*.exe"))
            if binaries:
                return binaries[0]
    raise RuntimeError("FFmpeg non trovato")


def fit_cover(image: Image.Image, size: tuple[int, int], centering=(0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, Image.Resampling.LANCZOS, centering=centering)


def tracking_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    face: ImageFont.FreeTypeFont,
    fill: tuple[int, ...],
    tracking: int = 2,
) -> None:
    x, y = xy
    for char in value:
        draw.text((x, y), char, font=face, fill=fill)
        x += int(draw.textlength(char, font=face)) + tracking


def fit_face(
    path: Path,
    lines: tuple[str, ...],
    start: int,
    minimum: int,
    max_width: int,
) -> ImageFont.FreeTypeFont:
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    for size in range(start, minimum - 1, -2):
        face = font(path, size)
        if max((probe.textlength(line, font=face) for line in lines), default=0) <= max_width:
            return face
    return font(path, minimum)


class FrameSource:
    def __init__(self, directory: Path, fps: int) -> None:
        self.directory = directory
        self.fps = fps
        self.files = sorted(directory.glob("frame-*.jpg"))
        if not self.files:
            raise RuntimeError(f"Nessun frame in {directory}")

    @functools.lru_cache(maxsize=180)
    def frame(self, seconds: float) -> Image.Image:
        index = int(max(0.0, seconds) * self.fps) % len(self.files)
        with Image.open(self.files[index]) as source:
            return source.convert("RGB")


class Renderer:
    def __init__(self, ffmpeg: Path) -> None:
        self.ffmpeg = ffmpeg
        self._validate()
        self._extract_sources()
        self.blackhole = FrameSource(CACHE / "blackhole-10fps", 10)
        self.quicksand = FrameSource(CACHE / "quicksand-10fps", 10)
        self.cat = FrameSource(CACHE / "cat-15fps", 15)
        self.starts = [scene.start for scene in SCENES]
        self.total_frames = int(DURATION * FPS)

    def _validate(self) -> None:
        missing = [path for path in (BLACKHOLE, QUICKSAND, CAT, PORTRAIT, CRITICAL_INVENTORY) if not path.is_file()]
        if missing:
            raise FileNotFoundError("Asset mancanti: " + ", ".join(map(str, missing)))
        for previous, current in zip(SCENES, SCENES[1:]):
            if abs(previous.end - current.start) > 0.001:
                raise RuntimeError("Timeline non contigua")

    def _extract(self, source: Path, destination: Path, fps: int) -> None:
        expected = int((20 if source == BLACKHOLE else 6) * fps)
        existing = list(destination.glob("frame-*.jpg")) if destination.is_dir() else []
        if len(existing) >= expected:
            return
        destination.mkdir(parents=True, exist_ok=True)
        for old in existing:
            old.unlink()
        command = [
            str(self.ffmpeg), "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(source), "-vf", f"fps={fps}", "-q:v", "2",
            str(destination / "frame-%04d.jpg"),
        ]
        subprocess.run(command, check=True)

    def _extract_sources(self) -> None:
        self._extract(BLACKHOLE, CACHE / "blackhole-10fps", 10)
        self._extract(QUICKSAND, CACHE / "quicksand-10fps", 10)
        self._extract(CAT, CACHE / "cat-15fps", 15)

    def scene_at(self, seconds: float) -> Scene:
        index = bisect.bisect_right(self.starts, seconds) - 1
        return SCENES[max(0, min(index, len(SCENES) - 1))]

    @staticmethod
    def media_time(scene: Scene, local: float) -> float:
        duration = scene.end - scene.start
        progress = clamp01(local / duration)
        if scene.index == 3:
            return 0.2 + progress * 1.6
        if scene.index == 4:
            return 0.5 + progress * 3.5
        if scene.index == 5:
            return 0.2 + progress * 5.0
        if scene.index == 6:
            return 2.0 + progress * 18.3
        if scene.index == 8:
            return 14.5 * (1.0 - progress) + 0.5
        if scene.index == 9:
            return 17.8 + progress * 2.5
        if scene.index == 10:
            return 0.2 + progress * 20.2
        return progress * 20.0

    @staticmethod
    def add_scanlines(image: Image.Image, strength: float = 0.12) -> Image.Image:
        result = image.copy()
        draw = ImageDraw.Draw(result, "RGBA")
        alpha = int(255 * strength)
        for y in range(0, result.height, 5):
            draw.line((0, y, result.width, y), fill=(0, 0, 0, alpha), width=1)
        return result

    def draw_header(self, image: Image.Image, scene: Scene) -> None:
        draw = ImageDraw.Draw(image)
        label = f"TOOL / GHOSTTY BLACKHOLE · {scene.index:02d}/13"
        tracking_text(draw, (SAFE_LEFT, 258), label, font(FONT_MONO, 25), ACID, 1)
        draw.rectangle((SAFE_LEFT, 324, SAFE_LEFT + 260, 332), fill=ACID)
        draw.line((1005, 258, 950, 330), fill=ACID, width=10)

    def draw_progress(self, image: Image.Image, scene: Scene) -> None:
        draw = ImageDraw.Draw(image)
        draw.rectangle((SAFE_LEFT, PROGRESS_Y, SAFE_RIGHT, PROGRESS_Y + 5), fill=ASH)
        width = int((SAFE_RIGHT - SAFE_LEFT) * scene.index / len(SCENES))
        draw.rectangle((SAFE_LEFT, PROGRESS_Y, SAFE_LEFT + width, PROGRESS_Y + 5), fill=ACID)

    def draw_media_frame(self, image: Image.Image, source: Image.Image, *, credit=True) -> None:
        width = MEDIA_BOX[2] - MEDIA_BOX[0]
        height = MEDIA_BOX[3] - MEDIA_BOX[1]
        media = self.add_scanlines(fit_cover(source, (width, height)))
        image.paste(media, (MEDIA_BOX[0], MEDIA_BOX[1]))
        draw = ImageDraw.Draw(image)
        draw.rectangle(MEDIA_BOX, outline=BONE, width=3)
        length = 38
        for x, y, dx, dy in (
            (MEDIA_BOX[0], MEDIA_BOX[1], 1, 1), (MEDIA_BOX[2], MEDIA_BOX[1], -1, 1),
            (MEDIA_BOX[0], MEDIA_BOX[3], 1, -1), (MEDIA_BOX[2], MEDIA_BOX[3], -1, -1),
        ):
            draw.line((x, y, x + dx * length, y), fill=ACID, width=6)
            draw.line((x, y, x, y + dy * length), fill=ACID, width=6)
        if credit:
            label = "FOOTAGE: S0XDK / GHOSTTY-BLACKHOLE"
            face = font(FONT_MONO, 19)
            label_width = int(draw.textlength(label, font=face)) + 28
            y = MEDIA_BOX[3] - 50
            draw.rectangle((MEDIA_BOX[0] + 14, y, MEDIA_BOX[0] + 14 + label_width, y + 36), fill=INK)
            tracking_text(draw, (MEDIA_BOX[0] + 28, y + 6), label, face, BONE, 1)

    def draw_body(self, image: Image.Image, scene: Scene, seconds: float) -> None:
        local = seconds - scene.start
        duration = scene.end - scene.start
        enter = ease_out(local / (8 / FPS))
        exit_alpha = 1.0 - clamp01((local - (duration - 6 / FPS)) / (6 / FPS))
        alpha = int(255 * min(enter, exit_alpha))
        offset = int((1.0 - enter) * 24)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        face = fit_face(FONT_BODY, scene.text, 68, 52, SAFE_RIGHT - SAFE_LEFT)
        line_height = max(1, face.getbbox("Ag")[3] - face.getbbox("Ag")[1])
        spacing = 18
        for line_index, line in enumerate(scene.text):
            fill = ACID if scene.accent_line == line_index else BONE
            draw.text(
                (SAFE_LEFT, TEXT_Y + line_index * (line_height + spacing) + offset),
                line,
                font=face,
                fill=fill + (alpha,),
            )
        image.paste(overlay, (0, 0), overlay)

    def draw_title(self, image: Image.Image, scene: Scene, seconds: float) -> None:
        local = seconds - scene.start
        duration = scene.end - scene.start
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        face = fit_face(FONT_TITLE, scene.text, 150 if scene.index != 1 else 128, 74, 940)
        line_height = max(1, face.getbbox("Ag")[3] - face.getbbox("Ag")[1])
        spacing = max(10, int(face.size * 0.08))
        total = len(scene.text) * line_height + (len(scene.text) - 1) * spacing
        y0 = 650 if scene.index != 1 else 700
        for line_index, line in enumerate(scene.text):
            delay = line_index * 2 / FPS
            enter = ease_out((local - delay) / (6 / FPS))
            exit_alpha = 1.0 - clamp01((local - (duration - 6 / FPS)) / (6 / FPS))
            alpha = int(255 * max(0.0, min(enter, exit_alpha)))
            offset = int((1.0 - enter) * 36)
            fill = ACID if scene.accent_line == line_index else BONE
            draw.text((SAFE_LEFT, y0 + line_index * (line_height + spacing) + offset), line, font=face, fill=fill + (alpha,))
        bar = int(300 * ease_out((local - 0.25) / 0.25))
        if bar > 0:
            draw.rectangle((SAFE_LEFT, y0 + total + 58, SAFE_LEFT + bar, y0 + total + 70), fill=ACID + (255,))
        tracking_text(draw, (SAFE_LEFT, 310), f"GHOSTTY BLACKHOLE · {scene.index:02d}/13", font(FONT_MONO, 24), ACID + (255,), 1)
        image.paste(overlay, (0, 0), overlay)

    def draw_small_title(self, image: Image.Image, scene: Scene, seconds: float) -> None:
        source = self.blackhole.frame(self.media_time(scene, seconds - scene.start))
        width, height = 940, 708
        media = fit_cover(source, (width, height))
        image.paste(media, (70, 600))
        shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        shade_draw = ImageDraw.Draw(shade)
        shade_draw.rectangle((0, 0, W, H), fill=(11, 11, 13, 70))
        image.paste(shade, (0, 0), shade)
        draw = ImageDraw.Draw(image)
        face = font(FONT_TITLE, 158)
        draw.text((SAFE_LEFT, 760), scene.text[0], font=face, fill=BONE)
        draw.rectangle((SAFE_LEFT, 965, SAFE_LEFT + 290, 979), fill=ACID)

    def draw_reaction(self, image: Image.Image, scene: Scene, seconds: float) -> None:
        local = seconds - scene.start
        if scene.index == 7:
            gif_start = 2.8
            if local >= gif_start:
                source = self.quicksand.frame(local - gif_start + 1.3)
                box = (160, 820, 920, 1422)
                media = self.add_scanlines(fit_cover(source, (box[2] - box[0], box[3] - box[1])))
                image.paste(media, (box[0], box[1]))
                draw = ImageDraw.Draw(image)
                draw.rectangle(box, outline=BONE, width=3)
                draw.rectangle((box[0], box[1], box[0] + 160, box[1] + 8), fill=NERV)
            text_y = 500
        else:
            gif_start = 3.4
            if local < gif_start:
                source = self.blackhole.frame(self.media_time(scene, local))
                self.draw_media_frame(image, source)
            else:
                source = self.cat.frame(local - gif_start + 0.8)
                box = (255, 710, 825, 1420)
                media = self.add_scanlines(fit_cover(source, (box[2] - box[0], box[3] - box[1]), (0.5, 0.35)))
                image.paste(media, (box[0], box[1]))
                draw = ImageDraw.Draw(image)
                draw.rectangle(box, outline=BONE, width=3)
                draw.rectangle((box[0], box[1], box[0] + 160, box[1] + 8), fill=ACID)
            text_y = 1190 if local < gif_start else 450

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        face = fit_face(FONT_BODY_BOLD, scene.text, 74, 54, 940)
        line_height = max(1, face.getbbox("Ag")[3] - face.getbbox("Ag")[1])
        enter = ease_out(local / (7 / FPS))
        alpha = int(255 * enter)
        for index, line in enumerate(scene.text):
            fill = NERV if scene.index == 7 and index == 1 else BONE
            draw.text((SAFE_LEFT, text_y + index * (line_height + 18)), line, font=face, fill=fill + (alpha,))
        image.paste(overlay, (0, 0), overlay)

    def draw_context(self, image: Image.Image, scene: Scene, seconds: float) -> None:
        local = seconds - scene.start
        duration = scene.end - scene.start
        progress = clamp01(local / duration)
        source = self.blackhole.frame(self.media_time(scene, local))
        self.draw_media_frame(image, source)
        draw = ImageDraw.Draw(image)
        x0, x1, y = 110, 970, 1080
        draw.rectangle((x0, y, x1, y + 12), fill=ASH)
        draw.rectangle((x0, y, x0 + int((x1 - x0) * progress), y + 12), fill=ACID)
        label = f"CONTEXT {int(12 + progress * 88):03d}%"
        tracking_text(draw, (x0, y - 42), label, font(FONT_MONO, 23), ACID, 1)

    def draw_repo(self, image: Image.Image, scene: Scene, seconds: float) -> None:
        local = seconds - scene.start
        draw = ImageDraw.Draw(image)
        tracking_text(draw, (SAFE_LEFT, 300), "GITHUB / S0XDK", font(FONT_MONO, 26), ACID, 1)
        draw.rectangle((SAFE_LEFT, 370, SAFE_RIGHT, 376), fill=ASH)
        face = fit_face(FONT_TITLE, scene.text, 132, 74, 940)
        line_height = max(1, face.getbbox("Ag")[3] - face.getbbox("Ag")[1])
        y0 = 590
        for index, line in enumerate(scene.text):
            enter = ease_out((local - index * 0.08) / 0.22)
            fill = ACID if index == 2 else BONE
            draw.text((SAFE_LEFT, y0 + index * (line_height + 12) + int((1 - enter) * 24)), line, font=face, fill=fill)
        draw.rectangle((SAFE_LEFT, 1260, SAFE_RIGHT, 1360), outline=BONE, width=3)
        tracking_text(draw, (SAFE_LEFT + 28, 1290), "github.com/s0xDk/ghostty-blackhole", font(FONT_MONO, 23), BONE, 1)

    def draw_final(self, image: Image.Image, scene: Scene, seconds: float) -> None:
        local = seconds - scene.start
        draw = ImageDraw.Draw(image)
        tracking_text(draw, (SAFE_LEFT, 320), "OVERENGINEERING / LIVELLO COSMICO", font(FONT_MONO, 24), ACID, 1)
        face = fit_face(FONT_TITLE, scene.text, 145, 78, 940)
        line_height = max(1, face.getbbox("Ag")[3] - face.getbbox("Ag")[1])
        y0 = 590
        for index, line in enumerate(scene.text):
            enter = ease_out((local - index * 0.08) / 0.24)
            fill = ACID if index == 2 else BONE
            draw.text((SAFE_LEFT, y0 + index * (line_height + 14) + int((1 - enter) * 30)), line, font=face, fill=fill)
        draw.rectangle((SAFE_LEFT, 1325, SAFE_LEFT + 290, 1338), fill=NERV)
        tracking_text(draw, (SAFE_LEFT, 1380), "LINK IN CAPTION", font(FONT_MONO, 25), BONE, 2)

    @staticmethod
    def transparent_line_art(source: Image.Image) -> Image.Image:
        line_art = source.convert("RGBA")
        grayscale = ImageOps.grayscale(line_art)
        line_art.putalpha(ImageOps.invert(grayscale))
        return line_art

    @staticmethod
    def remove_checkerboard(source: Image.Image) -> Image.Image:
        logo = source.convert("RGBA")
        pixels = logo.load()
        for y in range(logo.height):
            for x in range(logo.width):
                red, green, blue, alpha = pixels[x, y]
                if alpha and max(red, green, blue) - min(red, green, blue) < 10 and min(red, green, blue) > 215:
                    pixels[x, y] = (red, green, blue, 0)
        return logo

    def draw_about(self, image: Image.Image, scene: Scene, seconds: float) -> None:
        local = seconds - scene.start
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        with Image.open(CRITICAL_INVENTORY) as source:
            logo = self.remove_checkerboard(source)
        logo.thumbnail((700, 440), Image.Resampling.LANCZOS)
        logo_x = SAFE_LEFT
        logo_y = 165
        overlay.alpha_composite(logo, (logo_x, logo_y))

        with Image.open(PORTRAIT) as source:
            portrait = source.convert("RGBA")
        portrait.thumbnail((500, 700), Image.Resampling.LANCZOS)
        portrait_x = 570
        portrait_y = 640
        overlay.alpha_composite(portrait, (portrait_x, portrait_y))

        fade = ease_out(local / 0.28)
        body_face = fit_face(FONT_BODY_BOLD, scene.text[:2], 66, 52, 500)
        line_height = body_face.getbbox("Ag")[3] - body_face.getbbox("Ag")[1]
        draw.text((SAFE_LEFT, 730), scene.text[0], font=body_face, fill=BONE + (int(255 * fade),))
        draw.text((SAFE_LEFT, 730 + line_height + 16), scene.text[1], font=body_face, fill=ACID + (int(255 * fade),))

        detail_face = fit_face(FONT_BODY, scene.text[2:4], 42, 34, 500)
        detail_height = detail_face.getbbox("Ag")[3] - detail_face.getbbox("Ag")[1]
        for index, line in enumerate(scene.text[2:4]):
            draw.text((SAFE_LEFT, 1000 + index * (detail_height + 14)), line, font=detail_face, fill=BONE + (int(255 * fade),))

        draw.rectangle((SAFE_LEFT, 1320, SAFE_LEFT + 220, 1329), fill=NERV + (int(255 * fade),))
        cta_face = font(FONT_MONO, 25)
        tracking_text(draw, (SAFE_LEFT, 1380), scene.text[4].upper(), cta_face, ACID + (int(255 * fade),), 1)
        tracking_text(draw, (SAFE_LEFT, 1530), "CRITICALINVENTORY.IT", font(FONT_MONO, 21), MUTED + (int(255 * fade),), 1)
        image.paste(overlay, (0, 0), overlay)

        # RGB split only at the card entrance, then two restrained scan bars.
        if 0.18 <= local <= 0.42 or 3.6 <= local <= 3.72:
            offset = 8 if local < 1 else 4
            red, green, blue = image.split()
            shifted = Image.merge("RGB", (ImageChops.offset(red, offset, 0), green, ImageChops.offset(blue, -offset, 0)))
            bar_y = 760 if local < 1 else 1260
            image.paste(shifted.crop((0, bar_y, W, bar_y + 7)), (0, bar_y))

    def apply_glitch(self, image: Image.Image, frame_index: int) -> Image.Image:
        boundaries = [int(scene.start * FPS) for scene in SCENES[1:]]
        active = [boundary - frame_index for boundary in boundaries if 1 <= boundary - frame_index <= 2]
        if not active:
            return image
        amount = 7 if min(active) == 1 else 4
        red, green, blue = image.split()
        result = Image.merge("RGB", (ImageChops.offset(red, amount, 0), green, ImageChops.offset(blue, -amount, 0)))
        draw = ImageDraw.Draw(result)
        y = 380 + (frame_index * 71) % 920
        draw.rectangle((SAFE_LEFT, y, SAFE_RIGHT, y + 8), fill=NERV)
        return result

    def render_frame(self, frame_index: int) -> Image.Image:
        seconds = min(frame_index / FPS, DURATION - 1 / FPS)
        scene = self.scene_at(seconds)
        local = seconds - scene.start
        image = Image.new("RGB", (W, H), INK)

        if scene.mode == "title":
            self.draw_title(image, scene, seconds)
        elif scene.mode == "small-title":
            self.draw_small_title(image, scene, seconds)
        elif scene.mode == "reaction":
            self.draw_header(image, scene)
            self.draw_reaction(image, scene, seconds)
            self.draw_progress(image, scene)
        elif scene.mode == "repo":
            self.draw_repo(image, scene, seconds)
        elif scene.mode == "final":
            self.draw_final(image, scene, seconds)
        elif scene.mode == "about":
            self.draw_about(image, scene, seconds)
        else:
            self.draw_header(image, scene)
            if scene.index == 10:
                self.draw_context(image, scene, seconds)
            else:
                source = self.blackhole.frame(self.media_time(scene, local))
                self.draw_media_frame(image, source)
            self.draw_body(image, scene, seconds)
            self.draw_progress(image, scene)

        return self.apply_glitch(image, frame_index)

    def preview(self, output: Path) -> None:
        output.mkdir(parents=True, exist_ok=True)
        samples = (1.7, 5.2, 8.1, 11.0, 15.4, 20.8, 25.3, 29.0, 35.0, 38.6, 42.0, 46.0, 51.0)
        thumbs: list[Image.Image] = []
        for index, seconds in enumerate(samples, 1):
            frame = self.render_frame(int(seconds * FPS))
            frame.save(output / f"scene-{index:02d}.png", optimize=True)
            thumbs.append(frame.resize((270, 480), Image.Resampling.LANCZOS))
        sheet = Image.new("RGB", (1080, 1440), INK)
        for index, thumb in enumerate(thumbs):
            sheet.paste(thumb, ((index % 4) * 270, (index // 4) * 480))
        sheet.save(output / "contact-sheet.jpg", quality=94, subsampling=0)
        print(output / "contact-sheet.jpg", flush=True)

    def render_video(self, output: Path, preset: str, crf: int) -> None:
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
            for frame_index in range(self.total_frames):
                process.stdin.write(self.render_frame(frame_index).tobytes())
                if frame_index % (FPS * 5) == 0:
                    print(f"Render {frame_index / FPS:04.0f}s / {DURATION:.0f}s", flush=True)
        finally:
            process.stdin.close()
        if process.wait():
            raise RuntimeError("FFmpeg ha interrotto la codifica")
        print(output, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render BUCO NERO")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--preset", default="veryfast", choices=("ultrafast", "veryfast", "faster", "fast", "medium"))
    parser.add_argument("--crf", type=int, default=19)
    args = parser.parse_args()

    renderer = Renderer(find_ffmpeg())
    if args.preview:
        renderer.preview(CACHE / "preview")
    else:
        renderer.render_video(args.output or DIST / "buco-nero-draft-01.mp4", args.preset, args.crf)


if __name__ == "__main__":
    main()
