"""extract_web.py
Extract article text from web URLs using requests and BeautifulSoup.
"""

import argparse
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def extract(url: str, out_dir: str) -> Optional[str]:
    """
    Extract article text from url and save to out_dir.

    Args:
        url: URL to fetch and extract
        out_dir: Directory to save extracted text

    Returns:
        Path to saved file, or None if extraction failed
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract text from paragraphs
        paragraphs = soup.find_all("p")
        text = "\n".join([p.get_text(strip=True) for p in paragraphs])

        if not text:
            # Fallback: get all text
            text = soup.get_text(separator="\n", strip=True)

        # Save to file
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        parsed = urlparse(url)
        filename = (
            parsed.netloc.replace("www.", "").replace(".", "_")
            + "_content.txt"
        )
        out_path = os.path.join(out_dir, filename)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"✓ Extracted to {out_path}")
        return out_path

    except Exception as e:
        print(f"✗ Error extracting {url}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Extract web articles")
    parser.add_argument("--url", required=True, help="URL to extract")
    parser.add_argument(
        "--out",
        default="../extracted/text/",
        help="Output directory",
    )
    args = parser.parse_args()
    extract(args.url, args.out)


if __name__ == "__main__":
    main()
