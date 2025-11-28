# Content Automation System

A comprehensive content automation pipeline that ingests text, audio, and video files, extracts metadata and transcripts, analyzes content, generates multi-platform content, and prepares scheduler-ready outputs.

## Features

- **Multi-format Ingestion**: Automatically detect and ingest text (`.txt`, `.md`, `.html`), audio (`.mp3`, `.wav`, `.m4a`), and video (`.mp4`, `.mov`, `.avi`, `.mkv`) files
- **Audio/Video Extraction**: Extract metadata and audio from video files using `ffmpeg` (optional)
- **Intelligent Transcription**: Supports multiple transcription backends with automatic fallback:
  - OpenAI Whisper API (cloud-based, requires API key)
  - Local Whisper model (requires `openai-whisper` package and `ffmpeg`)
  - Graceful placeholder fallback if transcription unavailable
- **Content Analysis**: Extract tags, categorize content by brand pillars, generate trend scores
- **Multi-Platform Content Generation**: Automatically create formatted content for:
  - Blog posts (with YAML front matter)
  - Instagram captions
  - YouTube descriptions
  - Additional platforms (extensible)
- **Scheduler-Ready Output**: Prepare content for social media schedulers with platform-specific formatting
- **Robust Error Handling**: Automatic retries with exponential backoff for external API calls and file operations
- **Dry-Run Mode**: Test the pipeline without writing files
- **Archival & Metadata**: Timestamp-based run directories with JSON metadata tracking

## Quick Start

### 1. Setup Environment

```bash
# Clone and navigate to the project
cd /workspaces/contentcreation

# Create virtual environment (if not already created)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure (Optional)

Edit `content-system/config.yaml` to customize brand information and pipeline settings:

```yaml
brand:
  name: Your Brand Name
  mission: Your mission statement
  pillars:
    - Pillar 1
    - Pillar 2
```

### 3. Add Content

Place files in `content-system/input/uploads/`:

```bash
# Example
cp your_article.txt content-system/input/uploads/
cp your_podcast.mp3 content-system/input/uploads/
cp your_video.mp4 content-system/input/uploads/
```

### 4. Run Pipeline

**Option A: Full pipeline with dry-run (preview changes)**

```bash
python3 content-system/system/ingest_uploads.py --dry-run --verbose
```

**Option B: Full pipeline (process files and archive)**

```bash
python3 content-system/system/ingest_uploads.py --verbose --commit
```

**Option C: Run individual stages**

```bash
# Analyze extracted content
python3 content-system/system/analyze.py

# Generate multi-platform content
python3 content-system/system/generate_content.py

# Prepare for schedulers
python3 content-system/system/scheduler_prep.py
```

### 5. Check Output

- **Extracted content**: `content-system/extracted/` (text, transcripts, cleaned video)
- **Analysis results**: `content-system/analysis/` (JSON files with tags and pillar categorization)
- **Generated content**: `content-system/content/` (blog posts, Instagram captions, YouTube descriptions)
- **Scheduler-ready**: `content-system/scheduler_ready/` (platform-specific formatted files)
- **Processed archive**: `content-system/input/processed/` (timestamped runs with metadata)

## Configuration

### Transcription Setup

The system supports multiple transcription backends. To configure:

```bash
# Check current transcription environment
python3 content-system/system/setup_transcription.py

# Install Python transcription packages
python3 content-system/system/setup_transcription.py --install openai whisper

# Install system packages (Debian/Ubuntu)
python3 content-system/system/setup_transcription.py --install-system
```

### OpenAI API (Cloud Transcription)

For cloud-based transcription using OpenAI Whisper:

1. Sign up at [OpenAI](https://platform.openai.com)
2. Get an API key
3. Set environment variable:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
4. Install the package:
   ```bash
   pip install openai
   ```

### Local Transcription

For privacy-focused local transcription:

1. Install system dependencies:
   ```bash
   # On Debian/Ubuntu
   sudo apt update && sudo apt install ffmpeg
   
   # On macOS (with Homebrew)
   brew install ffmpeg
   ```

2. Install Python package:
   ```bash
   pip install openai-whisper
   ```

3. First run will download the model (~140MB for "small" model, or ~1.5GB for "base" model)

## Pipeline Stages

### Stage 1: Ingestion (`ingest_uploads.py`)

Scans `content-system/input/uploads/` and routes files to extractors:
- **Text files** → copied to `extracted/text/`
- **Audio files** → copied to `extracted/transcripts/` + metadata extraction
- **Video files** → copied to `extracted/cleaned/` + metadata extraction

**Options:**
- `--dry-run`: Preview actions without writing
- `--verbose`: Detailed logging
- `--commit`: Archive processed files with metadata

### Stage 2: Extraction

#### Audio Extraction (`extract_audio.py`)
- Extracts metadata (file size, duration)
- Transcribes audio using configured backend
- Supports retry with exponential backoff

#### Video Extraction (`extract_video.py`)
- Extracts metadata
- Extracts audio using `ffmpeg` (if available)
- Transcribes audio via audio extraction pipeline

### Stage 3: Analysis (`analyze.py`)

Analyzes extracted text files:
- Extracts tags and keywords
- Categorizes content by brand pillars
- Calculates trend scores
- Generates JSON analysis files
- Outputs comprehensive `analysis/all_analysis.json`

### Stage 4: Content Generation (`generate_content.py`)

Generates multi-platform content from analysis:
- **Blog posts**: Markdown with YAML front matter (title, date, tags, pillar)
- **Instagram captions**: Formatted for character limits with hashtags
- **YouTube descriptions**: With video metadata
- Extensible template system for additional platforms

### Stage 5: Scheduler Prep (`scheduler_prep.py`)

Prepares content for social media schedulers:
- Copies generated content to `scheduler_ready/` platform directories
- Formats as `_ready.txt` files with platform-specific structure
- Ready to paste into scheduling tools (Buffer, Hootsuite, etc.)

## CLI Reference

### ingest_uploads.py

```bash
python3 content-system/system/ingest_uploads.py [OPTIONS]

Options:
  --dry-run          Show actions without writing files
  --verbose          Enable debug logging
  --commit           Archive processed files to input/processed/TIMESTAMP/
```

### extract_audio.py

```bash
python3 content-system/system/extract_audio.py --audio FILE [OPTIONS]

Options:
  --audio FILE       Path to audio file (required)
  --out DIR          Output directory for metadata/transcripts
  --transcribe       Enable transcription
```

### extract_video.py

```bash
python3 content-system/system/extract_video.py --video FILE [OPTIONS]

Options:
  --video FILE       Path to video file (required)
  --out DIR          Output directory
  --transcribe       Enable transcription
```

### analyze.py

```bash
python3 content-system/system/analyze.py
# Analyzes all files in extracted/text/
```

### generate_content.py

```bash
python3 content-system/system/generate_content.py
# Generates content for all analyzed files
```

### scheduler_prep.py

```bash
python3 content-system/system/scheduler_prep.py
# Prepares all generated content for schedulers
```

### setup_transcription.py

```bash
python3 content-system/system/setup_transcription.py [OPTIONS]

Options:
  --install PKG      Install Python packages (openai, whisper)
  --install-system   Install ffmpeg via apt-get (Debian/Ubuntu)
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ingest_dryrun.py -v

# Run with coverage
pytest tests/ --cov=content-system/system
```

### Code Quality

```bash
# Format code
black content-system/system/ tests/

# Lint
flake8 content-system/system/ tests/
ruff check content-system/system/ tests/

# Type checking (if mypy is installed)
mypy content-system/system/ tests/
```

### Project Structure

```
content-system/
├── config.yaml                  # Brand and pipeline configuration
├── README.md                    # Pipeline documentation
├── TRANSCRIPTION.md             # Transcription setup guide
├── input/
│   ├── uploads/                 # Drop folder for new content
│   └── processed/               # Timestamped archives of processed runs
├── extracted/
│   ├── text/                    # Extracted text files
│   ├── transcripts/             # Audio files and transcripts
│   └── cleaned/                 # Extracted video metadata
├── analysis/
│   ├── all_analysis.json        # Comprehensive analysis summary
│   └── approved/                # Curated analysis results
├── content/
│   ├── blog/                    # Generated blog posts
│   ├── instagram/               # Generated Instagram captions
│   ├── youtube/                 # Generated YouTube descriptions
│   └── ...                      # Other platforms
├── scheduler_ready/
│   ├── blog/                    # Scheduler-ready blog posts
│   ├── instagram/               # Scheduler-ready Instagram posts
│   ├── youtube/                 # Scheduler-ready YouTube posts
│   └── ...                      # Other platforms
└── system/
    ├── main.py                  # Main orchestration entry point
    ├── ingest_uploads.py        # Ingestion and routing
    ├── extract_audio.py         # Audio extraction and transcription
    ├── extract_video.py         # Video extraction
    ├── analyze.py               # Content analysis
    ├── generate_content.py      # Multi-platform generation
    ├── scheduler_prep.py        # Scheduler preparation
    ├── setup_transcription.py   # Dependency setup helper
    ├── file_manager.py          # File utilities
    ├── clean_text.py            # Text cleaning utilities
    └── __pycache__/
```

## Troubleshooting

### Audio/Video Processing Issues

**"ffmpeg not found"**
- Install ffmpeg: `sudo apt install ffmpeg` (Linux) or `brew install ffmpeg` (macOS)
- Verify: `which ffmpeg`

**"Transcription unavailable"**
- Check environment: `python3 content-system/system/setup_transcription.py`
- Either:
  - Set `OPENAI_API_KEY` and install `openai` package
  - Or install `openai-whisper` and `ffmpeg`

**"Module not found" errors**
- Ensure virtual environment is activated: `source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### Pipeline Hangs

- Check for large files in `input/uploads/` (transcription can be slow)
- Use `--dry-run` first to preview: `python3 content-system/system/ingest_uploads.py --dry-run`
- Run stages individually rather than full pipeline

### File Permission Errors

- Ensure write permissions: `chmod -R 755 content-system/`
- If archiving fails with `--commit`, check disk space

## Advanced Usage

### Custom Brand Pillars

Edit `content-system/config.yaml`:

```yaml
brand:
  name: My Brand
  pillars:
    - Education
    - Inspiration
    - Community
```

Analysis automatically categorizes content into these pillars.

### Extending Content Formats

Add new platform generation in `content-system/system/generate_content.py`:

```python
def make_tiktok(title: str, bullets: list, tags: list) -> str:
    # Your TikTok formatting logic
    return formatted_content

# In save_content():
for analysis in analyses:
    tiktok_content = make_tiktok(...)
    (CONTENT_DIR / "tiktok" / f"{stem}.txt").write_text(tiktok_content)
```

Then run `scheduler_prep.py` to move to scheduler_ready/.

### Batch Processing

Process multiple uploads folder runs:

```bash
# Run 1
python3 content-system/system/ingest_uploads.py --verbose --commit

# Check output
ls content-system/input/processed/

# Run 2 (add more files to uploads/ first)
python3 content-system/system/ingest_uploads.py --verbose --commit
```

Each run gets a unique timestamp directory with metadata.

## Performance Notes

- **First whisper run**: ~5-10 min (downloads ~140MB model)
- **Local transcription**: 1-2 min per 10 min audio
- **Cloud transcription (OpenAI)**: 30-60 sec per 10 min audio
- **Pipeline end-to-end**: ~2 min (with local transcription, excluding network time)

## Support & Contributing

For issues or improvements:

1. Check `content-system/TRANSCRIPTION.md` for setup issues
2. Review test cases in `tests/` for usage examples
3. Run test suite to validate changes: `pytest tests/ -v`

## License

[Add your license here]

---

**Ready to automate your content?** Start with `python3 content-system/system/ingest_uploads.py --dry-run --verbose` to preview the pipeline!
