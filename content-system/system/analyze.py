"""analyze.py
Analyze all extracted text files, categorize by brand pillars, and output metadata.
"""

import json
from typing import List, Dict
from pathlib import Path
import yaml
import re

EXTRACTED_TEXT = Path(__file__).parent.parent / "extracted" / "text"
ANALYSIS_DIR = Path(__file__).parent.parent / "analysis"
PILLARS = []

def load_config():
    global PILLARS
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            PILLARS.extend([p.lower() for p in config.get("brand", {}).get("pillars", [])])

def extract_tags(text: str) -> List[str]:
    # naive split by words > 5 chars
    words = [w.strip(".,!?()[]") for w in text.split()]
    tags = list({w.lower() for w in words if len(w) > 5})
    return tags

def score_trend(tags: List[str]) -> dict:
    return {t: 1.0 for t in tags}

def categorize_pillar(text: str) -> str:
    # Simple keyword match to pillar
    for pillar in PILLARS:
        if re.search(pillar.split()[0], text, re.IGNORECASE):
            return pillar
    return "uncategorized"

def analyze_file(filepath: Path) -> Dict:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    tags = extract_tags(text)
    trend = score_trend(tags)
    pillar = categorize_pillar(text)
    return {
        "filename": filepath.name,
        "pillar": pillar,
        "tags": tags,
        "trend_scores": trend,
        "length": len(text),
    }

def save_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)

def main():
    load_config()
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    all_results = []
    for file in EXTRACTED_TEXT.glob("*.txt"):
        result = analyze_file(file)
        all_results.append(result)
        out_path = ANALYSIS_DIR / f"{file.stem}_analysis.json"
        save_json(result, out_path)
        print(f"✓ Analyzed {file.name} -> {out_path.name}")
    # Save summary
    save_json(all_results, ANALYSIS_DIR / "all_analysis.json")

if __name__ == "__main__":
    main()
