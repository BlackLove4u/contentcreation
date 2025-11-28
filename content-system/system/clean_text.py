"""clean_text.py
Text cleaning utilities for the content pipeline.
"""

import re


def clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text


if __name__ == "__main__":
    sample = "This   is   messy\n\nText."
    print(clean(sample))
