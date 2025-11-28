"""generate_content.py
Generate multi-platform content (blog, Instagram, YouTube, etc.) from analysis results and config.
"""

import json
from pathlib import Path
import yaml

ANALYSIS_DIR = Path(__file__).parent.parent / "analysis"
CONTENT_DIR = Path(__file__).parent.parent / "content"
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)
    return {}

def make_blog(title: str, bullets: list, brand=None) -> str:
    intro = f"# {title}\n\n"
    if brand:
        intro += f"*A {brand['name']} original*\n\n"
    for b in bullets:
        intro += f"- {b}\n"
    return intro

def make_instagram_caption(tags: list, pillar: str, brand=None) -> str:
    base = f"{pillar.title()} | " if pillar else ""
    caption = base + " ".join([f"#{t}" for t in tags[:5]])
    if brand:
        caption += f"\nFollow @{brand['name'].replace(' ', '').lower()} for more!"
    return caption

def make_youtube_desc(tags: list, brand=None) -> str:
    desc = "This video covers: " + ", ".join(tags[:7])
    if brand:
        desc += f"\nSubscribe for more {brand['name']} content!"
    return desc

def generate_for_file(analysis, brand):
    title = analysis['filename'].replace('_', ' ').replace('.txt', '').title()
    tags = analysis['tags']
    pillar = analysis['pillar']
    # Blog
    blog = make_blog(title, tags[:7], brand)
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
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for platform, text in content.items():
        out_path = Path(out_dir) / platform / filename
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)

def main():
    brand = load_config().get("brand", {})
    with open(ANALYSIS_DIR / "all_analysis.json") as f:
        analyses = json.load(f)
    for analysis in analyses:
        content = generate_for_file(analysis, brand)
        save_content(content, CONTENT_DIR, analysis['filename'].replace('.txt', '.md'))
        print(f"✓ Generated content for {analysis['filename']}")

if __name__ == "__main__":
    main()
