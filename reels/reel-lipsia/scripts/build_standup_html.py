"""Come build_standup.py, ma le didascalie arrivano da scripts/captions.html.

Cambia un pezzo solo della catena. Il montaggio visivo (Ken Burns sulle
immagini, cover-crop 9:16 sulle clip, concatenazione) resta quello di
build_standup.py: qui viene importato, non riscritto.

Al posto di caption_overlay(), che disegna una PNG ferma con PIL e la tiene
immobile per tutta la durata del beat, sovrappone la sequenza di PNG
trasparenti prodotta da render_captions.py, dove il testo entra parola per
parola e l'evidenziazione arriva con una passata.

Prima di usarlo:
    .venv/Scripts/python.exe scripts/render_captions.py

Uso:
    .venv/Scripts/python.exe scripts/build_standup_html.py [timeline_v4.json]
"""

import json
import sys
from pathlib import Path

from moviepy import CompositeVideoClip, ImageSequenceClip, concatenate_videoclips

from build_standup import build_visual_shot

ROOT = Path(__file__).resolve().parent.parent
CAPTIONS_DIR = ROOT / "dist" / "captions"


def load_captions(fps: int, expected: int):
    frames = sorted(CAPTIONS_DIR.glob("frame_*.png"))
    if not frames:
        raise SystemExit(
            f"Nessuna PNG in {CAPTIONS_DIR}.\n"
            f"Lancia prima: .venv/Scripts/python.exe scripts/render_captions.py"
        )
    if len(frames) != expected:
        raise SystemExit(
            f"Trovate {len(frames)} PNG ma ne servono {expected}.\n"
            f"Probabilmente hai usato --every: rilancia render_captions.py senza."
        )
    # with_mask=True legge il canale alpha delle PNG e lo usa come maschera,
    # cosi' il testo si sovrappone al footage invece di coprirlo con un rettangolo.
    return ImageSequenceClip([str(f) for f in frames], fps=fps, with_mask=True)


def main():
    timeline_name = sys.argv[1] if len(sys.argv) > 1 else "timeline_v4.json"
    data = json.loads((ROOT / "content" / timeline_name).read_text(encoding="utf-8"))
    width, height, fps = data["width"], data["height"], data["fps"]

    # 1) stessa logica di build_standup: gli shot di un beat si dividono
    #    la durata del beat in parti uguali
    flat_shots = []
    for beat in data["beats"]:
        n = len(beat["shots"])
        per_shot_dur = beat["duration"] / n
        for shot in beat["shots"]:
            flat_shots.append({**shot, "duration": per_shot_dur})

    total_duration = sum(b["duration"] for b in data["beats"])
    n_frames = round(total_duration * fps)
    print(f"Beat: {len(data['beats'])} | shot: {len(flat_shots)} | "
          f"durata: {total_duration:.2f}s | frame: {n_frames}")

    # 2) il montaggio visivo, identico a prima
    shot_clips = [build_visual_shot(s, s["duration"], width, height, fps) for s in flat_shots]
    base = concatenate_videoclips(shot_clips, method="chain")

    # 3) le didascalie animate, una sola clip sopra tutto
    captions = load_captions(fps, n_frames)
    print(f"Didascalie: {captions.duration:.2f}s da {CAPTIONS_DIR.name}/")

    final = CompositeVideoClip([base, captions], size=(width, height)).with_duration(total_duration)

    # Il nome di default segue la timeline, cosi' non si accumulano output
    # che non si sa piu' da quale sorgente vengano.
    version = Path(timeline_name).stem.replace("timeline_", "") or "x"
    default_name = f"discarica-dei-libri-{version}-html.mp4"
    out_path = ROOT / "dist" / data.get("out_name_html", default_name)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(str(out_path), fps=fps, codec="libx264", audio=False)
    print(f"Salvato: {out_path}")


if __name__ == "__main__":
    main()
