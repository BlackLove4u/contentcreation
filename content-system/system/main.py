"""main.py
Entry point to run the pipeline step-by-step.
"""
import argparse
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Run content-system pipeline steps")
    parser.add_argument("--step", choices=["extract_web","extract_video","pdf","clean","analyze","generate","prep"], help="Pipeline step to run")
    args = parser.parse_args()
    print(f"Requested step: {args.step}")
    # This is a dispatcher to call the module scripts (stubs)
    if args.step == "extract_web":
        subprocess.run(["python3", "system/extract_web.py", "--url", "https://example.com/article-1"]) 


if __name__ == "__main__":
    main()
