"""Controlla una timeline prima di renderizzarla.

Dieci secondi qui invece di scoprire l'errore dopo cinque minuti di PNG e
otto di montaggio. Verifica quello che gli script darebbero per scontato:
evidenziazioni che esistono davvero nel testo, asset presenti sul disco,
durate sensate, e -- misurandolo nel browser, non a stima -- se il testo
ci sta nelle quattro righe.

Uso:
    .venv/Scripts/python.exe scripts/check_timeline.py
    .venv/Scripts/python.exe scripts/check_timeline.py timeline_v3.json
    .venv/Scripts/python.exe scripts/check_timeline.py --no-browser   # solo controlli statici

Esce con codice 1 se trova errori, 0 se ci sono solo avvisi.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Soglie editoriali, non regole tecniche: sono i punti in cui un reel
# smette di essere leggibile sul telefono. Cambiale se non ti tornano.
MIN_SHOT_DUR      = 0.60   # sotto, l'inquadratura e' un lampo
MAX_CHARS_PER_SEC = 25.0   # sopra, la battuta scorre troppo in fretta
MIN_READ_TAIL     = 0.80   # secondi di frase ferma dopo l'ultima parola entrata
VALID_KINDS       = {"image", "clip", "solid"}

errors, warnings, notes = [], [], []
silent_beats = []


def err(beat, msg):
    errors.append((beat, msg))


def warn(beat, msg):
    warnings.append((beat, msg))


def clip_duration(path, _cache={}):
    """Durata reale di una clip, letta una volta sola per file."""
    key = str(path)
    if key not in _cache:
        try:
            r = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", key],
                capture_output=True, text=True, timeout=20,
            )
            _cache[key] = float(r.stdout.strip())
        except Exception:
            _cache[key] = None
    return _cache[key]


def load_asset_ids():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from build_fullscreen import IMAGE_SOURCES
    images = {k: p for k, p in IMAGE_SOURCES.items()}
    clips = {p.stem: p for p in sorted((ROOT / "assets" / "clips").glob("*.mp4"))}
    return images, clips


def static_checks(data, images, clips):
    for key in ("width", "height", "fps", "beats"):
        if key not in data:
            err(None, f"manca il campo obbligatorio '{key}'")
    if errors:
        return

    if not isinstance(data["beats"], list) or not data["beats"]:
        err(None, "'beats' e' vuoto")
        return

    used = set()

    for i, beat in enumerate(data["beats"], 1):
        text = beat.get("text") or ""
        if not isinstance(text, str):
            err(i, f"'text' deve essere una stringa o null, non {type(text).__name__}")
            continue

        # Beat muto: nessuna didascalia e nessuna fascia scura. Voluto per le
        # card che portano gia' la loro grafica, come quella finale.
        silent = not text.strip()
        if silent:
            silent_beats.append(i)
            if beat.get("highlight"):
                err(i, "beat senza testo ma con highlight: togli l'highlight")

        hl = beat.get("highlight")
        if hl and not silent:
            if not isinstance(hl, str) or not hl.strip():
                err(i, "highlight presente ma vuoto: usa null")
            elif text.lower().find(hl.lower()) == -1:
                err(i, f"highlight non trovato nel testo: {hl!r}\n"
                       f"            il verde non comparirebbe, senza nessun errore a runtime")
            elif hl.strip().lower() == text.strip().lower():
                warn(i, "l'highlight copre tutto il testo: nessun contrasto")

        dur = beat.get("duration")
        if not isinstance(dur, (int, float)) or dur <= 0:
            err(i, f"duration non valida: {dur!r}")
            continue

        cps = len(text) / dur
        if not silent and cps > MAX_CHARS_PER_SEC:
            warn(i, f"{cps:.0f} caratteri al secondo (soglia {MAX_CHARS_PER_SEC:.0f}): "
                    f"allunga la durata o accorcia la battuta")

        shots = beat.get("shots")
        if not isinstance(shots, list) or not shots:
            err(i, "nessuno shot")
            continue

        per_shot = dur / len(shots)
        if per_shot < MIN_SHOT_DUR:
            warn(i, f"{len(shots)} shot in {dur}s = {per_shot:.2f}s ciascuno "
                    f"(sotto {MIN_SHOT_DUR}s si legge come un lampo)")

        for j, shot in enumerate(shots, 1):
            kind = shot.get("kind")
            src = shot.get("source")
            if kind not in VALID_KINDS:
                err(i, f"shot {j}: kind sconosciuto {kind!r} "
                       f"(ammessi: {', '.join(sorted(VALID_KINDS))})")
                continue
            if kind == "solid":
                continue
            if not src:
                err(i, f"shot {j}: manca 'source'")
                continue

            used.add((kind, src))
            if kind == "image":
                path = images.get(src)
                if path is None:
                    err(i, f"shot {j}: id immagine sconosciuto {src!r}\n"
                           f"            disponibili: {', '.join(sorted(images))}")
                elif not path.exists():
                    err(i, f"shot {j}: file mancante per {src!r}: {path}")
            else:
                path = clips.get(src)
                if path is None:
                    err(i, f"shot {j}: clip sconosciuta {src!r} "
                           f"(cercata in assets/clips/{src}.mp4)")
                else:
                    # seek + durata dello shot non devono superare la clip:
                    # oltre, build_clip_shot la rimanda da capo e a meta'
                    # inquadratura si vede un salto.
                    avail = clip_duration(path)
                    seek = shot.get("seek") or 0
                    if avail and seek + per_shot > avail + 0.05:
                        warn(i, f"shot {j}: {src} dura {avail:.1f}s ma servono "
                                f"{seek + per_shot:.1f}s (seek {seek} + {per_shot:.1f}s): "
                                f"la clip riparte da capo a meta' inquadratura")

    # Informativo: materiale che hai sul disco e non stai usando.
    unused_img = sorted(set(images) - {s for k, s in used if k == "image"})
    unused_clip = sorted(set(clips) - {s for k, s in used if k == "clip"})
    if unused_img:
        notes.append("immagini non usate: " + ", ".join(unused_img))
    if unused_clip:
        notes.append("clip non usate:     " + ", ".join(unused_clip))


def probe_copy(data):
    """Copia buona per la misura dell'impaginazione.

    Corpo e numero di righe non dipendono dalla durata: sostituendo le
    durate non valide con un segnaposto, il controllo del testo troppo
    lungo funziona anche su una timeline che ha gia' altri errori.
    """
    beats = []
    for beat in data.get("beats", []):
        text = beat.get("text")
        dur = beat.get("duration")
        beats.append({
            "text": text if isinstance(text, str) else "",
            "highlight": beat.get("highlight"),
            "duration": dur if isinstance(dur, (int, float)) and dur > 0 else 3.0,
            "shots": beat.get("shots", []),
        })
    return {**data, "beats": beats}


def structure_ok(data):
    return (
        isinstance(data.get("width"), int)
        and isinstance(data.get("height"), int)
        and isinstance(data.get("beats"), list)
        and len(data["beats"]) > 0
    )


def browser_checks(data, real_durations):
    """Impagina davvero nel browser e riporta corpo, righe e tempi."""
    from playwright.sync_api import sync_playwright
    from render_captions import start_server, PAGE

    httpd, base_url = start_server(ROOT)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            page = browser.new_page(
                viewport={"width": data["width"], "height": data["height"]},
                device_scale_factor=1,
            )
            page.add_init_script("window.__RENDER__ = true;")
            page.goto(f"{base_url}/{PAGE}", wait_until="load")
            page.evaluate("async () => { await document.fonts.ready; }")
            page.evaluate("d => window.setTimeline(d)", data)
            measures = page.evaluate("() => window.measure()")
            browser.close()
    finally:
        httpd.shutdown()

    for m in measures:
        i = m["index"] + 1
        if m.get("silent"):
            continue
        if m["overflow"]:
            err(i, f"il testo non ci sta: {m['lineCount']} righe anche al corpo minimo "
                   f"(52px, massimo 4). Accorcia la battuta o dividila in due beat")
        # Il margine di lettura ha senso solo se la durata vera e' valida:
        # sulle altre il beat ha gia' un errore suo.
        real = real_durations.get(m["index"])
        if real is None:
            continue
        tail = real - m["entranceEnd"]
        if tail < MIN_READ_TAIL:
            warn(i, f"solo {tail:.2f}s di frase ferma dopo l'ultima parola "
                    f"(sotto {MIN_READ_TAIL}s si fa in tempo a leggere a fatica)")
    return measures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("timeline", nargs="?", default="timeline_v4.json")
    ap.add_argument("--no-browser", action="store_true",
                    help="salta l'impaginazione reale (piu' veloce, meno completo)")
    args = ap.parse_args()

    path = ROOT / "content" / args.timeline
    if not path.exists():
        print(f"[ER] file non trovato: {path}")
        return 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[ER] JSON non valido in {args.timeline}: riga {e.lineno}, colonna {e.colno}")
        print(f"     {e.msg}")
        return 1

    images, clips = load_asset_ids()
    static_checks(data, images, clips)

    measures = None
    if not args.no_browser and structure_ok(data):
        real_durations = {
            i: b["duration"]
            for i, b in enumerate(data["beats"])
            if isinstance(b.get("duration"), (int, float)) and b["duration"] > 0
        }
        try:
            measures = browser_checks(probe_copy(data), real_durations)
        except Exception as exc:
            warn(None, f"impaginazione nel browser non riuscita: {exc}")

    beats = data.get("beats", [])
    total = sum(b.get("duration", 0) for b in beats if isinstance(b.get("duration"), (int, float)))
    fps = data.get("fps", 25)

    print(f"{args.timeline}: {len(beats)} beat | {total:.2f}s | "
          f"{data.get('width')}x{data.get('height')} @ {fps}fps | "
          f"{round(total * fps)} frame")
    print("-" * 72)

    for label, items in (("ER", errors), ("!!", warnings)):
        # in ordine di beat, non nell'ordine in cui i controlli sono girati
        for beat, msg in sorted(items, key=lambda x: (x[0] is not None, x[0] or 0)):
            where = f"beat {beat:>2}" if beat else "timeline"
            print(f"[{label}] {where}: {msg}")

    if measures:
        tight = [m for m in measures
                 if not m.get("silent") and m["fontSize"] <= 60]
        if tight:
            print(f"[--] beat impaginati sotto i 60px (piu' fitti da leggere): "
                  + ", ".join(str(m['index'] + 1) for m in tight))

    if silent_beats:
        notes.insert(0, "beat senza didascalia (voluto): "
                     + ", ".join(str(b) for b in silent_beats))

    for n in notes:
        print(f"[--] {n}")

    print("-" * 72)
    if errors:
        print(f"{len(errors)} errori, {len(warnings)} avvisi. Non renderizzare.")
        return 1
    print(f"Nessun errore, {len(warnings)} avvisi. Puoi renderizzare.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
