#!/usr/bin/env python3
"""Extract transcript from a YouTube video using yt-dlp.

Usage:
  python3 yt_transcript.py --video-id dQw4w9WgXcQ
  python3 yt_transcript.py --url "https://youtube.com/watch?v=dQw4w9WgXcQ"
  python3 yt_transcript.py --url "..." --lang es         # Spanish subtitles
  python3 yt_transcript.py --url "..." --timestamps       # Include timestamps

Output: JSON to stdout with keys: videoId, language, transcript (plain text or timestamped segments).

Requires: yt-dlp installed (pip3 install yt-dlp). Falls back gracefully if missing.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse


def check_ytdlp():
    """Check if yt-dlp is available."""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def parse_video_id_from_url(url):
    """Extract video ID from a YouTube URL."""
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname in ("youtu.be",):
        return parsed.path.lstrip("/")
    if parsed.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            qs = urllib.parse.parse_qs(parsed.query)
            return qs.get("v", [""])[0]
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/shorts/")[1].split("/")[0]
    return ""


def parse_vtt(vtt_text):
    """Parse WebVTT subtitle file into segments."""
    segments = []
    current_start = ""
    current_end = ""
    current_text_lines = []

    for line in vtt_text.split("\n"):
        line = line.strip()

        # Skip WebVTT header and style blocks
        if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if line == "" or line.startswith("NOTE"):
            if current_text_lines and current_start:
                text = " ".join(current_text_lines)
                # Remove VTT formatting tags
                text = re.sub(r"<[^>]+>", "", text)
                text = text.strip()
                if text:
                    segments.append({
                        "start": current_start,
                        "end": current_end,
                        "text": text,
                    })
            current_text_lines = []
            current_start = ""
            current_end = ""
            continue

        # Timestamp line: 00:00:01.000 --> 00:00:04.000
        ts_match = re.match(r"(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})", line)
        if ts_match:
            current_start = ts_match.group(1)
            current_end = ts_match.group(2)
            continue

        # Numeric cue identifier
        if re.match(r"^\d+$", line):
            continue

        # Text line
        if current_start:
            current_text_lines.append(line)

    # Flush last segment
    if current_text_lines and current_start:
        text = " ".join(current_text_lines)
        text = re.sub(r"<[^>]+>", "", text).strip()
        if text:
            segments.append({"start": current_start, "end": current_end, "text": text})

    return segments


def deduplicate_segments(segments):
    """Remove duplicate/overlapping subtitle lines (common in auto-captions)."""
    if not segments:
        return []

    deduped = [segments[0]]
    for seg in segments[1:]:
        if seg["text"] != deduped[-1]["text"]:
            deduped.append(seg)

    return deduped


def extract_transcript(video_id, lang="en", include_timestamps=False):
    """Extract transcript using yt-dlp."""
    if not check_ytdlp():
        return {
            "error": "yt-dlp not installed",
            "setup": "Install with: pip3 install yt-dlp",
            "fallback": "Skill will continue using video title and description only.",
        }

    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, "subs")

        # Try manual subs first, then auto-generated
        for sub_flag in ["--write-subs", "--write-auto-subs"]:
            cmd = [
                "yt-dlp",
                "--skip-download",
                sub_flag,
                "--sub-lang", lang,
                "--sub-format", "vtt",
                "--output", output_template,
                url,
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            except subprocess.TimeoutExpired:
                continue

            # Find the subtitle file
            vtt_path = os.path.join(tmpdir, f"subs.{lang}.vtt")
            if not os.path.exists(vtt_path):
                # yt-dlp sometimes uses full language name
                for f in os.listdir(tmpdir):
                    if f.endswith(".vtt"):
                        vtt_path = os.path.join(tmpdir, f)
                        break

            if os.path.exists(vtt_path):
                with open(vtt_path, "r", encoding="utf-8") as f:
                    vtt_text = f.read()

                segments = parse_vtt(vtt_text)
                segments = deduplicate_segments(segments)

                if not segments:
                    continue

                if include_timestamps:
                    return {
                        "videoId": video_id,
                        "language": lang,
                        "segmentCount": len(segments),
                        "segments": segments,
                    }
                else:
                    full_text = " ".join(seg["text"] for seg in segments)
                    # Clean up repeated spaces
                    full_text = re.sub(r"\s+", " ", full_text).strip()
                    return {
                        "videoId": video_id,
                        "language": lang,
                        "wordCount": len(full_text.split()),
                        "transcript": full_text,
                    }

    return {
        "videoId": video_id,
        "error": "No captions available",
        "detail": f"No manual or auto-generated {lang} subtitles found for this video.",
        "fallback": "Skill will continue using video title and description only.",
    }


def main():
    parser = argparse.ArgumentParser(description="Extract YouTube transcript via yt-dlp")
    parser.add_argument("--video-id", help="YouTube video ID")
    parser.add_argument("--url", help="YouTube video URL")
    parser.add_argument("--lang", default="en", help="Subtitle language code (default: en)")
    parser.add_argument("--timestamps", action="store_true", help="Include timestamps in output")

    args = parser.parse_args()

    video_id = args.video_id
    if args.url and not video_id:
        video_id = parse_video_id_from_url(args.url)
        if not video_id:
            print(json.dumps({"error": f"Could not parse video ID from URL: {args.url}"}))
            sys.exit(1)

    if not video_id:
        parser.print_help()
        sys.exit(1)

    result = extract_transcript(video_id, lang=args.lang, include_timestamps=args.timestamps)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
