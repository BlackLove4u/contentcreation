import os
import yaml
from pathlib import Path


CONTENT_DIR = Path("content-system/content")
SCHEDULER_DIR = Path("content-system/scheduler_ready")


def _read_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_blog_front_matter_exists_and_valid():
    blog_dir = CONTENT_DIR / "blog"
    assert blog_dir.exists(), "Content blog directory missing"
    md_files = list(blog_dir.glob("*.md"))
    assert md_files, "No blog markdown files found"

    required_keys = {"title", "date", "tags", "pillar"}
    for md in md_files:
        txt = _read_file(md)
        assert txt.startswith("---"), f"Missing YAML front matter in {md}"
        parts = txt.split("---")
        assert len(parts) > 2, f"Invalid front matter format in {md}"
        fm_raw = parts[1]
        try:
            fm = yaml.safe_load(fm_raw)
        except Exception as e:
            raise AssertionError(f"YAML parse error in {md}: {e}")
        assert required_keys.issubset(set(fm.keys())), f"Front matter missing keys in {md}: {fm.keys()}"


def test_scheduler_ready_files_exist():
    assert SCHEDULER_DIR.exists(), "scheduler_ready directory missing"
    platforms = [p for p in SCHEDULER_DIR.iterdir() if p.is_dir()]
    assert platforms, "No platform folders in scheduler_ready"
    found_any = False
    for p in platforms:
        files = list(p.glob("*_ready.txt"))
        if files:
            found_any = True
    assert found_any, "No scheduler-ready files found in any platform folder"
