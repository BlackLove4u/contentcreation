"""extract_video.py
Video/audio extraction (stub) — extract audio, produce transcripts.
"""
import argparse


def extract_audio(video_path: str, out_dir: str):
    print(f"(stub) extracting audio from {video_path} -> {out_dir}")


def transcribe(audio_path: str, out_dir: str):
    print(f"(stub) transcribing {audio_path} -> {out_dir}")


def main():
    parser = argparse.ArgumentParser(description="Extract/transcribe video")
    parser.add_argument("--video", help="Video file path")
    parser.add_argument("--out", default="../extracted/transcripts/", help="Output directory")
    args = parser.parse_args()
    extract_audio(args.video, args.out)
    transcribe(args.video, args.out)


if __name__ == "__main__":
    main()
