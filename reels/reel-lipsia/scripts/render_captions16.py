"""Fotografa scripts/captions.html fotogramma per fotogramma.

Stesso principio del motore che monta i reel da pagine web: la pagina non
"gira" mai: viene portata a un istante preciso, fotografata, portata
all'istante successivo. Per questo lo stesso JSON produce sempre gli stessi
PNG, anche su un computer lento, e rigenerando dopo aver corretto una parola
il resto resta identico.

Le PNG escono con lo sfondo trasparente, pronte per essere sovrapposte al
montaggio di moviepy da build_standup_html.py.

Uso:
    .venv/Scripts/python.exe scripts/render_captions.py                # tutti i frame
    .venv/Scripts/python.exe scripts/render_captions.py --every 25     # 1 frame al secondo, prova rapida
    .venv/Scripts/python.exe scripts/render_captions.py --preview      # anteprima nel browser
"""

import argparse
import functools
import http.server
import json
import shutil
import socketserver
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGE = "scripts/captions16.html"


def start_server(directory: Path):
    """Serve la cartella del reel su una porta libera, solo su localhost.

    Serve perche' la pagina possa caricare ../content/*.json: da file://
    il browser lo vieta.
    """
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(directory)
    )

    class Quiet(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

        def log_message(self, *args):  # pragma: no cover
            pass

    httpd = Quiet(("127.0.0.1", 0), handler)
    httpd.RequestHandlerClass.log_message = lambda *a, **k: None
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def main():
    ap = argparse.ArgumentParser()
    # posizionale come check_timeline.py e build_standup_html.py
    ap.add_argument("timeline", nargs="?", default="timeline_v7.json")
    ap.add_argument("--out", default="dist/captions")
    ap.add_argument("--every", type=int, default=1,
                    help="fotografa 1 frame ogni N (prova rapida)")
    ap.add_argument("--preview", action="store_true",
                    help="apre solo il server e stampa l'indirizzo")
    args = ap.parse_args()

    data = json.loads((ROOT / "content" / args.timeline).read_text(encoding="utf-8"))
    width, height, fps = data["width"], data["height"], data["fps"]
    total = sum(b["duration"] for b in data["beats"])
    n_frames = round(total * fps)

    httpd, base_url = start_server(ROOT)
    url = f"{base_url}/{PAGE}"

    if args.preview:
        print(f"Anteprima: {url}")
        print("Ctrl+C per chiudere.")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            httpd.shutdown()
        return

    out_dir = ROOT / args.out
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    print(f"{len(data['beats'])} beat | {total:.2f}s | {fps}fps -> {n_frames} frame")
    print(f"Output: {out_dir}")

    started = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",           # usa il Chrome gia' installato
            headless=True,
            args=["--force-color-profile=srgb", "--disable-lcd-text"],
        )
        page = browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=1,
        )
        page.add_init_script("window.__RENDER__ = true;")
        page.goto(url, wait_until="load")
        page.evaluate("async () => { await document.fonts.ready; }")

        info = page.evaluate("d => window.setTimeline(d)", data)
        print(f"Pagina pronta: {info['beats']} beat, {info['duration']:.2f}s")

        written = 0
        for i in range(n_frames):
            if i % args.every:
                continue
            page.evaluate("t => window.seek(t)", i / fps)
            page.screenshot(
                path=str(out_dir / f"frame_{i:05d}.png"),
                omit_background=True,
            )
            written += 1
            if written % 100 == 0:
                rate = written / (time.time() - started)
                print(f"  {written} frame | {rate:.1f} frame/s")

        browser.close()

    httpd.shutdown()
    elapsed = time.time() - started
    print(f"Fatto: {written} PNG in {elapsed:.1f}s ({written/elapsed:.1f} frame/s)")


if __name__ == "__main__":
    main()
