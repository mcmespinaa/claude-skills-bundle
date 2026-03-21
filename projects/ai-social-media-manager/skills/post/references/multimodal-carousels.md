# Multimodal Carousels (Image + Video)

## Step 3b — Decide on Mixed Media

For carousel posts, ask if the user wants **mixed media** (images + video slides):

- **Recommended placement:** Video on slide 1 (hook, stops the scroll with motion) and slide 5 (re-engagement spike mid-carousel).
- **Default:** 2 videos + 8 images for a 10-slide carousel.
- **Platform support:**
  - Instagram: YES (mixed images + videos in same carousel)
  - Threads: YES (up to 20 images or 5 videos, mixed)
  - Facebook: NO (images only OR videos only, not mixed). Auto-generate image-only version for FB.
- **Cost:** ~$0.36-1.32 per multimodal carousel (images ~$0.02-0.04 each, videos ~$0.10-0.50 each).
- **Time:** ~4-8 minutes total (vs ~2 minutes for image-only).

If the user wants multimodal, note which slides should be video in your slide plan. Pass this to the generation step.

## Generation Pipeline

1. Create a JSON config defining each slide's type, prompt, and settings.
2. Run `gen_multimodal_slides.py` which generates all images first (Gemini 3.1 Flash Image), then videos (Veo 3.1).
3. Video slides use either text-to-video (for hook slide) or image-to-video (animate an existing slide).
4. If a video fails, the script auto-falls back to a generated image with a warning.
5. Output: JSON manifest with file paths, types, and sizes.

```bash
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/gen_multimodal_slides.py \
  --config /tmp/carousel_config.json \
  --output-dir /tmp/carousel_output
```

## Video Generation Config

- Model: `veo-3.1-generate-preview` (Veo 3.1)
- Duration: 4-6 seconds (4s for hooks, 6s for re-engagement)
- Aspect ratio: 9:16 portrait (matches IG feed autoplay)
- Resolution: 720p or 1080p
- Negative prompt: "cartoon, low quality, blurry, dark background, neon, stock footage, jarring transitions"
- Generation time: 40-360 seconds per video (async polling)

## Veo 3.1 API Gotchas

- Veo uses the `predictLongRunning` endpoint, NOT `generateContent`. Using `generateContent` with `"responseModalities": ["VIDEO"]` returns 400.
- `personGeneration: "dont_allow"` is NOT supported. Omit this parameter entirely or get 400.
- The `gen_video_slide.py` script uses the google-genai SDK which routes correctly. Only raw curl/urllib calls need to use `predictLongRunning`.
- Response is a long-running operation. Poll with `GET /v1beta/{operation_name}` until `done: true`.

## Upload Mixed Media

```bash
bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_upload_carousel.sh \
  --file /tmp/carousel_output/slide_01.mp4 \
  --file /tmp/carousel_output/slide_02.jpg \
  --file /tmp/carousel_output/slide_03.jpg \
  --platform ig --multimodal
```

With `--multimodal`, the script outputs a JSON manifest with URL+type pairs instead of comma-separated URLs.

## Platform-Specific Media Handling

- **Instagram/Threads:** Use full mixed media array (images + videos).
- **Facebook:** Strip video URLs, use image-only media array.
- When posting to "All" platforms, build two media arrays: mixed for IG/TH, image-only for FB.
