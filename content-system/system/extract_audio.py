"""extract_audio.py
Extract metadata and transcribe audio files.

Behavior:
- If `OPENAI_API_KEY` is set and the `openai` package is installed, use OpenAI's
  Whisper API for transcription.
- Else if the `whisper` package is installed locally, use it as a fallback.
- Otherwise write a placeholder transcript and metadata file and warn the user.
"""

import argparse
import os
from pathlib import Path
import subprocess
from typing import Optional

AUDIO_DIR = Path(__file__).parent.parent / "extracted" / "transcripts"


def extract_metadata(audio_path: str, out_dir: str):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (Path(audio_path).stem + "_meta.txt")
    info = f"File: {audio_path}\nSize: {Path(audio_path).stat().st_size} bytes\n"
    with open(out_path, "w") as f:
        f.write(info)
    print(f"✓ Audio metadata extracted: {out_path}")


def transcribe_with_openai(audio_path: str) -> Optional[str]:
    try:
        import openai
    except Exception:
        return None
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    openai.api_key = api_key
    try:
        with open(audio_path, "rb") as af:
            # Newer OpenAI SDK provides Audio.transcribe
            if hasattr(openai, "Audio") and hasattr(openai.Audio, "transcribe"):
                resp = openai.Audio.transcribe("whisper-1", af)
                return resp.get("text")
            # Fallback: older method
            resp = openai.Whisper.transcribe(af)
            return resp.get("text")
    except Exception as e:
        print(f"! OpenAI transcription failed: {e}")
        return None


def transcribe_with_whisper_local(audio_path: str) -> Optional[str]:
    try:
        import whisper
    except Exception:
        return None
    try:
        model = whisper.load_model("small")
        result = model.transcribe(str(audio_path))
        return result.get("text")
    except Exception as e:
        print(f"! Local whisper transcription failed: {e}")
        return None


def transcribe(audio_path: str, out_dir: str):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = out_dir / (Path(audio_path).stem + "_transcript.txt")

    # Try OpenAI API first
    text = transcribe_with_openai(audio_path)
    if text:
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✓ Transcribed with OpenAI: {transcript_path}")
        return

    # Try local whisper fallback
    text = transcribe_with_whisper_local(audio_path)
    if text:
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✓ Transcribed with local whisper: {transcript_path}")
        return

    # Nothing available — write placeholder
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write("[transcription unavailable] Install OpenAI SDK and set OPENAI_API_KEY, or install `whisper` locally.")
    print(f"! Transcription unavailable, wrote placeholder: {transcript_path}")


def main():
    parser = argparse.ArgumentParser(description="Extract audio metadata and transcribe")
    parser.add_argument("--audio", required=True, help="Audio file path")
    parser.add_argument("--out", default=str(AUDIO_DIR), help="Output directory for metadata and transcripts")
    parser.add_argument("--transcribe", action="store_true", help="Run transcription")
    args = parser.parse_args()
    extract_metadata(args.audio, args.out)
    if args.transcribe:
        transcribe(args.audio, args.out)


if __name__ == "__main__":
    main()
