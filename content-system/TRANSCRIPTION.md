Transcription setup and operational notes

This document explains how to enable and run transcription for audio/video files in the content-system pipeline.

Options

1) OpenAI Whisper (cloud)
   - Install: `pip install openai`
   - Set API key: `export OPENAI_API_KEY="sk-..."`
   - Notes: Uses the OpenAI Whisper API (model `whisper-1`). Costs and quotas apply. This is the simplest option if you have an API key.

2) Local Whisper (Python)
   - Install: `pip install -U openai-whisper` or `pip install -U whisper` (package name may vary by distribution)
   - Requirements: `ffmpeg` must be installed and available on PATH. On Ubuntu: `sudo apt update && sudo apt install -y ffmpeg`.
   - Notes: Local models can be large and require GPU for best performance. The helper script can attempt to install Python packages but will not configure GPUs.

3) whisper.cpp or other local C++ runtimes
   - Useful for CPU-only local deployments (especially on Apple Silicon). See their respective project docs for model downloads and usage.

Helper script

A helper script `content-system/system/setup_transcription.py` is provided to:

- Check whether `openai` or `whisper` packages are installed.
- Check for `OPENAI_API_KEY` in the environment.
- Check that `ffmpeg` is available.
- Optionally run `pip install` for the requested packages (pass `--install`).

Security

- Keep API keys secret. Do not commit them to source control.
- If using local Whisper, download models from trusted sources.

Switching behavior in the pipeline

- `extract_audio.py` will prefer OpenAI (if `openai` installed and `OPENAI_API_KEY` present), otherwise fallback to the local `whisper` package, otherwise write a placeholder transcript.
- `extract_video.py` extracts audio (using `ffmpeg`) and then delegates to the audio transcription flow.

If you want, I can extend the helper to automatically download a chosen Whisper model, or add instructions and automation for whisper.cpp model downloads.
