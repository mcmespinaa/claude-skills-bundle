#!/usr/bin/env python3
"""Transcribe Instagram Reel audio files using Whisper.

Usage:
    python3 ig_transcribe.py <audio_file_or_dir> [--model base] [--language en] [--output-dir <dir>]

Outputs .txt transcript files alongside each audio file (or in --output-dir).
"""

import argparse
import json
import sys
from pathlib import Path

def transcribe_file(audio_path: Path, model, output_dir: Path) -> dict:
    """Transcribe a single audio file and save the transcript."""
    print(f"Transcribing: {audio_path.name} ...", flush=True)

    result = model.transcribe(str(audio_path))
    text = result["text"].strip()
    language = result.get("language", "unknown")

    # Save transcript
    stem = audio_path.stem
    txt_path = output_dir / f"{stem}.txt"
    txt_path.write_text(text, encoding="utf-8")

    # Save detailed JSON (with segments/timestamps)
    json_path = output_dir / f"{stem}_transcript.json"
    segments = [
        {
            "start": s["start"],
            "end": s["end"],
            "text": s["text"].strip(),
        }
        for s in result.get("segments", [])
    ]
    json_path.write_text(
        json.dumps(
            {"file": audio_path.name, "language": language, "text": text, "segments": segments},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"  -> {txt_path} ({len(text)} chars, lang={language})")
    return {"file": audio_path.name, "transcript": str(txt_path), "chars": len(text), "language": language}


def main():
    parser = argparse.ArgumentParser(description="Transcribe IG reel audio with Whisper")
    parser.add_argument("input", help="Audio file or directory of audio files")
    parser.add_argument("--model", default="base", help="Whisper model: tiny, base, small, medium, large (default: base)")
    parser.add_argument("--language", default=None, help="Language code (e.g. en, de). Auto-detected if omitted.")
    parser.add_argument("--output-dir", default=None, help="Output directory for transcripts (default: same as input)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: {input_path} does not exist", file=sys.stderr)
        sys.exit(1)

    # Collect audio files
    audio_exts = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}
    if input_path.is_dir():
        audio_files = sorted(f for f in input_path.iterdir() if f.suffix.lower() in audio_exts)
    else:
        audio_files = [input_path]

    if not audio_files:
        print("No audio files found.", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir) if args.output_dir else (input_path if input_path.is_dir() else input_path.parent)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load Whisper model
    print(f"Loading Whisper model '{args.model}' ...", flush=True)
    import whisper
    model = whisper.load_model(args.model)

    results = []
    for af in audio_files:
        try:
            r = transcribe_file(af, model, output_dir)
            results.append(r)
        except Exception as e:
            print(f"  ERROR transcribing {af.name}: {e}", file=sys.stderr)

    print(f"\nDone. Transcribed {len(results)}/{len(audio_files)} files.")

    # Print summary as JSON for piping
    summary_path = output_dir / "transcription_summary.json"
    summary_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
