# Content-System: Existing Audit & Enhancement Plan

## Current System State

### ✓ Working Components

- **extract_web.py**: Fetches articles from URLs using requests + BeautifulSoup. Saves to `extracted/text/`.
- **Directory Structure**: Input/extracted/analysis/content/scheduler_ready organized by stage.
- **Code Quality**: All Python scripts pass flake8/black PEP8 standards.
- **Dependencies**: beautifulsoup4, requests, ruff, flake8, black installed and working.

### Existing Modules (To Preserve & Enhance)

```
system/
├── extract_web.py      [WORKING - will extend for HTML articles]
├── extract_video.py    [STUB - enhance for podcasts/videos]
├── extract_pdf.py      [STUB - enhance for documents]
├── clean_text.py       [BASIC - enhance for multi-format]
├── analyze.py          [BASIC - enhance for content categorization]
├── generate_content.py [BASIC - extend to multi-platform variations]
├── file_manager.py     [BASIC - keep as-is]
├── scheduler_prep.py   [BASIC - enhance for platform APIs]
├── main.py             [STUB - upgrade to full orchestrator]
└── __pycache__/        [AUTO - ignore]
```

## Content Inventory You Have

**You bring:**

- Blog articles (plain text, HTML-CSS formatted)
- Podcast audio files + metadata
- Videos, project presentations, live motion clips
- Short-form content (shorts/reels)
- Full outlines and content planning documents

**We need to handle:**

1. **Blog articles**: Extract from HTML/Markdown, preserve formatting
2. **Podcast audio**: Extract metadata, generate transcripts (optional: OpenAI Whisper)
3. **Videos**: Extract metadata, frame captures, auto-generated captions
4. **Short-form**: Extract clips, optimized for TikTok/Instagram Reels
5. **Planning docs**: Parse outlines → generate structured content

## Enhancement Strategy

### Phase 1: Non-Breaking Extraction Layer Expansion

- Extend `extract_web.py` to handle local HTML files
- Create `extract_blog.py` for HTML-CSS blog articles
- Enhance `extract_video.py` for local video files (metadata + optional transcript)
- All new extractors write to existing `extracted/` structure
- **Preserve**: Original `extract_web.py` URL fetching unchanged

### Phase 2: Smart Analysis & Categorization

- Enhance `analyze.py` to detect content type (blog/podcast/video/social)
- Extract themes, keywords, sentiment
- Auto-categorize by content pillar
- Generate structured metadata JSON
- **Preserve**: Existing tag/trend scoring logic

### Phase 3: Multi-Platform Content Generation

- Upgrade `generate_content.py` with templates for:
  - Instagram captions (3 variations: casual, professional, story prompt)
  - TikTok scripts (hook + punchline format)
  - LinkedIn posts (thought-leadership angle)
  - Email subject lines + body
  - Blog snippets (pull quote format)
  - Podcast show notes
- Optional: OpenAI API for AI enhancement (falls back to templates)
- **Preserve**: Existing blog generation logic

### Phase 4: Engagement & Community Building

- New module `engagement_prompts.py`: Generate questions/CTAs/polls
- New module `bot_responses.py`: Draft comment replies, DM templates
- Human review interface for all AI-generated content
- **Preserve**: All existing modules unchanged

### Phase 5: Smart Scheduling & Orchestration

- Enhance `scheduler_prep.py` to format for Buffer/Meta/YouTube schedulers
- Upgrade `main.py` to full orchestrator with:
  - `--extract`: Run extraction only
  - `--analyze`: Run analysis only
  - `--generate`: Run content generation
  - `--full`: Run entire pipeline
  - `--dry-run`: Preview without committing
- Add `config.yaml` for brand customization
- **Preserve**: Existing file structure and naming

## What You Need to Provide

Before we start enhancements, provide (one at a time as we progress):

1. **Sample content files** (Step 2):
   - 1 blog article (HTML or Markdown)
   - 1 podcast episode info/transcript
   - 1 video metadata/description
   - Your brand mission statement (1-2 sentences)

2. **Platform preferences** (Step 2):
   - Which platforms matter most? (Instagram, TikTok, YouTube, LinkedIn, Blog, Email?)
   - Posting frequency goal? (3x/week? Daily?)
   - Best times to post? (or use AI analysis?)

3. **Content pillars** (Step 2):
   - What are your 3-5 main topics? (e.g., "Nonprofit impact", "Personal growth", "Behind-the-scenes")

4. **Tone/voice** (Step 2):
   - Casual? Professional? Inspirational? Humorous?

---

## Why This Approach Works

✓ **No breaking changes**: All existing code stays intact
✓ **Modular**: Add features independently
✓ **Testable**: Each step can be validated before moving to next
✓ **Trackable**: Easy to see progress and rollback if needed
✓ **Solo-friendly**: Can pause anytime and resume exactly where we left off
✓ **Future-proof**: New platforms/formats can be added without rewriting

---

## Next Step

**Go to Step 1: Audit** — I'll confirm the current system is working end-to-end with your existing content pipeline.
