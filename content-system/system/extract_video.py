"""extract_video.py
Extract video metadata, extract audio and transcribe the audio.

This script attempts to extract audio from the video using `ffmpeg` (if available),
and then transcribes using the same logic as `extract_audio.py` (OpenAI -> local whisper -> placeholder).

Includes retry logic with exponential backoff for robustness.
"""

import argparse
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

# Handle both standalone and package imports
try:
    from . import extract_audio as _audio_module
except ImportError:
    # When run as a script, import as a module
    sys.path.insert(0, str(Path(__file__).parent))
    import extract_audio as _audio_module

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def retry_on_exception(max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0):
    """Decorator to retry a function with exponential backoff.
    
    Args:
        max_retries: maximum number of attempts
        initial_delay: initial delay in seconds between retries
        backoff_factor: multiply delay by this after each failure
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt}/{max_retries} failed for {func.__name__}: {e}")
                    if attempt == max_retries:
                        logger.error(f"Max retries ({max_retries}) reached for {func.__name__}. Raising exception.")
                        raise
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator


def extract_metadata(video_path: str, out_dir: str):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (Path(video_path).stem + "_meta.txt")
    try:
        file_size = Path(video_path).stat().st_size
        info = f"File: {video_path}\nSize: {file_size} bytes\n"
        with open(out_path, "w") as f:
            f.write(info)
        logger.info(f"✓ Video metadata extracted: {out_path}")
    except Exception as e:
        logger.error(f"Failed to extract video metadata: {e}")


@retry_on_exception(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
def _extract_audio_ffmpeg_with_retry(video_path: str, audio_path: Path) -> None:
    """Wrapper to retry ffmpeg audio extraction."""
    cmd = ["ffmpeg", "-y", "-i", str(video_path), "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(audio_path)]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def extract_audio_from_video(video_path: str, out_dir: str) -> Optional[str]:
    """Use ffmpeg to extract audio to a wav file. Returns path or None."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_path = out_dir / (Path(video_path).stem + "_audio.wav")
    
    try:
        logger.info(f"Attempting to extract audio from {Path(video_path).name} using ffmpeg...")
        _extract_audio_ffmpeg_with_retry(video_path, audio_path)
        logger.info(f"✓ Extracted audio to: {audio_path}")
        return str(audio_path)
    except FileNotFoundError:
        logger.error("ffmpeg not installed or not on PATH; skipping audio extraction")
        return None
    except Exception as e:
        logger.error(f"ffmpeg audio extraction failed: {e}; skipping audio extraction")
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
                logger.info(f"Transcribing extracted audio {Path(audio).name}...")
                _audio_module.transcribe(audio, args.out)
            except Exception as e:
                logger.error(f"Transcription via extract_audio failed: {e}")
        else:
            # Attempt to transcribe the video file directly (some transcribers can handle it)
            try:
                logger.info(f"Attempting to transcribe video {Path(args.video).name} directly...")
                _audio_module.transcribe(args.video, args.out)
            except Exception as e:
                logger.error(f"Direct video transcription failed: {e}")


if __name__ == "__main__":
    main()
