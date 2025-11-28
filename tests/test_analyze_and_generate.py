import subprocess
from pathlib import Path


def test_analyze_generates_summary():
    """Run analyze.py and ensure all_analysis.json is created."""
    cmd = ["python3", "content-system/system/analyze.py"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    summary = Path("content-system/analysis/all_analysis.json")
    assert summary.exists()


def test_generate_creates_content():
    """Run generate_content.py and ensure output files are created for sample_text."""
    cmd = ["python3", "content-system/system/generate_content.py"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    blog_file = Path("content-system/content/blog/sample_text.md")
    insta_file = Path("content-system/content/instagram/sample_text.md")
    yt_file = Path("content-system/content/youtube/sample_text.md")
    assert blog_file.exists()
    assert insta_file.exists()
    assert yt_file.exists()
