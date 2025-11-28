"""scheduler_prep.py
Move generated content to scheduler_ready folders for each platform.
"""

import os
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "content"
SCHEDULER_READY = Path(__file__).parent.parent / "scheduler_ready"

def prepare_for_instagram(post_text: str, image_path: str, out_dir: str):
    """Save an instagram-ready text file (and optionally note the image path).

    This is a small helper used when preparing posts for scheduling.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = out_dir / "instagram_post.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(post_text)
        if image_path:
            f.write(f"\n[image]={image_path}\n")
    return filename

def move_content(platform: str):
    src_dir = CONTENT_DIR / platform
    dst_dir = SCHEDULER_READY / platform
    dst_dir.mkdir(parents=True, exist_ok=True)
    for file in src_dir.glob("*.md"):
        out_path = dst_dir / file.name.replace(".md", "_ready.txt")
        with open(file, "r", encoding="utf-8") as fin, open(out_path, "w", encoding="utf-8") as fout:
            fout.write(fin.read())
        print(f"✓ {platform.title()} post ready: {out_path}")

def main():
    for platform in ["blog", "instagram", "youtube"]:
        move_content(platform)

if __name__ == "__main__":
    main()
