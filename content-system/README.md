
# content-system

## Automated Content Pipeline for Phoenix Rise

This system lets you upload new content (blog, text, audio, video), then automatically:

1. Ingests and sorts files
2. Analyzes and categorizes content by your brand pillars
3. Generates multi-platform posts (blog, Instagram, YouTube, etc.)
4. Prepares everything for scheduling

### How to Use

1. **Add new content**
 - Place files in `content-system/input/uploads/` (text, blog, audio, video)

2. **Run the full pipeline**
 - From the project root:
   ```bash
   python3 content-system/system/main.py --step full
   ```

	- This will:
   - Ingest new files
   - Analyze and categorize them
   - Generate content for each platform
   - Move posts to `scheduler_ready/` folders

3. **Review and schedule**
 - Find ready-to-post content in `content-system/scheduler_ready/` for each platform

### Customization

- Edit `content-system/config.yaml` to update your brand, pillars, and platform settings
- Add new content types or platforms by extending the pipeline scripts

### Next Steps

- Integrate with social media APIs for auto-posting
- Add dashboard and engagement automation

---

**You can now focus on creating and uploading content—your system handles the rest!**
