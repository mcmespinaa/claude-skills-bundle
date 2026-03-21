# NotebookLM Artifact Types

Full reference for all artifact types that NotebookLM can generate, their typical processing times, and download formats.

## Generation Commands

All commands support `-s <source_id>` to limit generation to specific sources, `--language <code>` for output language, and `--json` for machine-readable output.

### Audio (Podcast)

```bash
notebooklm generate audio "Focus on practical takeaways"
notebooklm generate audio --format deep-dive --length long
```

| Option | Values |
|--------|--------|
| `--format` | `deep-dive` (default), `brief`, `critique`, `debate` |
| `--length` | `short`, `default`, `long` |
| **Processing time** | 10-20 minutes |
| **Download** | `.mp3` |

**Social use:** Extract key quotes for text posts. Create "podcast highlight" cards. Repurpose as Reels/TikTok audio.

### Video

```bash
notebooklm generate video "Explain the key concepts visually"
```

| Option | Values |
|--------|--------|
| `--format` | `explainer` (default), `brief` |
| `--style` | `auto`, `classic`, `whiteboard`, `kawaii`, `anime`, `watercolor`, `retro-print`, `heritage`, `paper-craft` |
| **Processing time** | 15-45 minutes |
| **Download** | `.mp4` |

**Social use:** Post directly to IG Reels, FB, TH. Upload to YouTube via `/distribute`. Use as carousel video slides.

### Slide Deck

```bash
notebooklm generate slide-deck
notebooklm generate slide-deck --format presenter --length short
```

| Option | Values |
|--------|--------|
| `--format` | `detailed` (default), `presenter` |
| `--length` | `default`, `short` |
| **Processing time** | 5-15 minutes |
| **Download** | `.pdf` (default), `.pptx` (with `--format pptx`) |

**Social use:** Extract slides as carousel images. Convert PDF pages to PNGs for IG/FB carousels.

### Report

```bash
notebooklm generate report --format briefing-doc
notebooklm generate report --format study-guide --append "Target audience: business owners"
```

| Option | Values |
|--------|--------|
| `--format` | `briefing-doc`, `study-guide`, `blog-post`, `custom` |
| `--append` | Extra instructions appended to the template |
| **Processing time** | 5-15 minutes |
| **Download** | `.md` |

**Social use:** Extract key sections as LinkedIn long-form posts. Pull quotes for shorter posts.

### Mind Map

```bash
notebooklm generate mind-map
```

| **Processing time** | Instant (synchronous) |
|--------|--------|
| **Download** | `.json` |

**Social use:** Convert to visual diagram for carousel slides. Use as content structure reference.

### Quiz

```bash
notebooklm generate quiz --difficulty medium --quantity standard
```

| Option | Values |
|--------|--------|
| `--difficulty` | `easy`, `medium`, `hard` |
| `--quantity` | `fewer`, `standard`, `more` |
| **Processing time** | 5-15 minutes |
| **Download** | `.json`, `.md` (with `--format markdown`), `.html` |

**Social use:** Extract 1-2 questions as engagement posts ("Did you know?" format). Create "Test your knowledge" carousel slides.

### Flashcards

```bash
notebooklm generate flashcards --difficulty medium
```

| Option | Values |
|--------|--------|
| `--difficulty` | `easy`, `medium`, `hard` |
| `--quantity` | `fewer`, `standard`, `more` |
| **Processing time** | 5-15 minutes |
| **Download** | `.json`, `.md` (with `--format markdown`), `.html` |

**Social use:** Convert Q&A pairs into carousel slides (one card per slide).

### Infographic

```bash
notebooklm generate infographic
notebooklm generate infographic --orientation portrait --detail detailed
```

| Option | Values |
|--------|--------|
| `--orientation` | `landscape`, `portrait`, `square` |
| `--detail` | `concise`, `standard`, `detailed` |
| **Processing time** | 5-15 minutes |
| **Download** | `.png` |

**Social use:** Post directly to IG, FB, TH, LI. Auto-resize via upload scripts.

### Data Table

```bash
notebooklm generate data-table "Compare the key metrics across all sources"
```

| **Processing time** | 5-15 minutes |
|--------|--------|
| **Download** | `.csv` |

**Social use:** Extract top rows for "By the numbers" posts. Convert to visual chart for carousel.

## Downloading Artifacts

```bash
# Check what's available
notebooklm artifact list --json

# Wait for completion (use in background agent)
notebooklm artifact wait <artifact_id> --timeout 1200

# Download by type
notebooklm download audio ./podcast.mp3
notebooklm download video ./explainer.mp4
notebooklm download report ./report.md
notebooklm download slide-deck ./slides.pdf
notebooklm download slide-deck ./slides.pptx --format pptx
notebooklm download infographic ./infographic.png
notebooklm download mind-map ./mindmap.json
notebooklm download data-table ./data.csv
notebooklm download quiz ./quiz.md --format markdown
notebooklm download flashcards ./cards.md --format markdown
```

## Artifact Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Queued, not started |
| `in_progress` | Currently generating |
| `completed` | Ready for download |
| `unknown` | Check manually |

## Rate Limiting

Audio, video, quiz, flashcards, infographic, and slide deck generation may fail due to Google rate limits. Reliable operations: mind-map, report, data-table. If generation fails, wait 5-10 minutes and retry.
