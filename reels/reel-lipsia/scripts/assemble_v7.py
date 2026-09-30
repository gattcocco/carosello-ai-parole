#!/usr/bin/env python3
"""Ricompone il MASTER finale v7 (YouTube 16:9) da fonti persistite nel progetto.

Catena:
  1. make_credits_v7.py   -> credits_tall.png (immagine alta dei titoli di coda)
  2. ffmpeg pad + scroll  -> clip titoli di coda 16:9 (34s)
  3. concat: montaggio muto (dist/discarica-dei-libri-v7-yt.mp4) + titoli di coda
  4. mux: letto musicale (dist/audio/newwave-lipsia.wav) con fade

NON rigenera didascalie e montaggio (lunghi): usa il montaggio muto gia' in dist/.
Per rigenerare TUTTO da capo vedi HANDOFF.md.

Uso:
    python scripts/assemble_v7.py          # v7
    python scripts/assemble_v7.py v8       # v8 "Dalla discarica a Saturno"
Richiede: ffmpeg nel PATH, Pillow, il font Bodoni MT + Consolas (Windows).
"""
import subprocess, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
BUILD = ROOT / "dist" / "_build"; BUILD.mkdir(parents=True, exist_ok=True)
VER    = sys.argv[1] if len(sys.argv) > 1 else "v7"
SUFFIX = "" if VER == "v7" else f"-{VER}"
SILENT = ROOT / "dist" / f"discarica-dei-libri-{VER}-yt.mp4"      # montaggio muto (corpo)
MUSIC  = ROOT / "dist" / "audio" / f"newwave-lipsia{SUFFIX}.wav"  # colonna sonora originale
OUT    = ROOT / "dist" / f"discarica-dei-libri-{VER}-youtube.mp4"  # master finale
CREDITS_SCRIPT = SCRIPTS / f"make_credits_{VER}.py"
CRED_SECONDS = 34

def run(cmd, **kw): print("»", " ".join(str(c) for c in cmd)); subprocess.run(cmd, check=True, **kw)

def main():
    for p in (SILENT, MUSIC):
        if not p.exists(): sys.exit(f"Manca: {p}\n(rigenera prima il montaggio muto — vedi HANDOFF.md)")

    # 1) immagine titoli di coda (make_credits scrive credits_tall.png nella cwd)
    run([sys.executable, str(CREDITS_SCRIPT)], cwd=str(BUILD))
    tall = BUILD / "credits_tall.png"
    H = Image.open(tall).height
    pad_h = H + 2160                       # 1080 nero sopra + 1080 sotto
    dist  = pad_h - 1080                   # corsa dello scroll
    padded = BUILD / "credits_padded.png"
    run(["ffmpeg","-y","-v","error","-i",str(tall),"-vf",f"pad=1920:{pad_h}:0:1080:color=0x080808",str(padded)])

    # 2) scroll verticale (titoli di coda 16:9)
    cred = BUILD / f"credits_{VER}.mp4"
    run(["ffmpeg","-y","-v","error","-loop","1","-i",str(padded),"-t",str(CRED_SECONDS),
         "-vf",f"crop=1920:1080:0:'(t/{CRED_SECONDS})*{dist}',format=yuv420p","-r","25",
         "-c:v","libx264","-preset","veryfast","-crf","20",str(cred)])

    # 3) concat corpo muto + titoli di coda
    concat = BUILD / f"concat_{VER}.txt"
    concat.write_text(f"file '{SILENT.as_posix()}'\nfile '{cred.as_posix()}'\n", encoding="utf-8")
    full = BUILD / f"full_silent_{VER}.mp4"
    run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(full)])

    # 4) letto musicale + fade (il fade-out chiude sugli ultimi 2,8 s del video)
    total = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                                  "-of","csv=p=0",str(full)],capture_output=True,text=True,check=True).stdout)
    fade_st = round(total - 2.8, 2)
    run(["ffmpeg","-y","-v","error","-i",str(full),"-i",str(MUSIC),
         "-filter_complex",f"[1:a]volume=0.92,afade=in:st=0:d=1.5,afade=out:st={fade_st}:d=2.8[a]",
         "-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-shortest",
         "-movflags","+faststart",str(OUT)])
    print(f"\nOK -> {OUT}")

if __name__ == "__main__":
    main()
