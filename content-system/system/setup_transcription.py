"""Helper for checking and optionally installing transcription dependencies.

Usage:
  python3 setup_transcription.py         # prints checks and instructions
  python3 setup_transcription.py --install openai whisper ffmpeg
  python3 setup_transcription.py --install-system  # attempts sudo apt-get for ffmpeg

Note: Installing whisper and ffmpeg may require large downloads or system packages.
System-level installation (apt-get) requires sudo and only works on Debian/Ubuntu.
"""

import argparse
import platform
import shutil
import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def check_openai():
    try:
        import openai  # noqa: F401
        return True
    except Exception:
        return False


def check_whisper():
    try:
        import whisper  # noqa: F401
        return True
    except Exception:
        return False


def check_ffmpeg():
    return shutil.which("ffmpeg") is not None


def detect_system():
    """Detect OS and package manager."""
    system = platform.system()
    if system == "Linux":
        try:
            with open("/etc/os-release") as f:
                content = f.read().lower()
                if "ubuntu" in content or "debian" in content:
                    return "debian"
        except Exception:
            pass
    return None


def install_ffmpeg_apt():
    """Attempt to install ffmpeg via apt-get (Debian/Ubuntu)."""
    system = detect_system()
    if system != "debian":
        logger.error("System package installation only supported on Debian/Ubuntu.")
        return False
    
    try:
        logger.info("Attempting to install ffmpeg via apt...")
        subprocess.run(["sudo", "apt", "update"], check=False)
        subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)
        logger.info("✓ ffmpeg installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install ffmpeg via apt: {e}")
        return False
    except Exception as e:
        logger.error(f"Error during apt installation: {e}")
        return False


def run_pip_install(packages):
    """Install Python packages via pip."""
    cmd = [sys.executable, "-m", "pip", "install"] + packages
    logger.info("Running: " + " ".join(cmd))
    try:
        subprocess.check_call(cmd)
        logger.info("✓ Python packages installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install Python packages: {e}")
        raise


def print_status_report(has_openai, has_whisper, has_ffmpeg, has_key):
    """Print human-readable status report."""
    print("\n" + "="*60)
    print("TRANSCRIPTION ENVIRONMENT CHECK")
    print("="*60)
    print(f"  openai package installed:     {_status_icon(has_openai)} {has_openai}")
    print(f"  whisper package installed:    {_status_icon(has_whisper)} {has_whisper}")
    print(f"  ffmpeg on PATH:               {_status_icon(has_ffmpeg)} {has_ffmpeg}")
    print(f"  OPENAI_API_KEY environment:   {_status_icon(has_key)} {has_key}")
    print("="*60)


def _status_icon(status):
    return "✓" if status else "✗"


def print_recommendations(has_openai, has_whisper, has_ffmpeg, has_key):
    """Print installation recommendations."""
    print("\nRECOMMENDATIONS:")
    
    if has_openai and has_key:
        print("  ✓ OpenAI cloud transcription is ready!")
    elif not has_openai:
        print("  - To enable OpenAI transcription: install openai package and set OPENAI_API_KEY")
    else:
        print("  - OPENAI_API_KEY not set; set it to enable cloud transcription")
    
    if has_whisper and has_ffmpeg:
        print("  ✓ Local transcription (whisper) is ready!")
    elif not has_whisper:
        print("  - To enable local transcription: install whisper (openai-whisper package)")
    elif not has_ffmpeg:
        print("  - ffmpeg required for local transcription; install via: sudo apt install ffmpeg")
    
    if not (has_openai and has_key) and not (has_whisper and has_ffmpeg):
        print("\n  ⚠ NO TRANSCRIPTION METHOD AVAILABLE!")
        print("    Transcription will write placeholder text unless you install dependencies.")


def main():
    parser = argparse.ArgumentParser(description="Check and install transcription dependencies")
    parser.add_argument("--install", nargs="*", help="Install packages (openai, whisper)")
    parser.add_argument("--install-system", action="store_true", help="Install ffmpeg via apt-get (Debian/Ubuntu only)")
    args = parser.parse_args()

    # Check current status
    has_openai = check_openai()
    has_whisper = check_whisper()
    has_ffmpeg = check_ffmpeg()
    has_key = bool(os.getenv("OPENAI_API_KEY"))

    # Print status
    print_status_report(has_openai, has_whisper, has_ffmpeg, has_key)

    # Handle installations
    if args.install_system:
        if install_ffmpeg_apt():
            has_ffmpeg = check_ffmpeg()
        print_status_report(has_openai, has_whisper, has_ffmpeg, has_key)

    if args.install:
        to_install = []
        for p in args.install:
            if p == "openai":
                to_install.append("openai")
            elif p == "whisper":
                to_install.append("openai-whisper")
            else:
                to_install.append(p)
        
        if to_install:
            try:
                run_pip_install(to_install)
                # Re-check status
                has_openai = check_openai()
                has_whisper = check_whisper()
                print_status_report(has_openai, has_whisper, has_ffmpeg, has_key)
            except Exception as e:
                logger.error(f"Installation failed: {e}")
                sys.exit(1)

    # Print recommendations
    print_recommendations(has_openai, has_whisper, has_ffmpeg, has_key)
    print()


if __name__ == "__main__":
    main()
