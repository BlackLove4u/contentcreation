"""file_manager.py
Small helpers to move/copy files between pipeline stages.
"""

import shutil
from pathlib import Path


def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def copy(src: str, dst: str):
    ensure_dir(dst)
    shutil.copy(src, dst)


if __name__ == "__main__":
    ensure_dir("../extracted/text/")
    print("ensured dir")
