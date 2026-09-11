#!/usr/bin/env python3
"""Renderer del paper edit v0.5 di Extra Coin.

Il testo e i timing arrivano dalla traccia SRT corrente. Il renderer produce
un master verticale muto e tiene cache, anteprime e output separati dal draft
legacy generato da ``render.py``.
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
REPO = PROJECT.parent.parent if PROJECT.parent.name.lower() == "reels" else PROJECT
ASSETS = PROJECT / "assets"
SHOTS = ASSETS / "screenshots"
RAW = ASSETS / "raw"
CONTENT = PROJECT / "content"
CURRENT_SRT = CONTENT / "text-track.srt"
PAPER_EDIT_FILES = (
    CONTENT / "storyboard.md",
    CONTENT / "on-screen-copy.md",
    CONTENT / "template-discorsivo.md",
    CURRENT_SRT,
)
CACHE = REPO / ".cache" / "extra-coin-draft-v05"
DIST = PROJECT / "dist"

W, H = 1080, 1920
FPS = 30
FOOTAGE_FPS = 15
TARGET_DURATION = 52.0

INK = (11, 11, 13)
BONE = (242, 239, 233)
ACID = (166, 255, 0)
EVA = (91, 62, 150)
NERV = (255, 77, 0)
ASH = (74, 74, 80)
MUTED = (166, 164, 160)
MOTION_EVA = (177, 139, 255)
MOTION_ASH = (174, 174, 184)

FONT_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
FONT_TITLE = FONT_DIR / "BOD_CB.TTF"
FONT_COPY = FONT_DIR / "seguisb.ttf"
FONT_COPY_BOLD = FONT_DIR / "segoeuib.ttf"
FONT_MONO = FONT_DIR / "consolab.ttf"

# Area prudente rispetto all'interfaccia di Instagram, allineata al template
# approvato. La finestra mantiene il rapporto 16:9, mentre il testo vive
# sempre al di sotto e non finisce sotto i comandi laterali del Reel.
SAFE_LEFT, SAFE_RIGHT = 70, 910
MEDIA_BOX = (SAFE_LEFT, 390, SAFE_RIGHT, 863)
MEME_BOX = MEDIA_BOX
TEXT_Y = 1080
PROGRESS_Y = 1548

SCENE_ACCENTS = (
    NERV, NERV, ACID, EVA, NERV,
    NERV, NERV, ACID, EVA, ACID,
    EVA, EVA, ASH, ACID, NERV,
)
SECTION_LABELS = (
    "SCHEDA IDENTITÀ", "IL PUNTO DI PARTENZA", "CHE GIOCO È",
    "MIKA", "IL BUON LOOP", "IL PROBLEMA", "LA DOMANDA",
    "IL RIBALTAMENTO", "INTENZIONE ≠ ASSOLUZIONE", "FUORI DAL LOOP",
    "LA SCRITTURA", "DIVENTARE ADULTI", "CIÒ CHE RESTA",
    "IL VERDETTO", "LA DOMANDA FINALE",
)


@dataclass(frozen=True)
class Cue:
    index: int
    start: float
    end: float
    text: str


def parse_timecode(value: str) -> float:
    hours, minutes, rest = value.split(":")
    seconds, millis = rest.split(",")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def ease_out_cubic(value: float) -> float:
    value = clamp01(value)
    return 1.0 - (1.0 - value) ** 3


def smoothstep(value: float) -> float:
    value = clamp01(value)
    return value * value * (3.0 - 2.0 * value)


def mix_color(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
    amount: float,
) -> tuple[int, int, int]:
    amount = clamp01(amount)
    return tuple(
        int(round(first[channel] + (second[channel] - first[channel]) * amount))
        for channel in range(3)
    )


DISPLAY_TEXT = {
    2: "Extra Coin mi ha annoiato.\nForse voleva proprio farlo.",
    3: "È un'avventura narrativa ambientata\nin The Arcade, un metaverso che\npromette una vita migliore.",
    4: "Mika entra lì per ritrovare\ni genitori che l'hanno\nabbandonata.",
    5: "Per avanzare seguo il «buon Loop»:\nminigiochi, padel e pochi\npotenziamenti, ogni giorno.",
    6: "Poi tutto si ripete.\nLa progressione si ferma\ne il gioco sembra costruito male.",
    7: "TOTALE INCOMPETENZA\nDEGLI SVILUPPATORI?",
    8: "Quando Mika disobbedisce,\ncapisco il trucco: quella gabbia\nera diventata anche la mia.",
    9: "È una piccola perla metanarrativa.\nMa non è un'assoluzione:\nuna noia voluta resta comunque noia.",
    10: "Il gioco si sveglia quando\nrompo il Loop: arrivano ribellione,\nboss, amicizie e scelte.",
    11: "La scrittura approfondisce\ni personaggi e il gioco ci mette\ndavanti a scelte morali.",
    12: "Il tema è che diventare adulti\nsignifica scoprire che anche i genitori\npossono sbagliare e arrendersi.",
    13: "Ma qualunque scelta faccia Mika,\nqualcosa resta irrisolto.\nPer sempre.",
    14: "UN'IDEA BRILLANTE.\nDENTRO UN GIOCO\nTROPPO POVERO.",
    15: "QUANTA NOIA SEI DISPOSTO\nA PERDONARE IN UN VIDEOGAME?",
}

QUESTION_RESPONSE = "È la domanda inevitabile.\nMa la risposta è: non proprio."

HIGHLIGHTS = {
    2: "annoiato.",
    3: "The Arcade,",
    4: "genitori",
    5: "«buon Loop»:",
    6: "si ripete.",
    8: "gabbia",
    9: "non è un'assoluzione:",
    10: "rompo il Loop:",
    11: "scelte morali.",
    12: "anche i genitori",
    13: "irrisolto.",
}


def read_cues() -> list[Cue]:
    blocks = re.split(r"\r?\n\s*\r?\n", CURRENT_SRT.read_text(encoding="utf-8").strip())
    cues: list[Cue] = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        start_raw, end_raw = [part.strip() for part in lines[1].split("-->")]
        cues.append(
            Cue(
                index=int(lines[0]),
                start=parse_timecode(start_raw),
                end=parse_timecode(end_raw),
                text="\n".join(lines[2:]),
            )
        )

    if len(cues) != 15 or [cue.index for cue in cues] != list(range(1, 16)):
        raise RuntimeError(f"Attese 15 cue numerate 1–15, trovate {len(cues)} in {CURRENT_SRT}")
    if abs(cues[0].start) > 0.001 or abs(cues[-1].end - TARGET_DURATION) > 0.001:
        raise RuntimeError("La traccia v0.5 deve coprire esattamente 00:00–00:52")
    for previous, current in zip(cues, cues[1:]):
        if abs(previous.end - current.start) > 0.001:
            raise RuntimeError(f"Vuoto o sovrapposizione fra cue {previous.index} e {current.index}")

    # Gli a capo grafici possono cambiare, le parole no.
    for cue in cues[1:]:
        display = DISPLAY_TEXT[cue.index]
        if cue.index == 7:
            display += "\n" + QUESTION_RESPONSE
        if normalize_text(display) != normalize_text(cue.text):
            raise RuntimeError(f"Il copy grafico della cue {cue.index} diverge dalla traccia SRT")
    return cues


def validate_paper_edit() -> None:
    missing = [path for path in PAPER_EDIT_FILES if not path.is_file()]
    if missing:
        raise FileNotFoundError("File del paper edit mancanti: " + ", ".join(map(str, missing)))
    storyboard = (CONTENT / "storyboard.md").read_text(encoding="utf-8")
    copy = (CONTENT / "on-screen-copy.md").read_text(encoding="utf-8")
    template = (CONTENT / "template-discorsivo.md").read_text(encoding="utf-8")
    if "Extra Coin v0.5" not in storyboard or "**Durata:** 52 secondi" not in storyboard:
        raise RuntimeError("storyboard.md non descrive il paper edit v0.5 da 52 secondi")
    if "Extra Coin v0.5" not in copy or "15/15" not in copy:
        raise RuntimeError("on-screen-copy.md non contiene le 15 schede v0.5")
    if "15 stati testuali" not in template:
        raise RuntimeError("template-discorsivo.md non contiene la griglia approvata a 15 stati")


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


@functools.lru_cache(maxsize=96)
def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.is_file():
        raise FileNotFoundError(f"Font non trovato: {path}")
    return ImageFont.truetype(str(path), size)


def cover(image: Image.Image, size: tuple[int, int], *, centering: tuple[float, float] = (0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, Image.Resampling.LANCZOS, centering=centering)


def fit_inside(
    image: Image.Image,
    size: tuple[int, int],
    *,
    resample: Image.Resampling = Image.Resampling.LANCZOS,
) -> Image.Image:
    source = image.convert("RGB")
    ratio = min(size[0] / source.width, size[1] / source.height)
    result = source.resize(
        (max(1, int(round(source.width * ratio))), max(1, int(round(source.height * ratio)))),
        resample,
    )
    canvas = Image.new("RGB", size, INK)
    canvas.paste(result, ((size[0] - result.width) // 2, (size[1] - result.height) // 2))
    return canvas


def text_metrics(lines: list[str], face: ImageFont.FreeTypeFont, spacing: int) -> tuple[int, int]:
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    widths = [int(probe.textlength(line, font=face)) for line in lines]
    box = face.getbbox("Ag")
    line_height = max(1, box[3] - box[1])
    return max(widths, default=0), line_height * len(lines) + spacing * max(0, len(lines) - 1)


def fit_face(
    path: Path,
    lines: list[str],
    start: int,
    minimum: int,
    max_width: int,
    max_height: int,
    spacing_ratio: float = 0.18,
) -> tuple[ImageFont.FreeTypeFont, int]:
    for size in range(start, minimum - 1, -2):
        face = font(path, size)
        spacing = max(8, int(size * spacing_ratio))
        width, height = text_metrics(lines, face, spacing)
        if width <= max_width and height <= max_height:
            return face, spacing
    face = font(path, minimum)
    spacing = max(8, int(minimum * spacing_ratio))
    width, height = text_metrics(lines, face, spacing)
    if width > max_width or height > max_height:
        raise RuntimeError(
            f"Testo fuori area anche a {minimum}px: {width}×{height}, "
            f"limite {max_width}×{max_height}: {' / '.join(lines)}"
        )
    return face, spacing


def tracking_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    face: ImageFont.FreeTypeFont,
    fill: tuple[int, ...],
    tracking: int = 2,
) -> None:
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=face, fill=fill)
        x += int(draw.textlength(char, font=face)) + tracking


def add_corner_marks(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], accent: tuple[int, int, int]) -> None:
    x0, y0, x1, y1 = box
    length, width = 38, 6
    for x, y, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        draw.line((x, y, x + dx * length, y), fill=accent, width=width)
        draw.line((x, y, x, y + dy * length), fill=accent, width=width)


def draw_highlighted_lines(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    lines: list[str],
    face: ImageFont.FreeTypeFont,
    spacing: int,
    highlight: str | None,
    accent: tuple[int, int, int],
) -> tuple[int, int]:
    x, y = xy
    box = face.getbbox("Ag")
    line_height = max(1, box[3] - box[1])
    for line in lines:
        if highlight and highlight in line:
            before, after = line.split(highlight, 1)
            draw.text((x, y), before, font=face, fill=BONE)
            hx = x + int(draw.textlength(before, font=face))
            draw.text((hx, y), highlight, font=face, fill=accent)
            ax = hx + int(draw.textlength(highlight, font=face))
            draw.text((ax, y), after, font=face, fill=BONE)
        else:
            draw.text((x, y), line, font=face, fill=BONE)
        y += line_height + spacing
    return text_metrics(lines, face, spacing)


class Renderer:
    def __init__(self, ffmpeg: Path, *, motion: bool = False) -> None:
        validate_paper_edit()
        self.ffmpeg = ffmpeg
        self.motion = motion
        self.cues = read_cues()
        self.cue_starts = [cue.start for cue in self.cues]
        self.duration = self.cues[-1].end
        self.total_frames = int(round(self.duration * FPS))
        self.images = {
            path.stem: Image.open(path).convert("RGB")
            for path in SHOTS.iterdir()
            if path.suffix.lower() in {".jpg", ".jpeg", ".png"}
        }
        self.media_stills = {
            name: fit_inside(image, (MEDIA_BOX[2] - MEDIA_BOX[0], MEDIA_BOX[3] - MEDIA_BOX[1]))
            for name, image in self.images.items()
        }
        self.identity_art = self.media_stills["keyart"]
        # Il key art sorgente è 7680×4319: dopo la riduzione non serve più
        # trattenerlo in memoria durante il render dei 2910 frame.
        self.images.pop("keyart", None)
        self.gifs = {
            "fry": self._load_gif(RAW / "memes" / "meme-a-scettico.gif", Image.Resampling.NEAREST),
            "either": self._load_gif(RAW / "memes" / "meme-b-esausto.gif", Image.Resampling.LANCZOS),
        }
        self.footage_dir = CACHE / "footage-15fps"
        self._ensure_footage_frames()
        self.footage_files = sorted(self.footage_dir.glob("frame-*.jpg"))
        if not self.footage_files:
            raise RuntimeError("Nessun frame estratto dal footage ufficiale")

    def accent_for(self, cue: Cue) -> tuple[int, int, int]:
        accent = SCENE_ACCENTS[cue.index - 1]
        if not self.motion:
            return accent
        if accent == EVA:
            return MOTION_EVA
        if accent == ASH:
            return MOTION_ASH
        return accent

    def _load_gif(self, path: Path, resample: Image.Resampling) -> tuple[list[Image.Image], list[int], int]:
        if not path.is_file():
            raise FileNotFoundError(f"GIF mancante: {path}")
        source = Image.open(path)
        frames: list[Image.Image] = []
        cumulative: list[int] = []
        elapsed = 0
        target_size = (MEME_BOX[2] - MEME_BOX[0], MEME_BOX[3] - MEME_BOX[1])
        for source_frame in ImageSequence.Iterator(source):
            frame_image = fit_inside(source_frame.convert("RGB"), target_size, resample=resample)
            # Una scanline molto leggera integra la GIF nel sistema grafico.
            for y in range(0, frame_image.height, 6):
                strip = frame_image.crop((0, y, frame_image.width, min(y + 1, frame_image.height)))
                frame_image.paste(ImageEnhance.Brightness(strip).enhance(0.82), (0, y))
            elapsed += max(20, int(source_frame.info.get("duration", source.info.get("duration", 80))))
            frames.append(frame_image)
            cumulative.append(elapsed)
        return frames, cumulative, elapsed

    def _ensure_footage_frames(self) -> None:
        source = RAW / "footage" / "extra-coin-official-footage.mp4"
        if not source.is_file():
            raise FileNotFoundError(f"Footage mancante: {source}")
        existing = list(self.footage_dir.glob("frame-*.jpg")) if self.footage_dir.is_dir() else []
        if len(existing) >= 330:
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

    @functools.lru_cache(maxsize=96)
    def footage_media(self, index: int) -> Image.Image:
        index = max(0, min(index, len(self.footage_files) - 1))
        with Image.open(self.footage_files[index]) as source:
            image = source.convert("RGB")
        return fit_inside(image, (MEDIA_BOX[2] - MEDIA_BOX[0], MEDIA_BOX[3] - MEDIA_BOX[1]))

    def footage_at(self, seconds: float) -> Image.Image:
        return self.footage_media(int(max(0.0, seconds) * FOOTAGE_FPS))

    def footage_without_lower_ui(self, seconds: float) -> Image.Image:
        """Ritaglia l'UI inglese bassa della schermata build."""
        image = self.footage_media(int(max(0.0, seconds) * FOOTAGE_FPS))
        # Il crop conserva 16:9: rimuove circa l'11% inferiore e la stessa
        # quantità proporzionale sui lati, senza deformare l'immagine.
        crop_height = int(image.height * 0.89)
        crop_width = int(crop_height * 16 / 9)
        left = (image.width - crop_width) // 2
        cropped = image.crop((left, 0, left + crop_width, crop_height))
        return cover(cropped, (MEDIA_BOX[2] - MEDIA_BOX[0], MEDIA_BOX[3] - MEDIA_BOX[1]), centering=(0.5, 0.35))

    @staticmethod
    def exhausted_repeat(media: Image.Image) -> Image.Image:
        gray = ImageOps.grayscale(media).convert("RGB")
        gray = ImageEnhance.Contrast(gray).enhance(0.88)
        return ImageEnhance.Brightness(gray).enhance(0.58)

    def cue_at(self, seconds: float) -> Cue:
        index = bisect.bisect_right(self.cue_starts, seconds) - 1
        return self.cues[max(0, min(index, len(self.cues) - 1))]

    def draw_header(self, image: Image.Image, cue: Cue) -> None:
        draw = ImageDraw.Draw(image)
        accent = self.accent_for(cue)
        label = f"RECENSIONE / EXTRA COIN · {cue.index:02d}/15"
        tracking_text(draw, (SAFE_LEFT, 258), label, font(FONT_MONO, 26), accent)
        draw.rectangle((SAFE_LEFT, 324, SAFE_LEFT + 250, 332), fill=accent)
        draw.line((900, 258, 846, 326), fill=accent, width=10)

    def draw_progress(self, image: Image.Image, cue: Cue) -> None:
        draw = ImageDraw.Draw(image)
        width = SAFE_RIGHT - SAFE_LEFT
        draw.rectangle((SAFE_LEFT, PROGRESS_Y, SAFE_RIGHT, PROGRESS_Y + 5), fill=ASH)
        draw.rectangle(
            (SAFE_LEFT, PROGRESS_Y, SAFE_LEFT + int(width * cue.index / 15), PROGRESS_Y + 5),
            fill=self.accent_for(cue),
        )

    def draw_media(self, image: Image.Image, media: Image.Image, cue: Cue, *, credit: bool = False) -> None:
        image.paste(media, (MEDIA_BOX[0], MEDIA_BOX[1]))
        draw = ImageDraw.Draw(image)
        accent = self.accent_for(cue)
        draw.rectangle(MEDIA_BOX, outline=BONE, width=3)
        add_corner_marks(draw, MEDIA_BOX, accent)
        if credit:
            label = "FOOTAGE: EXTRA COIN — CINIC GAMES"
            face = font(FONT_MONO, 19)
            label_width = int(draw.textlength(label, font=face)) + 26
            label_x = MEDIA_BOX[0] + 14
            label_y = MEDIA_BOX[3] - 54
            draw.rectangle((label_x, label_y, label_x + label_width, label_y + 36), fill=INK)
            tracking_text(draw, (label_x + 13, label_y + 6), label, face, BONE, 1)

    def draw_still(self, image: Image.Image, name: str, cue: Cue) -> None:
        self.draw_media(image, self.media_stills[name], cue)

    def draw_gif(self, image: Image.Image, name: str, seconds_into_gif: float, cue: Cue) -> None:
        frames, cumulative, total = self.gifs[name]
        millis = int(max(0.0, seconds_into_gif) * 1000) % max(1, total)
        frame_index = min(bisect.bisect_right(cumulative, millis), len(frames) - 1)
        self.draw_media(image, frames[frame_index], cue)

    def draw_placeholder(self, image: Image.Image, cue: Cue, label: str) -> None:
        draw = ImageDraw.Draw(image)
        accent = self.accent_for(cue)
        draw.rectangle(MEDIA_BOX, fill=(18, 18, 22), outline=ASH, width=3)
        add_corner_marks(draw, MEDIA_BOX, accent)
        face = font(FONT_MONO, 28)
        width = int(draw.textlength(label, font=face))
        label_x = MEDIA_BOX[0] + ((MEDIA_BOX[2] - MEDIA_BOX[0] - width) // 2)
        tracking_text(draw, (label_x, 605), label, face, accent, 1)

    def draw_identity(self, image: Image.Image, cue: Cue) -> None:
        self.draw_header(image, cue)
        self.draw_media(image, self.identity_art, cue)
        draw = ImageDraw.Draw(image)
        tracking_text(draw, (SAFE_LEFT, 982), "RECENSIONE DI", font(FONT_MONO, 30), ACID, 2)
        title = font(FONT_TITLE, 168)
        draw.multiline_text((SAFE_LEFT, 1028), "EXTRA COIN", font=title, fill=BONE, spacing=0)
        draw.rectangle((SAFE_LEFT, 1248, SAFE_LEFT + 150, 1260), fill=NERV)
        meta = font(FONT_MONO, 28)
        tracking_text(draw, (SAFE_LEFT, 1303), "CINIC GAMES · 8 OTTOBRE 2024", meta, BONE, 1)
        tracking_text(draw, (SAFE_LEFT, 1360), "PC (STEAM) · NINTENDO SWITCH", meta, BONE, 1)
        tracking_text(draw, (SAFE_LEFT, 1437), "DAL 2026: PLAYSTATION · XBOX", meta, ACID, 1)
        self.draw_progress(image, cue)

    def draw_body(self, image: Image.Image, cue: Cue, *, y: int = TEXT_Y) -> None:
        draw = ImageDraw.Draw(image)
        accent = self.accent_for(cue)
        tracking_text(draw, (SAFE_LEFT, y - 70), SECTION_LABELS[cue.index - 1], font(FONT_MONO, 25), accent, 2)
        lines = DISPLAY_TEXT[cue.index].splitlines()
        face, spacing = fit_face(
            FONT_COPY,
            lines,
            start=68,
            minimum=48,
            max_width=SAFE_RIGHT - SAFE_LEFT,
            max_height=390,
        )
        draw_highlighted_lines(draw, (SAFE_LEFT, y), lines, face, spacing, HIGHLIGHTS.get(cue.index), accent)
        self.draw_progress(image, cue)

    def draw_question(self, image: Image.Image, cue: Cue) -> None:
        draw = ImageDraw.Draw(image)
        accent = self.accent_for(cue)
        tracking_text(draw, (SAFE_LEFT, 982), SECTION_LABELS[cue.index - 1], font(FONT_MONO, 25), accent, 2)
        title_lines = DISPLAY_TEXT[7].splitlines()
        title_face, spacing = fit_face(
            FONT_TITLE, title_lines, 140, 82, SAFE_RIGHT - SAFE_LEFT, 245, 0.10
        )
        draw.text((SAFE_LEFT, 1030), title_lines[0], font=title_face, fill=NERV)
        draw.text((SAFE_LEFT, 1030 + title_face.size + spacing), title_lines[1], font=title_face, fill=BONE)
        response_lines = QUESTION_RESPONSE.splitlines()
        response_face, response_spacing = fit_face(
            FONT_COPY, response_lines, 58, 44, SAFE_RIGHT - SAFE_LEFT, 150
        )
        draw.multiline_text(
            (SAFE_LEFT, 1308), QUESTION_RESPONSE, font=response_face, fill=BONE, spacing=response_spacing
        )
        self.draw_progress(image, cue)

    def draw_verdict(self, image: Image.Image, cue: Cue) -> None:
        draw = ImageDraw.Draw(image)
        accent = self.accent_for(cue)
        tracking_text(draw, (SAFE_LEFT, 470), SECTION_LABELS[cue.index - 1], font(FONT_MONO, 27), accent, 2)
        lines = DISPLAY_TEXT[14].splitlines()
        face, spacing = fit_face(
            FONT_TITLE, lines, 154, 82, SAFE_RIGHT - SAFE_LEFT, 620, 0.12
        )
        y = 545
        line_height = max(1, face.getbbox("Ag")[3] - face.getbbox("Ag")[1])
        for line in lines:
            draw.text((SAFE_LEFT, y), line, font=face, fill=ACID if "BRILLANTE" in line else BONE)
            y += line_height + spacing
        draw.rectangle((SAFE_LEFT, min(1375, y + 28), SAFE_LEFT + 320, min(1387, y + 40)), fill=accent)
        self.draw_progress(image, cue)

    def draw_cta(self, image: Image.Image, cue: Cue) -> None:
        draw = ImageDraw.Draw(image)
        accent = self.accent_for(cue)
        tracking_text(draw, (SAFE_LEFT, 500), SECTION_LABELS[cue.index - 1], font(FONT_MONO, 27), accent, 2)
        lines = DISPLAY_TEXT[15].splitlines()
        face, spacing = fit_face(
            FONT_TITLE, lines, 126, 76, SAFE_RIGHT - SAFE_LEFT, 430, 0.13
        )
        draw.multiline_text((SAFE_LEFT, 600), DISPLAY_TEXT[15], font=face, fill=BONE, spacing=spacing)
        draw.rectangle((SAFE_LEFT, 1085, SAFE_LEFT + 260, 1097), fill=NERV)
        tracking_text(
            draw,
            (SAFE_LEFT, 1340),
            "ALTRE STORIE DAI VIDEOGIOCHI · SEGUIMI",
            font(FONT_MONO, 25),
            ACID,
            1,
        )
        self.draw_progress(image, cue)

    def motion_state(
        self,
        cue: Cue,
        local: float,
        *,
        delay: float = 0.0,
        entry_frames: int = 6,
        exit_frames: int = 7,
        enter_offset: int = 24,
        exit_offset: int = 10,
        exit_enabled: bool | None = None,
    ) -> tuple[int, int, float]:
        """Restituisce alpha, spostamento verticale e avanzamento d'entrata."""
        entry_duration = entry_frames / FPS
        entry = ease_out_cubic((local - delay) / entry_duration)
        if exit_enabled is None:
            exit_enabled = cue.index not in {7, 9, 13, 15}
        if exit_enabled:
            remaining = (cue.end - cue.start) - local
            exit_progress = smoothstep(remaining / (exit_frames / FPS))
        else:
            exit_progress = 1.0
        opacity = int(round(255 * entry * exit_progress))
        dy = int(round(enter_offset * (1.0 - entry) - exit_offset * (1.0 - exit_progress)))
        return opacity, dy, entry

    @staticmethod
    def composite_overlay(image: Image.Image, overlay: Image.Image) -> None:
        image.paste(overlay, (0, 0), overlay)

    def draw_motion_body(self, image: Image.Image, cue: Cue, seconds: float, *, y: int = TEXT_Y) -> None:
        local = seconds - cue.start
        accent = self.accent_for(cue)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        label_alpha, label_dy, _ = self.motion_state(
            cue, local, entry_frames=5, enter_offset=12, exit_offset=7
        )
        if label_alpha:
            tracking_text(
                draw,
                (SAFE_LEFT, y - 70 + label_dy),
                SECTION_LABELS[cue.index - 1],
                font(FONT_MONO, 25),
                accent + (label_alpha,),
                2,
            )

        lines = DISPLAY_TEXT[cue.index].splitlines()
        face, spacing = fit_face(
            FONT_COPY,
            lines,
            start=68,
            minimum=48,
            max_width=SAFE_RIGHT - SAFE_LEFT,
            max_height=390,
        )
        line_height = max(1, face.getbbox("Ag")[3] - face.getbbox("Ag")[1])
        highlight = HIGHLIGHTS.get(cue.index)
        for line_index, line in enumerate(lines):
            delay = line_index * 2 / FPS
            alpha, dy, _ = self.motion_state(cue, local, delay=delay)
            if not alpha:
                continue
            line_y = y + line_index * (line_height + spacing) + dy
            if highlight and highlight in line:
                before, after = line.split(highlight, 1)
                accent_progress = smoothstep((local - delay - 4 / FPS) / (3 / FPS))
                highlight_fill = mix_color(BONE, accent, accent_progress) + (alpha,)
                draw.text((SAFE_LEFT, line_y), before, font=face, fill=BONE + (alpha,))
                highlight_x = SAFE_LEFT + int(draw.textlength(before, font=face))
                draw.text((highlight_x, line_y), highlight, font=face, fill=highlight_fill)
                after_x = highlight_x + int(draw.textlength(highlight, font=face))
                draw.text((after_x, line_y), after, font=face, fill=BONE + (alpha,))

                # Un solo gesto di sottolineatura accompagna il cambio colore,
                # poi scompare: la keyword resta colorata durante l'hold.
                wipe_in = smoothstep((local - delay - 5 / FPS) / (3 / FPS))
                wipe_out = smoothstep((local - delay - 10 / FPS) / (3 / FPS))
                underline_amount = wipe_in * (1.0 - wipe_out)
                if underline_amount > 0.01:
                    underline_width = int(draw.textlength(highlight, font=face) * wipe_in)
                    underline_alpha = int(alpha * underline_amount * 0.82)
                    underline_y = line_y + line_height + 6
                    draw.rectangle(
                        (highlight_x, underline_y, highlight_x + underline_width, underline_y + 4),
                        fill=accent + (underline_alpha,),
                    )
            else:
                draw.text((SAFE_LEFT, line_y), line, font=face, fill=BONE + (alpha,))

        self.composite_overlay(image, overlay)
        self.draw_progress(image, cue)

    def draw_motion_question(self, image: Image.Image, cue: Cue, seconds: float) -> None:
        local = seconds - cue.start
        accent = self.accent_for(cue)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        label_alpha, label_dy, _ = self.motion_state(
            cue, local, entry_frames=5, enter_offset=12, exit_enabled=False
        )
        if label_alpha:
            tracking_text(
                draw,
                (SAFE_LEFT, 982 + label_dy),
                SECTION_LABELS[cue.index - 1],
                font(FONT_MONO, 25),
                accent + (label_alpha,),
                2,
            )

        title_lines = DISPLAY_TEXT[7].splitlines()
        title_face, title_spacing = fit_face(
            FONT_TITLE, title_lines, 140, 82, SAFE_RIGHT - SAFE_LEFT, 245, 0.10
        )
        title_positions = (1030, 1030 + title_face.size + title_spacing)
        for line_index, (line, line_y) in enumerate(zip(title_lines, title_positions)):
            alpha, dy, _ = self.motion_state(
                cue,
                local,
                delay=(1 + line_index * 2) / FPS,
                entry_frames=6,
                exit_enabled=False,
            )
            if alpha:
                fill = NERV if line_index == 0 else BONE
                draw.text((SAFE_LEFT, line_y + dy), line, font=title_face, fill=fill + (alpha,))

        response_lines = QUESTION_RESPONSE.splitlines()
        response_face, response_spacing = fit_face(
            FONT_COPY, response_lines, 58, 44, SAFE_RIGHT - SAFE_LEFT, 150
        )
        response_height = max(
            1, response_face.getbbox("Ag")[3] - response_face.getbbox("Ag")[1]
        )
        for line_index, line in enumerate(response_lines):
            delay = 0.65 + line_index * 0.13
            alpha, dy, _ = self.motion_state(
                cue, local, delay=delay, entry_frames=6, exit_enabled=False, enter_offset=18
            )
            if alpha:
                line_y = 1308 + line_index * (response_height + response_spacing) + dy
                draw.text((SAFE_LEFT, line_y), line, font=response_face, fill=BONE + (alpha,))

        self.composite_overlay(image, overlay)
        self.draw_progress(image, cue)

    def draw_motion_verdict(self, image: Image.Image, cue: Cue, seconds: float) -> None:
        local = seconds - cue.start
        accent = self.accent_for(cue)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        label_alpha, label_dy, _ = self.motion_state(
            cue, local, entry_frames=5, enter_offset=12, exit_offset=7
        )
        if label_alpha:
            tracking_text(
                draw,
                (SAFE_LEFT, 470 + label_dy),
                SECTION_LABELS[cue.index - 1],
                font(FONT_MONO, 27),
                accent + (label_alpha,),
                2,
            )

        lines = DISPLAY_TEXT[14].splitlines()
        face, spacing = fit_face(
            FONT_TITLE, lines, 154, 82, SAFE_RIGHT - SAFE_LEFT, 620, 0.12
        )
        line_height = max(1, face.getbbox("Ag")[3] - face.getbbox("Ag")[1])
        target_y = 545
        delays = (2 / FPS, 10 / FPS, 12 / FPS)
        for line_index, line in enumerate(lines):
            alpha, dy, _ = self.motion_state(
                cue, local, delay=delays[line_index], entry_frames=6, enter_offset=28
            )
            if alpha:
                fill = ACID if "BRILLANTE" in line else BONE
                draw.text(
                    (SAFE_LEFT, target_y + line_index * (line_height + spacing) + dy),
                    line,
                    font=face,
                    fill=fill + (alpha,),
                )

        bar_y = min(1375, target_y + len(lines) * (line_height + spacing) + 28)
        bar_progress = ease_out_cubic((local - 18 / FPS) / (6 / FPS))
        bar_alpha, bar_dy, _ = self.motion_state(
            cue, local, delay=18 / FPS, entry_frames=6, enter_offset=0, exit_offset=7
        )
        if bar_alpha and bar_progress:
            draw.rectangle(
                (SAFE_LEFT, bar_y + bar_dy, SAFE_LEFT + int(320 * bar_progress), bar_y + 12 + bar_dy),
                fill=accent + (bar_alpha,),
            )

        self.composite_overlay(image, overlay)
        self.draw_progress(image, cue)

    def draw_motion_cta(self, image: Image.Image, cue: Cue, seconds: float) -> None:
        local = seconds - cue.start
        accent = self.accent_for(cue)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        label_alpha, label_dy, _ = self.motion_state(
            cue, local, entry_frames=5, enter_offset=12, exit_enabled=False
        )
        if label_alpha:
            tracking_text(
                draw,
                (SAFE_LEFT, 500 + label_dy),
                SECTION_LABELS[cue.index - 1],
                font(FONT_MONO, 27),
                accent + (label_alpha,),
                2,
            )

        lines = DISPLAY_TEXT[15].splitlines()
        face, spacing = fit_face(
            FONT_TITLE, lines, 126, 76, SAFE_RIGHT - SAFE_LEFT, 430, 0.13
        )
        line_height = max(1, face.getbbox("Ag")[3] - face.getbbox("Ag")[1])
        for line_index, line in enumerate(lines):
            delay = (2 if line_index == 0 else 7) / FPS
            alpha, dy, _ = self.motion_state(
                cue, local, delay=delay, entry_frames=6, exit_enabled=False, enter_offset=26
            )
            if alpha:
                line_y = 600 + line_index * (line_height + spacing) + dy
                draw.text((SAFE_LEFT, line_y), line, font=face, fill=BONE + (alpha,))

        bar_progress = ease_out_cubic((local - 14 / FPS) / (6 / FPS))
        if bar_progress:
            draw.rectangle(
                (SAFE_LEFT, 1085, SAFE_LEFT + int(260 * bar_progress), 1097),
                fill=NERV + (255,),
            )

        footer_alpha, footer_dy, _ = self.motion_state(
            cue,
            local,
            delay=20 / FPS,
            entry_frames=6,
            exit_enabled=False,
            enter_offset=14,
        )
        if footer_alpha:
            tracking_text(
                draw,
                (SAFE_LEFT, 1340 + footer_dy),
                "ALTRE STORIE DAI VIDEOGIOCHI · SEGUIMI",
                font(FONT_MONO, 25),
                ACID + (footer_alpha,),
                1,
            )

        self.composite_overlay(image, overlay)
        self.draw_progress(image, cue)

    def draw_visual(self, image: Image.Image, cue: Cue, seconds: float) -> None:
        local = seconds - cue.start
        index = cue.index
        if index == 2:
            self.draw_still(image, "mika depressa sul divano in casa sua mondo reale", cue)
        elif index == 3:
            first_split = (cue.end - cue.start) * 0.30
            if local < first_split:
                self.draw_media(image, self.footage_at(0.15 + local), cue, credit=True)
            else:
                self.draw_still(image, "xy-street", cue)
        elif index == 4:
            split = (cue.end - cue.start) * 0.50
            self.draw_still(image, "casa-mika" if local < split else "stanza-mika", cue)
        elif index == 5:
            duration = cue.end - cue.start
            first_split = duration / 3
            second_split = duration * 2 / 3
            if local < first_split:
                self.draw_still(image, "palestra", cue)
            elif local < second_split:
                self.draw_media(image, self.footage_at(8.25 + local - first_split), cue, credit=True)
            else:
                build_seconds = 6.05 + ((local - second_split) % 1.45)
                self.draw_media(image, self.footage_without_lower_ui(build_seconds), cue, credit=True)
        elif index == 6:
            # Lo stesso identico quadro torna due volte. La seconda passata è
            # svuotata e più scura: la routine si capisce senza lasciare in
            # campo i balloon inglesi presenti nel trailer.
            gym = self.media_stills["palestra"].copy()
            if local >= (cue.end - cue.start) * 0.50:
                gym = self.exhausted_repeat(gym)
            self.draw_media(image, gym, cue)
        elif index == 7:
            gif_start = cue.end - 1.2
            if seconds >= gif_start:
                self.draw_gif(image, "fry", seconds - gif_start, cue)
            else:
                self.draw_placeholder(image, cue, "IL DUBBIO")
        elif index == 8:
            first_split = (cue.end - cue.start) * 0.30
            if local < first_split:
                self.draw_media(image, self.footage_at(14.7 + local * 0.7), cue, credit=True)
            else:
                padel_seconds = 8.25 + ((local - first_split) % 3.35)
                self.draw_media(image, self.footage_at(padel_seconds), cue, credit=True)
        elif index == 9:
            gif_start = cue.end - 1.2
            if seconds >= gif_start:
                self.draw_gif(image, "either", seconds - gif_start, cue)
            else:
                self.draw_placeholder(image, cue, "INTENZIONE ≠ ASSOLUZIONE")
        elif index == 10:
            duration = cue.end - cue.start
            first_split = duration / 3
            second_split = duration * 2 / 3
            if local < first_split:
                self.draw_media(image, self.footage_at(7.0 + local), cue, credit=True)
            elif local < second_split:
                self.draw_media(image, self.footage_at(19.9 + local - first_split), cue, credit=True)
            else:
                self.draw_still(image, "quiet-point", cue)
        elif index == 11:
            duration = cue.end - cue.start
            if local < duration / 3:
                self.draw_still(image, "ron-cafe-01", cue)
            elif local < duration * 2 / 3:
                self.draw_still(image, "ron-cafe-02", cue)
            else:
                self.draw_still(image, "quiet-point", cue)
        elif index == 12:
            self.draw_still(image, "sogno-mika", cue)
        elif index == 13:
            self.draw_still(image, "sogno-mika", cue)
            x0, y0, x1, y1 = MEDIA_BOX
            ratio = min(0.98, 0.18 + local / max(0.1, cue.end - cue.start) * 0.80)
            cover_width = int((x1 - x0) * ratio / 2)
            draw = ImageDraw.Draw(image)
            draw.rectangle((x0, y0, x0 + cover_width, y1), fill=INK)
            draw.rectangle((x1 - cover_width, y0, x1, y1), fill=INK)

    def apply_macro_glitch(self, image: Image.Image, frame_index: int) -> Image.Image:
        # Solo quattro snodi macro; l'apertura resta leggibile dal frame zero.
        boundaries = [
            int(round(self.cues[cue_index - 1].start * FPS))
            for cue_index in (6, 8, 10, 14)
        ]
        if self.motion:
            # Nel montaggio animato il glitch vive soltanto nei tre frame che
            # precedono lo stacco. I nuovi glifi entrano quindi già puliti.
            ages = [boundary - frame_index for boundary in boundaries]
            active = [age for age in ages if 1 <= age <= 3]
            if not active:
                return image
            amount = (4 - min(active)) * 3
        else:
            pivots = [boundary - 1 for boundary in boundaries]
            distance = min((abs(frame_index - pivot) for pivot in pivots), default=99)
            if distance > 2:
                return image
            amount = 9 - distance * 3
        red, green, blue = image.split()
        result = Image.merge(
            "RGB",
            (ImageChops.offset(red, amount, 0), green, ImageChops.offset(blue, -amount, 0)),
        )
        draw = ImageDraw.Draw(result)
        y = 430 + (frame_index * 83) % 760
        draw.rectangle((SAFE_LEFT, y, SAFE_RIGHT, y + 8 + amount), fill=NERV)
        return result

    def render_frame(self, frame_index: int) -> Image.Image:
        seconds = min(frame_index / FPS, self.duration - 1 / FPS)
        cue = self.cue_at(seconds)
        image = Image.new("RGB", (W, H), INK)

        if self.motion:
            # Prima vengono composti sfondo, media e microheader. Il glitch si
            # applica qui; il layer testuale arriva dopo e resta sempre nitido.
            if cue.index == 1:
                self.draw_identity(image, cue)
            elif cue.index in {14, 15}:
                self.draw_header(image, cue)
            else:
                self.draw_header(image, cue)
                self.draw_visual(image, cue, seconds)
            image = self.apply_macro_glitch(image, frame_index)

            if cue.index == 14:
                self.draw_motion_verdict(image, cue, seconds)
            elif cue.index == 15:
                self.draw_motion_cta(image, cue, seconds)
            elif cue.index == 7:
                self.draw_motion_question(image, cue, seconds)
            elif cue.index != 1:
                self.draw_motion_body(image, cue, seconds)
            return image

        if cue.index == 1:
            self.draw_identity(image, cue)
        elif cue.index == 14:
            self.draw_header(image, cue)
            self.draw_verdict(image, cue)
        elif cue.index == 15:
            self.draw_header(image, cue)
            self.draw_cta(image, cue)
        else:
            self.draw_header(image, cue)
            self.draw_visual(image, cue, seconds)
            if cue.index == 7:
                self.draw_question(image, cue)
            else:
                self.draw_body(image, cue)

        # Entrata di tre frame: poi la composizione resta perfettamente ferma.
        elapsed_frames = int(round((seconds - cue.start) * FPS))
        if 0 <= elapsed_frames < 3 and cue.index != 1:
            offset = (2 - elapsed_frames) * 3
            shifted = Image.new("RGB", (W, H), INK)
            shifted.paste(image, (offset, 0))
            image = shifted
        return self.apply_macro_glitch(image, frame_index)

    def preview(self, output: Path) -> None:
        output.mkdir(parents=True, exist_ok=True)
        thumbs: list[Image.Image] = []
        for cue in self.cues:
            if cue.index == 7:
                seconds = cue.end - 0.65  # Fry e testo nello stesso frame.
            elif cue.index == 9:
                seconds = cue.end - 0.65  # Either/Or e testo nello stesso frame.
            else:
                seconds = cue.start + (cue.end - cue.start) * 0.52
            frame = self.render_frame(int(round(seconds * FPS)))
            frame.save(output / f"scene-{cue.index:02d}.png", optimize=True)
            thumbs.append(frame.resize((360, 640), Image.Resampling.LANCZOS))

        sheet = Image.new("RGB", (1080, 3200), INK)
        for index, thumb in enumerate(thumbs):
            sheet.paste(thumb, ((index % 3) * 360, (index // 3) * 640))
        sheet.save(output / "contact-sheet.jpg", quality=94, subsampling=0)
        print(f"Anteprima (15 frame): {output / 'contact-sheet.jpg'}", flush=True)

    def encode_frames(
        self,
        output: Path,
        frame_indices: range | list[int],
        *,
        label: str,
        preset: str = "veryfast",
        crf: int = 20,
    ) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        total_output_frames = len(frame_indices)
        output_duration = total_output_frames / FPS
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
            for output_index, frame_index in enumerate(frame_indices):
                process.stdin.write(self.render_frame(frame_index).tobytes())
                if output_index % (FPS * 5) == 0:
                    print(
                        f"{label} {output_index / FPS:05.1f}s / {output_duration:.1f}s",
                        flush=True,
                    )
        except BrokenPipeError as exc:
            raise RuntimeError("FFmpeg ha interrotto la codifica") from exc
        finally:
            process.stdin.close()
        return_code = process.wait()
        if return_code:
            raise RuntimeError(f"FFmpeg terminato con codice {return_code}")
        print(f"Video muto: {output}", flush=True)

    def video(self, output: Path, *, preset: str = "veryfast", crf: int = 20) -> None:
        self.encode_frames(
            output,
            range(self.total_frames),
            label="Render",
            preset=preset,
            crf=crf,
        )

    def motion_test(self, output: Path, *, preset: str = "veryfast", crf: int = 20) -> None:
        selected_frames: list[int] = []
        for cue_index in (2, 7, 9, 14, 15):
            cue = self.cues[cue_index - 1]
            selected_frames.extend(
                range(int(round(cue.start * FPS)), int(round(cue.end * FPS)))
            )
        self.encode_frames(
            output,
            selected_frames,
            label="Motion test",
            preset=preset,
            crf=crf,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render del reel Extra Coin — paper edit v0.5")
    parser.add_argument("--preview", action="store_true", help="genera 15 frame e una contact sheet")
    parser.add_argument("--motion", action="store_true", help="anima soltanto i layer testuali")
    parser.add_argument(
        "--motion-test",
        action="store_true",
        help="genera una prova breve con cue 02, 07, 09, 14 e 15",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--preset", default="veryfast", choices=("ultrafast", "veryfast", "faster", "fast", "medium"))
    parser.add_argument("--crf", type=int, default=20)
    args = parser.parse_args()

    ffmpeg = find_ffmpeg()
    print(f"FFmpeg: {ffmpeg}", flush=True)
    motion_enabled = args.motion or args.motion_test
    renderer = Renderer(ffmpeg, motion=motion_enabled)
    print(
        f"Paper edit: {len(renderer.cues)} cue · {renderer.duration:.1f}s · "
        f"{renderer.total_frames} frame · master muto · "
        f"testo {'animato' if motion_enabled else 'statico'}",
        flush=True,
    )
    if args.preview:
        renderer.preview(CACHE / "preview")
    elif args.motion_test:
        renderer.motion_test(
            args.output or CACHE / "motion-test-v01.mp4",
            preset=args.preset,
            crf=args.crf,
        )
    else:
        default_output = DIST / (
            "extra-coin-draft-06.mp4" if motion_enabled else "extra-coin-draft-06-static.mp4"
        )
        renderer.video(args.output or default_output, preset=args.preset, crf=args.crf)


if __name__ == "__main__":
    main()
