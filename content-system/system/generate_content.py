"""generate_content.py
Generate multi-platform content (blog, Instagram, YouTube, etc.) from analysis results and config.

Adds simple YAML front matter for blog posts and includes platform-specific formatting.
"""

import json
from pathlib import Path
import yaml
from datetime import datetime, timezone
import re

ANALYSIS_DIR = Path(__file__).parent.parent / "analysis"
CONTENT_DIR = Path(__file__).parent.parent / "content"
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)
    return {}


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "post"


def front_matter(title: str, tags: list, pillar: str, brand: dict | None = None) -> str:
    meta = {
        "title": title,
        "date": datetime.now(timezone.utc).isoformat() + "Z",
        "tags": tags,
        "pillar": pillar,
    }
    if brand:
        meta["brand"] = brand.get("name")
    return "---\n" + yaml.safe_dump(meta, sort_keys=False) + "---\n\n"


def make_blog(title: str, bullets: list, tags: list, pillar: str, brand=None) -> str:
    body = front_matter(title, tags, pillar, brand)
    body += f"# {title}\n\n"
    if brand:
        body += f"*A {brand['name']} original*\n\n"
    if bullets:
        body += "\n".join([f"- {b}" for b in bullets]) + "\n"
    else:
        body += "Write your article here.\n"
    return body


def make_instagram_caption(tags: list, pillar: str, brand=None) -> str:
    base = f"{pillar.title()} | " if pillar else ""
    caption = base + " ".join([f"#{t}" for t in tags[:10]])
    caption += "\n\n"
    caption += "Short caption text goes here."
    if brand:
        caption += f"\nFollow @{brand['name'].replace(' ', '').lower()} for more!"
    return caption


def make_youtube_desc(tags: list, brand=None) -> str:
    desc = "This video covers: " + ", ".join(tags[:10])
    desc += "\n\nMore resources and links in the description."
    if brand:
        desc += f"\nSubscribe for more {brand['name']} content!"
    return desc


def generate_for_file(analysis, brand):
    title = analysis['filename'].replace('_', ' ').replace('.txt', '').title()
    tags = analysis.get('tags', [])
    pillar = analysis.get('pillar', '')
    bullets = tags[:7]
    # Blog
    blog = make_blog(title, bullets, tags, pillar, brand)
    # Instagram
    insta = make_instagram_caption(tags, pillar, brand)
    # YouTube
    yt = make_youtube_desc(tags, brand)
    return {
        "blog": blog,
        "instagram": insta,
        "youtube": yt,
    }


def save_content(content, out_dir, filename):
    out_dir = Path(out_dir)
    for platform, text in content.items():
        if platform == "blog":
            out_path = out_dir / "blog" / filename
        elif platform == "instagram":
            out_path = out_dir / "instagram" / filename
        elif platform == "youtube":
            out_path = out_dir / "youtube" / filename
        else:
            out_path = out_dir / platform / filename
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)


def main():
    brand = load_config().get("brand", {})
    with open(ANALYSIS_DIR / "all_analysis.json") as f:
        analyses = json.load(f)
    for analysis in analyses:
        content = generate_for_file(analysis, brand)
        filename = analysis['filename'].replace('.txt', '.md')
        save_content(content, CONTENT_DIR, filename)
        print(f"✓ Generated content for {analysis['filename']}")


if __name__ == "__main__":
    main()
