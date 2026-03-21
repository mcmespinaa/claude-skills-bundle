# Step 4: Preprocess

- **Infographics (.png):** The `ghl_upload_media.sh` script auto-resizes to 4:5 (1080x1350) with ivory padding. Pass `--no-resize` only if user explicitly requests it.
- **Videos (.mp4):** Check file size. If over 500MB, warn and suggest compression. No resize needed.
- **Reports (.md):** Extract 2-3 key insights as caption text. The full report is too long for social.
- **Quizzes:** Extract 1-2 engaging questions as a teaser post.
- **Slide Decks (.pdf) — carousel path:** When user wants to post to social (not media-library-only):
  1. Run `pdf_to_slides.py` to extract per-page PNGs at 1080x1350:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/pdf_to_slides.py" \
       --input "<pdf_path>" \
       --output-dir "/tmp/slides-$(date +%Y%m%d-%H%M%S)" \
       --max-slides 10
     ```
  2. Parse the JSON output — the `slides` array contains the absolute paths of the PNGs.
  3. Proceed to Step 5 using `ghl_upload_carousel.sh` with those paths (not `ghl_upload_media.sh`).
- **Slide Decks (.pptx) — carousel path:**
  - Check if LibreOffice is installed: `command -v soffice`
  - If available: convert to PDF first: `soffice --headless --convert-to pdf --outdir /tmp "<pptx_path>"`, then follow the PDF carousel path above.
  - If not available: inform the user — "LibreOffice is needed to convert PPTX for carousel posting. Install with `brew install libreoffice`, or use the PDF version." Offer media-library-only upload as fallback.
