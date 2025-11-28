"""extract_audio.py
Extract metadata and transcribe audio files.

Behavior:
- If `OPENAI_API_KEY` is set and the `openai` package is installed, use OpenAI's
  Whisper API for transcription.
- Else if the `whisper` package is installed locally, use it as a fallback.
- Otherwise write a placeholder transcript and metadata file and warn the user.

Includes retry logic with exponential backoff for robustness.
"""

import argparse
import logging
import os
import time
from pathlib import Path
import subprocess
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

AUDIO_DIR = Path(__file__).parent.parent / "extracted" / "transcripts"


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


def extract_metadata(audio_path: str, out_dir: str):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (Path(audio_path).stem + "_meta.txt")
    info = f"File: {audio_path}\nSize: {Path(audio_path).stat().st_size} bytes\n"
    with open(out_path, "w") as f:
        f.write(info)
    print(f"✓ Audio metadata extracted: {out_path}")


def transcribe_with_openai(audio_path: str) -> Optional[str]:
    """Attempt transcription using OpenAI's Whisper API."""
    try:
        import openai
    except ImportError:
        logger.debug("openai package not installed")
        return None
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.debug("OPENAI_API_KEY not set")
        return None
    
    try:
        openai.api_key = api_key
        with open(audio_path, "rb") as af:
            # Newer OpenAI SDK provides Audio.transcribe
            if hasattr(openai, "Audio") and hasattr(openai.Audio, "transcribe"):
                resp = openai.Audio.transcribe("whisper-1", af)
                return resp.get("text")
            # Fallback: older method
            resp = openai.Whisper.transcribe(af)
            return resp.get("text")
    except Exception as e:
        logger.error(f"OpenAI transcription failed: {e}")
        raise


def transcribe_with_whisper_local(audio_path: str) -> Optional[str]:
    """Attempt transcription using local whisper model."""
    try:
        import whisper
    except ImportError:
        logger.debug("whisper package not installed")
        return None
    
    try:
        logger.info("Loading local whisper model (this may take a moment on first run)...")
        model = whisper.load_model("small")
        logger.info("Transcribing with local whisper...")
        result = model.transcribe(str(audio_path))
        return result.get("text")
    except Exception as e:
        logger.error(f"Local whisper transcription failed: {e}")
        raise


@retry_on_exception(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
def _transcribe_openai_with_retry(audio_path: str) -> str:
    """Wrapper to retry OpenAI transcription."""
    return transcribe_with_openai(audio_path)


@retry_on_exception(max_retries=2, initial_delay=1.0, backoff_factor=2.0)
def _transcribe_whisper_with_retry(audio_path: str) -> str:
    """Wrapper to retry local whisper transcription."""
    return transcribe_with_whisper_local(audio_path)


def transcribe(audio_path: str, out_dir: str):
    """Transcribe audio with fallbacks: OpenAI -> local whisper -> placeholder."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = out_dir / (Path(audio_path).stem + "_transcript.txt")

    # Try OpenAI API first (with retry)
    try:
        logger.info(f"Attempting OpenAI transcription for {Path(audio_path).name}...")
        text = _transcribe_openai_with_retry(audio_path)
        if text:
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(text)
            logger.info(f"✓ Transcribed with OpenAI: {transcript_path}")
            return
    except Exception as e:
        logger.warning(f"OpenAI transcription unavailable: {e}")

    # Try local whisper fallback (with retry)
    try:
        logger.info(f"Attempting local whisper transcription for {Path(audio_path).name}...")
        text = _transcribe_whisper_with_retry(audio_path)
        if text:
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(text)
            logger.info(f"✓ Transcribed with local whisper: {transcript_path}")
            return
    except Exception as e:
        logger.warning(f"Local whisper transcription unavailable: {e}")

    # Nothing available — write placeholder
    placeholder_text = (
        "[transcription unavailable] Install OpenAI SDK and set OPENAI_API_KEY, "
        "or install `whisper` locally and ensure ffmpeg is on PATH."
    )
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(placeholder_text)
    logger.warning(f"Transcription unavailable, wrote placeholder: {transcript_path}")


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
