"""extract_web.py
Simple web extraction stubs for content-system.
"""
import argparse


def extract(url: str, out_dir: str):
    """Placeholder: extract article text from `url` and save to out_dir."""
    print(f"(stub) extracting {url} -> {out_dir}")


def main():
    parser = argparse.ArgumentParser(description="Extract web articles")
    parser.add_argument("--url", help="URL to extract")
    parser.add_argument("--out", default="../extracted/text/", help="Output directory")
    args = parser.parse_args()
    extract(args.url, args.out)


if __name__ == "__main__":
    main()
