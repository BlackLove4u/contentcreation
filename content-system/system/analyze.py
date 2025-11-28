"""analyze.py
Simple analysis stubs: tags, trend scoring.
"""

import json
from typing import List


def extract_tags(text: str) -> List[str]:
    # naive split by words > 5 chars
    words = [w.strip(".,!?()[]") for w in text.split()]
    tags = list({w.lower() for w in words if len(w) > 5})
    return tags


def score_trend(tags: List[str]) -> dict:
    return {t: 1.0 for t in tags}


def save_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


if __name__ == "__main__":
    sample = (
        "This sample contains datadriven, trending, "
        "exampleword content for analysis."
    )
    tags = extract_tags(sample)
    print(tags)
    print(score_trend(tags))
