"""extract_video.py
Extract video metadata, extract audio and transcribe the audio.

This script attempts to extract audio from the video using `ffmpeg` (if available),
and then transcribes using the same logic as `extract_audio.py` (OpenAI -> local whisper -> placeholder).
"""

import argparse
import os
import subprocess
from pathlib import Path
from typing import Optional

from . import extract_audio as _audio_module


def extract_metadata(video_path: str, out_dir: str):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (Path(video_path).stem + "_meta.txt")
    info = f"File: {video_path}\nSize: {Path(video_path).stat().st_size} bytes\n"
    with open(out_path, "w") as f:
        f.write(info)
    print(f"✓ Video metadata extracted: {out_path}")


def extract_audio_from_video(video_path: str, out_dir: str) -> Optional[str]:
    """Use ffmpeg to extract audio to a wav file. Returns path or None."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_path = out_dir / (Path(video_path).stem + "_audio.wav")
    cmd = ["ffmpeg", "-y", "-i", str(video_path), "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(audio_path)]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✓ Extracted audio to: {audio_path}")
        return str(audio_path)
    except Exception:
        print("! ffmpeg audio extraction failed or ffmpeg not installed; skipping audio extraction")
        return None


def main():
    parser = argparse.ArgumentParser(description="Extract/transcribe video")
    parser.add_argument("--video", required=True, help="Video file path")
    parser.add_argument("--out", default=str(Path(__file__).parent.parent / "extracted" / "cleaned"), help="Output directory")
    parser.add_argument("--transcribe", action="store_true", help="Run transcription after extracting audio")
    args = parser.parse_args()

    extract_metadata(args.video, args.out)
    audio = extract_audio_from_video(args.video, args.out)
    if args.transcribe:
        if audio:
            # Use the audio transcribe function from extract_audio module
            try:
                _audio_module.transcribe(audio, args.out)
            except Exception as e:
                print(f"! Transcription via extract_audio failed: {e}")
        else:
            # Attempt to transcribe the video file directly (some transcribers can handle it)
            try:
                _audio_module.transcribe(args.video, args.out)
            except Exception as e:
                print(f"! Transcription failed: {e}")


if __name__ == "__main__":
    main()
