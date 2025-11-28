

import os
import argparse
import logging
from pathlib import Path
import subprocess

UPLOADS_DIR = Path(__file__).parent.parent / "input" / "uploads"
EXTRACTED_TEXT = Path(__file__).parent.parent / "extracted" / "text"
EXTRACTED_AUDIO = Path(__file__).parent.parent / "extracted" / "transcripts"
EXTRACTED_VIDEO = Path(__file__).parent.parent / "extracted" / "cleaned"

def detect_type(filename):
    ext = filename.suffix.lower()
    if ext in {".txt", ".md", ".html", ".htm"}:
        return "text"
    if ext in {".mp3", ".wav", ".m4a"}:
        return "audio"
    if ext in {".mp4", ".mov", ".avi", ".mkv"}:
        return "video"
    return "unknown"

def process_file(filepath, dry_run: bool = False, logger: logging.Logger | None = None):
    logger = logger or logging.getLogger("ingest")
    ftype = detect_type(filepath)
    if ftype == "text":
        out_path = EXTRACTED_TEXT / filepath.name
        logger.info("Text: %s -> %s", filepath.name, out_path)
        if not dry_run:
            EXTRACTED_TEXT.mkdir(parents=True, exist_ok=True)
            with open(filepath, "r", encoding="utf-8", errors="ignore") as fin, open(out_path, "w", encoding="utf-8") as fout:
                fout.write(fin.read())
            logger.info("✓ Text file processed: %s -> %s", filepath.name, out_path)
    elif ftype == "audio":
        out_path = EXTRACTED_AUDIO / filepath.name
        logger.info("Audio: %s -> %s", filepath.name, out_path)
        if not dry_run:
            EXTRACTED_AUDIO.mkdir(parents=True, exist_ok=True)
            with open(filepath, "rb") as fin, open(out_path, "wb") as fout:
                fout.write(fin.read())
            logger.info("✓ Audio file copied: %s -> %s", filepath.name, out_path)
            subprocess.run([
                "python3",
                str(Path(__file__).parent / "extract_audio.py"),
                "--audio",
                str(out_path),
                "--out",
                str(EXTRACTED_AUDIO),
            ])
    elif ftype == "video":
        out_path = EXTRACTED_VIDEO / filepath.name
        logger.info("Video: %s -> %s", filepath.name, out_path)
        if not dry_run:
            EXTRACTED_VIDEO.mkdir(parents=True, exist_ok=True)
            with open(filepath, "rb") as fin, open(out_path, "wb") as fout:
                fout.write(fin.read())
            logger.info("✓ Video file copied: %s -> %s", filepath.name, out_path)
            subprocess.run([
                "python3",
                str(Path(__file__).parent / "extract_video.py"),
                "--video",
                str(out_path),
                "--out",
                str(EXTRACTED_VIDEO),
            ])
    else:
        logger.warning("✗ Unknown file type: %s", filepath.name)

def main():
    parser = argparse.ArgumentParser(description="Ingest uploads folder and route files to extractors")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without writing files")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    logger = logging.getLogger("ingest")

    for file in UPLOADS_DIR.iterdir():
        if file.is_file():
            process_file(file, dry_run=args.dry_run, logger=logger)


if __name__ == "__main__":
    main()
