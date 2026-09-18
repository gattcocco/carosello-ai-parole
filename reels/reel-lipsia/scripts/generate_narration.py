"""Genera la narrazione audio unica per 'La discarica dei libri' (Gemini TTS).

Legge content/narration_full.txt per intero e lo affida a una sola chiamata
TTS: il testo e' scritto come discorso continuo (vedi primo-montaggio.md) e
la timeline video ha durate fisse gia' stimate su questa lettura, quindi non
serve (ne' e' corretto) spezzare l'audio per segmento.

Uso:
    .venv/Scripts/python.exe scripts/generate_narration.py
"""

import mimetypes
import os
import struct
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT.parent.parent.parent / ".env")

MODEL = "gemini-3.1-flash-tts-preview"
VOICE = "Achird"
AUDIO_PROFILE = "Voce maschile profonda e ferma, da documentario storico, in italiano."
DIRECTORS_NOTE = (
    "Stile: misurato, quasi sommesso nei passaggi piu' intimi. "
    "Ritmo: lento, con piccole pause tra le frasi. Accento: italiano neutro."
)


def build_prompt(text: str) -> str:
    return f"""Read the following transcript based on the audio profile and director's note.

# Audio Profile
{AUDIO_PROFILE}

# Director's note
{DIRECTORS_NOTE}

## Transcript:
{text}"""


def parse_audio_mime_type(mime_type: str) -> dict:
    bits_per_sample = 16
    rate = 24000
    for param in mime_type.split(";"):
        param = param.strip()
        if param.lower().startswith("rate="):
            try:
                rate = int(param.split("=", 1)[1])
            except (ValueError, IndexError):
                pass
        elif param.startswith("audio/L"):
            try:
                bits_per_sample = int(param.split("L", 1)[1])
            except (ValueError, IndexError):
                pass
    return {"bits_per_sample": bits_per_sample, "rate": rate}


def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    params = parse_audio_mime_type(mime_type)
    bits_per_sample = params["bits_per_sample"]
    sample_rate = params["rate"]
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", chunk_size, b"WAVE", b"fmt ", 16, 1,
        num_channels, sample_rate, byte_rate, block_align,
        bits_per_sample, b"data", data_size,
    )
    return header + audio_data


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY non trovata: controlla il file .env alla root del pacchetto.")

    text = (ROOT / "content" / "narration_full.txt").read_text(encoding="utf-8").strip()

    client = genai.Client(api_key=api_key)
    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=build_prompt(text))]),
    ]
    config = types.GenerateContentConfig(
        temperature=1,
        response_modalities=["audio"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE)
            )
        ),
    )

    audio_data = bytearray()
    mime_type = ""
    for chunk in client.models.generate_content_stream(model=MODEL, contents=contents, config=config):
        if chunk.parts is None:
            continue
        part = chunk.parts[0]
        if part.inline_data and part.inline_data.data:
            audio_data.extend(part.inline_data.data)
            mime_type = part.inline_data.mime_type
        elif chunk.text:
            print(chunk.text)

    if not audio_data:
        raise SystemExit("Nessun audio ricevuto dal modello.")

    ext = mimetypes.guess_extension(mime_type)
    data = bytes(audio_data)
    if ext is None:
        ext = ".wav"
        data = convert_to_wav(data, mime_type)

    out_dir = ROOT / "dist" / "audio"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"narrazione-discarica{ext}"
    out_path.write_bytes(data)
    print(f"Salvato: {out_path}")


if __name__ == "__main__":
    main()
