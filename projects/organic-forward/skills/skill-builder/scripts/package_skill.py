#!/usr/bin/env python3
"""Package a skill directory into a .skill zip file for distribution.

Usage:
    python -m scripts.package_skill <path/to/skill-folder> [--output <path>]

Creates a .skill file (zip archive) containing all skill files.
"""

import argparse
import sys
import zipfile
from pathlib import Path


def package_skill(skill_dir: Path, output: Path = None) -> Path:
    """Create a .skill zip from a skill directory."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"Error: {skill_md} not found — not a valid skill directory", file=sys.stderr)
        sys.exit(1)

    if output is None:
        output = skill_dir.parent / f"{skill_dir.name}.skill"

    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(skill_dir.rglob('*')):
            if file_path.is_file():
                # Skip workspace/eval directories and hidden files
                rel = file_path.relative_to(skill_dir)
                parts = rel.parts
                if any(p.startswith('.') or p.endswith('-workspace') for p in parts):
                    continue
                if any(p == '__pycache__' for p in parts):
                    continue
                zf.write(file_path, rel)
                print(f"  Added: {rel}")

    print(f"\nPackaged: {output} ({output.stat().st_size:,} bytes)")
    return output


def main():
    parser = argparse.ArgumentParser(description="Package a skill for distribution")
    parser.add_argument("skill_dir", help="Path to skill directory")
    parser.add_argument("--output", "-o", help="Output .skill file path")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    output = Path(args.output).resolve() if args.output else None
    package_skill(skill_dir, output)


if __name__ == "__main__":
    main()
