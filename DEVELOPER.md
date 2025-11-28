# Developer Guide

This guide covers architecture, extending the pipeline, testing, and contributing to the content automation system.

## Architecture Overview

The content automation pipeline follows a modular, stage-based architecture:

```
INPUT (uploads/) 
    ↓
INGEST (detect & route by type)
    ├── Text → extract/text/
    ├── Audio → extract/transcripts/ + extract_audio.py
    └── Video → extract/cleaned/ + extract_video.py
    ↓
ANALYZE (extract_audio.py & extract_video.py)
    ├── Metadata extraction
    ├── Transcription (with fallbacks & retry)
    └── Output to extracted/
    ↓
ANALYZE (analyze.py)
    ├── Tag extraction
    ├── Pillar categorization
    └── Output to analysis/*.json
    ↓
GENERATE (generate_content.py)
    ├── Blog posts (with YAML front matter)
    ├── Instagram captions
    ├── YouTube descriptions
    └── Output to content/*/
    ↓
PREP (scheduler_prep.py)
    └── Move to scheduler_ready/ platform dirs
    ↓
OUTPUT (scheduler_ready/)
```

## Module Reference

### ingest_uploads.py

**Purpose**: Entry point for the pipeline. Detects file types and routes to extractors.

**Key Functions**:
- `detect_type(filepath)`: Returns "text", "audio", "video", or "unknown"
- `process_file(filepath, dry_run, logger)`: Routes file to appropriate extractor
- `main()`: CLI entry point with argparse

**Extensibility**:
- Add new file types to `detect_type()`
- Add new routing logic in `process_file()`
- New extractors can be called as subprocesses

### extract_audio.py

**Purpose**: Extract metadata and transcribe audio files.

**Key Functions**:
- `retry_on_exception(max_retries, initial_delay, backoff_factor)`: Decorator for retry logic
- `extract_metadata(audio_path, out_dir)`: Get file metadata
- `transcribe_with_openai(audio_path)`: Use OpenAI Whisper API
- `transcribe_with_whisper_local(audio_path)`: Use local whisper model
- `transcribe(audio_path, out_dir)`: Main entry point with fallback chain

**Fallback Chain**:
1. Try OpenAI Whisper API (if `openai` installed and `OPENAI_API_KEY` set)
2. Try local whisper model (if `whisper` installed and `ffmpeg` available)
3. Write placeholder transcript

**Retry Logic**:
- OpenAI: 3 retries with 2s initial delay, 2x backoff
- Whisper: 2 retries with 1s initial delay, 2x backoff
- All retries log warnings with attempt counts

**Extensibility**:
- Add new transcriber by creating `transcribe_with_X()` function
- Add to fallback chain in `transcribe()`
- Wrap with `@retry_on_exception()` decorator

### extract_video.py

**Purpose**: Extract metadata, audio, and transcribe video files.

**Key Functions**:
- `extract_metadata(video_path, out_dir)`: Get file metadata
- `extract_audio_from_video(video_path, out_dir)`: Use ffmpeg to extract audio WAV
- `main()`: CLI entry point with transcription support

**Implementation Notes**:
- Handles both relative (`from . import`) and standalone (`sys.path.insert`) imports
- Uses `subprocess` to call `ffmpeg` with specific encoding (PCM 16-bit, 16kHz mono)
- Delegates audio transcription to `extract_audio.transcribe()`
- Graceful fallback if ffmpeg unavailable

**Extensibility**:
- Add metadata fields in `extract_metadata()`
- Replace ffmpeg with alternative audio extraction (e.g., `moviepy`)
- Call different transcription pipeline

### analyze.py

**Purpose**: Analyze extracted text and generate analysis metadata.

**Key Functions**:
- `load_config()`: Load brand config from YAML
- `extract_tags(text)`: Simple keyword extraction (configurable)
- `score_trend(tags)`: Calculate trend scores
- `categorize_pillar(text)`: Categorize into brand pillars
- `analyze_file(filepath)`: Main analysis logic
- `save_json(obj, path)`: Save analysis to JSON

**Analysis Output** (`analysis/FILE_analysis.json`):
```json
{
  "file": "example.txt",
  "tags": ["tag1", "tag2"],
  "pillar": "pillar_name",
  "summary_analysis": {
    "trend_score": 0.75,
    "key_themes": ["theme1", "theme2"]
  }
}
```

**Extensibility**:
- Enhance `extract_tags()` with NLP (spacy, NLTK, transformers)
- Improve `categorize_pillar()` with ML classification
- Add new analysis metrics (sentiment, readability, etc.)

### generate_content.py

**Purpose**: Generate multi-platform content from analysis results.

**Key Functions**:
- `load_config()`: Load brand configuration
- `slugify(s)`: Create URL-safe slugs from titles
- `front_matter(title, tags, pillar, brand)`: Create YAML front matter
- `make_blog(title, bullets, tags, pillar, brand)`: Generate blog post
- `make_instagram_caption(...)`: Generate Instagram caption
- `make_youtube_desc(...)`: Generate YouTube description
- `save_content(platform, filename, content)`: Save to platform-specific dir

**Template System**:

Each platform has a dedicated generation function:

```python
def make_PLATFORM(title, bullets, tags, pillar, brand=None) -> str:
    # Your formatting logic here
    return formatted_content
```

**YAML Front Matter** (Blog posts only):
```yaml
---
title: Article Title
date: 2025-11-28T12:34:56Z
tags: [tag1, tag2]
pillar: Education
brand: Brand Name
---
```

**Extensibility**:
- Add new platform: Create `make_PLATFORM()` function
- Update `save_content()` to handle new platform directory
- Add tests in `tests/test_content_generation.py`

### scheduler_prep.py

**Purpose**: Prepare generated content for social media schedulers.

**Key Functions**:
- `prepare_for_instagram(content)`: Format for Instagram limits
- `move_content(platform)`: Move from `content/` to `scheduler_ready/`

**Output Format**:

Each file is saved as `{stem}_ready.txt` in platform-specific scheduler_ready directory:

```
scheduler_ready/
├── blog/
│   └── article_ready.txt
├── instagram/
│   └── post_ready.txt
└── youtube/
    └── video_ready.txt
```

**Extensibility**:
- Add platform-specific formatting functions (e.g., `prepare_for_tiktok()`)
- Update `move_content()` to call new formatter
- Test with sample content files

## Testing

### Test Structure

```
tests/
├── test_ingest_dryrun.py          # Integration: ingest with --dry-run
├── test_analyze_and_generate.py   # Integration: analyze → generate
└── test_content_generation.py     # Unit: YAML front matter, scheduler files
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Single file
pytest tests/test_ingest_dryrun.py -v

# With coverage
pytest tests/ --cov=content-system/system --cov-report=html
```

### Writing Tests

**Example: Test new transcriber**

```python
# tests/test_transcription.py
import pytest
from pathlib import Path
from content_system.system import extract_audio

def test_transcribe_with_new_backend():
    # Create test audio (or use sample)
    audio_path = Path("content-system/extracted/transcripts/test.mp3")
    out_dir = Path("content-system/extracted/transcripts")
    
    # Call transcriber
    extract_audio.transcribe(audio_path, out_dir)
    
    # Verify output
    transcript = out_dir / "test_transcript.txt"
    assert transcript.exists()
    assert len(transcript.read_text()) > 0
```

## Adding Features

### 1. Add a New Content Platform

**Step 1**: Add generator function in `generate_content.py`

```python
def make_tiktok(title: str, bullets: list, tags: list, pillar: str) -> str:
    """Generate TikTok caption (max 150 chars)."""
    caption = f"{title[:20]}..."
    caption += f"\n\n#{pillar.lower()}"
    for tag in tags[:3]:  # Max 3 hashtags
        caption += f" #{tag}"
    return caption[:150]  # Enforce limit
```

**Step 2**: Update `save_content()` to handle TikTok

```python
def save_content(...):
    # ... existing platforms ...
    
    # Add TikTok
    if platform == "tiktok" or True:  # Generate all
        (CONTENT_DIR / "tiktok").mkdir(parents=True, exist_ok=True)
        tiktok_content = make_tiktok(...)
        (CONTENT_DIR / "tiktok" / f"{stem}.txt").write_text(tiktok_content)
```

**Step 3**: Update `scheduler_prep.py`

```python
def move_content(platform):
    # ... existing platforms ...
    
    # Add TikTok
    prepare_tiktok = lambda c: c  # No special formatting needed
    for file in (CONTENT_DIR / "tiktok").glob("*.txt"):
        content = file.read_text()
        content = prepare_tiktok(content)
        out_path = SCHEDULER_READY / "tiktok" / f"{file.stem}_ready.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content)
```

**Step 4**: Add test

```python
def test_tiktok_generation():
    from content_system.system import generate_content
    result = generate_content.make_tiktok("Title", ["bullet"], ["tag"], "pillar")
    assert len(result) <= 150
    assert "#pillar" in result
```

### 2. Add a New Extraction Backend

**For audio/transcription**:

```python
# In extract_audio.py

@retry_on_exception(max_retries=2, initial_delay=1.0)
def _transcribe_custom_with_retry(audio_path: str) -> str:
    """Wrapper for custom transcriber."""
    return transcribe_with_custom(audio_path)

def transcribe_with_custom(audio_path: str) -> Optional[str]:
    """Your custom transcription logic."""
    try:
        # Your implementation
        pass
    except Exception as e:
        logger.error(f"Custom transcription failed: {e}")
        raise
```

Then add to fallback chain in `transcribe()`:

```python
def transcribe(audio_path: str, out_dir: str):
    # ... try OpenAI ...
    # ... try whisper ...
    
    # Try custom backend
    try:
        logger.info(f"Attempting custom transcription...")
        text = _transcribe_custom_with_retry(audio_path)
        if text:
            # ... save and return ...
    except Exception as e:
        logger.warning(f"Custom transcription failed: {e}")
    
    # ... placeholder ...
```

### 3. Add Analysis Enhancements

```python
# In analyze.py

from textblob import TextBlob  # For sentiment
import spacy  # For NLP

def analyze_sentiment(text: str) -> float:
    """Calculate sentiment score (-1.0 to 1.0)."""
    blob = TextBlob(text)
    return blob.sentiment.polarity

def extract_entities(text: str) -> list:
    """Extract named entities using spaCy."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return [ent.text for ent in doc.ents]

def analyze_file(filepath):
    # ... existing analysis ...
    
    # Add sentiment and entities
    analysis["sentiment"] = analyze_sentiment(text)
    analysis["entities"] = extract_entities(text)
    
    # ... save ...
```

## Performance Optimization

### 1. Parallel Processing

For batch operations, use `concurrent.futures`:

```python
from concurrent.futures import ThreadPoolExecutor

def batch_analyze(files):
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(analyze_file, files))
    return results
```

### 2. Caching

Cache expensive operations (e.g., model loading):

```python
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        logger.info("Loading whisper model...")
        import whisper
        _whisper_model = whisper.load_model("small")
    return _whisper_model
```

### 3. Streaming

For large files, stream processing:

```python
def analyze_large_file(filepath, chunk_size=1000):
    """Analyze file in chunks."""
    with open(filepath) as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield analyze_text(chunk)
```

## Debugging

### Enable Debug Logging

```bash
# All Python scripts support logging levels
python3 content-system/system/ingest_uploads.py --verbose

# Or set environment variable
LOGLEVEL=DEBUG python3 content-system/system/analyze.py
```

### Use Dry-Run Mode

```bash
# Preview changes without writing
python3 content-system/system/ingest_uploads.py --dry-run --verbose
```

### Inspect Intermediate Outputs

```bash
# Check analysis files
cat content-system/analysis/all_analysis.json | python3 -m json.tool

# Check extracted content
ls -la content-system/extracted/*/

# Check generated content
ls -la content-system/content/*/
```

## Code Style

### Formatting

```bash
# Auto-format code
black content-system/ tests/

# Check formatting
black --check content-system/ tests/
```

### Linting

```bash
# Run flake8
flake8 content-system/ tests/

# Run ruff
ruff check content-system/ tests/
```

### Type Hints

Use Python 3.10+ syntax:

```python
from typing import Optional

def process_file(path: str, options: dict | None = None) -> bool:
    """Process a file.
    
    Args:
        path: File path
        options: Optional processing options
    
    Returns:
        True if successful
    """
    pass
```

## Common Patterns

### File Operations

```python
from pathlib import Path

# Safe directory creation
output_dir = Path("output")
output_dir.mkdir(parents=True, exist_ok=True)

# Safe file writing
output_file = output_dir / "result.json"
output_file.write_text(json.dumps(data, indent=2))

# Safe file reading
if output_file.exists():
    data = json.loads(output_file.read_text())
```

### Error Handling

```python
import logging

logger = logging.getLogger(__name__)

try:
    # Your operation
    pass
except FileNotFoundError:
    logger.error("File not found")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### Subprocess Calls

```python
import subprocess

try:
    result = subprocess.run(
        ["command", "arg1", "arg2"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    logger.info(f"Success: {result.stdout}")
except subprocess.CalledProcessError as e:
    logger.error(f"Command failed: {e.stderr}")
    raise
```

## Release Checklist

Before releasing a new version:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Code formatted: `black content-system/ tests/`
- [ ] Linting passes: `flake8 content-system/ tests/`
- [ ] README updated with new features
- [ ] Requirements.txt up to date
- [ ] Changelog updated
- [ ] Version bumped in `__init__.py` or similar
- [ ] Git commit and tag: `git tag v1.0.0`

## Support

For issues or questions:

1. Check existing issues/PRs on GitHub
2. Review test cases for usage examples
3. Run tests locally: `pytest tests/ -v`
4. Check logs for detailed error messages

---

**Happy developing!** 🚀
