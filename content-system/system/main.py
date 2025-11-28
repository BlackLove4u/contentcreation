"""main.py
Entry point to run the pipeline step-by-step.
"""

import argparse
import subprocess


def main():
    parser = argparse.ArgumentParser(
        description="Run content-system pipeline orchestrator"
    )
    parser.add_argument(
        "--step",
        choices=[
            "ingest",
            "analyze",
            "generate",
            "prep",
            "full",
        ],
        help="Pipeline step to run (or 'full' for all steps)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without making changes",
    )
    args = parser.parse_args()

    def run_script(script, extra_args=None):
        cmd = ["python3", f"system/{script}"]
        if extra_args:
            cmd += extra_args
        print(f"Running: {' '.join(cmd)}")
        if not args.dry_run:
            subprocess.run(cmd)

    if args.step == "ingest":
        run_script("ingest_uploads.py")
    elif args.step == "analyze":
        run_script("analyze.py")
    elif args.step == "generate":
        run_script("generate_content.py")
    elif args.step == "prep":
        run_script("scheduler_prep.py")
    elif args.step == "full":
        run_script("ingest_uploads.py")
        run_script("analyze.py")
        run_script("generate_content.py")
        run_script("scheduler_prep.py")
    else:
        print("No valid step provided. Use --step with one of: ingest, analyze, generate, prep, full.")


if __name__ == "__main__":
    main()
