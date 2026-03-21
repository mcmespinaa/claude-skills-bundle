#!/usr/bin/env python3
"""unsplash_fetch.py — Search and download images from Unsplash.

Usage:
  python3 unsplash_fetch.py --query "scandinavian morning light"
  python3 unsplash_fetch.py --query "office workspace" --orientation landscape --size full
  python3 unsplash_fetch.py --query "nature" --count 3 --output-dir ./images
  python3 unsplash_fetch.py --query "abstract" --no-brand-defaults --color black
  python3 unsplash_fetch.py --query "test" --raw-json

Output (stdout): JSON with downloaded image paths, attribution, and metadata.
Progress and errors go to stderr.

Brand defaults (on by default): color=white, orientation=portrait — matching
the Ces brand aesthetic (ivory, minimalist, Scandinavian).
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_BASE = "https://api.unsplash.com"
RATE_FILE = os.path.expanduser("~/.notebooklm/unsplash_rate.json")
DEMO_LIMIT = 50  # requests per hour (demo tier)

VALID_ORIENTATIONS = ["portrait", "landscape", "squarish"]
VALID_COLORS = [
    "black_and_white", "black", "white", "yellow", "orange",
    "red", "purple", "magenta", "green", "teal", "blue",
]
VALID_SIZES = ["raw", "full", "regular", "small", "thumb"]

# Brand defaults for Ces aesthetic
BRAND_DEFAULTS = {
    "color": "white",
    "orientation": "portrait",
}


def load_env():
    """Walk up from script dir to find .env and load it."""
    script_dir = Path(__file__).resolve().parent
    for ancestor in [script_dir] + list(script_dir.parents)[:6]:
        env_file = ancestor / ".env"
        if env_file.is_file():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
            break


def get_api_key():
    """Return UNSPLASH_ACCESS_KEY or exit with instructions."""
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        print(
            "Error: UNSPLASH_ACCESS_KEY not set.\n"
            "Add to your .env file:\n"
            "  UNSPLASH_ACCESS_KEY=your_key_here\n"
            "Get a key at https://unsplash.com/developers",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


# --- Rate limiting ---

def load_rate_data():
    """Load rate tracking JSON. Returns dict keyed by hour."""
    if not os.path.exists(RATE_FILE):
        return {}
    try:
        with open(RATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_rate_data(data):
    """Save rate tracking JSON, pruning entries older than 24h."""
    now = datetime.now(timezone.utc)
    pruned = {}
    for key, count in data.items():
        try:
            hour = datetime.strptime(key, "%Y-%m-%dT%H").replace(tzinfo=timezone.utc)
            if (now - hour).total_seconds() < 86400:
                pruned[key] = count
        except ValueError:
            continue
    os.makedirs(os.path.dirname(RATE_FILE), exist_ok=True)
    with open(RATE_FILE, "w") as f:
        json.dump(pruned, f, indent=2)


def check_rate_limit():
    """Check current hour's request count. Warn if near limit."""
    hour_key = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H")
    data = load_rate_data()
    used = data.get(hour_key, 0)
    if used >= DEMO_LIMIT:
        print(
            f"Error: Rate limit reached ({used}/{DEMO_LIMIT} requests this hour). "
            "Resets at the top of the next hour.",
            file=sys.stderr,
        )
        sys.exit(1)
    if used >= DEMO_LIMIT - 5:
        print(f"Warning: {used}/{DEMO_LIMIT} requests used this hour.", file=sys.stderr)
    return used


def record_request():
    """Increment the request counter for the current hour."""
    hour_key = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H")
    data = load_rate_data()
    data[hour_key] = data.get(hour_key, 0) + 1
    save_rate_data(data)


# --- Unsplash API ---

def api_request(path, params=None):
    """Make an authenticated GET request to the Unsplash API."""
    api_key = get_api_key()
    url = f"{API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Client-ID {api_key}")
    req.add_header("Accept-Version", "v1")

    check_rate_limit()

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            record_request()
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("Error: Rate limit exceeded (403). Try again later.", file=sys.stderr)
        elif e.code == 401:
            print("Error: Invalid UNSPLASH_ACCESS_KEY (401).", file=sys.stderr)
        else:
            print(f"Error: Unsplash API returned {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Network request failed: {e.reason}", file=sys.stderr)
        sys.exit(1)


def search_photos(query, orientation=None, color=None, per_page=10, page=1):
    """Search Unsplash photos. Returns the API response dict."""
    params = {"query": query, "per_page": per_page, "page": page}
    if orientation:
        params["orientation"] = orientation
    if color:
        params["color"] = color
    return api_request("/search/photos", params)


def track_download(photo_id):
    """Trigger the Unsplash download endpoint (required by API guidelines)."""
    try:
        api_request(f"/photos/{photo_id}/download")
        return True
    except SystemExit:
        # Non-fatal — log but don't abort
        print(f"Warning: Failed to track download for {photo_id}", file=sys.stderr)
        return False


def download_image(url, output_path):
    """Download an image from URL to disk."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "unsplash_fetch/1.0")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(output_path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
        return True
    except (urllib.error.URLError, OSError) as e:
        print(f"Warning: Failed to download image: {e}", file=sys.stderr)
        return False


def build_attribution(photo):
    """Build attribution strings from an Unsplash photo object."""
    name = photo.get("user", {}).get("name", "Unknown")
    username = photo.get("user", {}).get("username", "")
    profile_url = f"https://unsplash.com/@{username}" if username else "https://unsplash.com"
    photo_url = photo.get("links", {}).get("html", f"https://unsplash.com/photos/{photo['id']}")

    return {
        "photographer": name,
        "photographer_url": profile_url,
        "unsplash_url": photo_url,
        "attribution": f"Photo by {name} on Unsplash",
        "attribution_html": (
            f'<a href="{profile_url}?utm_source=your_app&utm_medium=referral">{name}</a>'
            f' on <a href="https://unsplash.com?utm_source=your_app&utm_medium=referral">Unsplash</a>'
        ),
    }


def save_sidecar(output_path, photo, attribution, download_tracked):
    """Write a sidecar JSON file alongside the downloaded image."""
    sidecar_path = Path(output_path).with_suffix(".json")
    sidecar = {
        "id": photo["id"],
        "width": photo.get("width"),
        "height": photo.get("height"),
        "download_tracked": download_tracked,
        **attribution,
    }
    with open(sidecar_path, "w") as f:
        json.dump(sidecar, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Search and download Unsplash images")
    parser.add_argument("--query", required=True, help="Search terms")
    parser.add_argument(
        "--orientation", choices=VALID_ORIENTATIONS, default=None,
        help="Image orientation filter (default: portrait with brand defaults)",
    )
    parser.add_argument(
        "--color", choices=VALID_COLORS, default=None,
        help="Color filter (default: white with brand defaults)",
    )
    parser.add_argument(
        "--size", choices=VALID_SIZES, default="regular",
        help="Image size variant to download (default: regular = 1080px wide)",
    )
    parser.add_argument("--count", type=int, default=1, help="Number of images (max 10, default: 1)")
    parser.add_argument("--output-dir", default="/tmp", help="Download directory (default: /tmp)")
    parser.add_argument(
        "--no-brand-defaults", action="store_true",
        help="Disable brand aesthetic defaults (color=white, orientation=portrait)",
    )
    parser.add_argument(
        "--raw-json", action="store_true",
        help="Print raw API response without downloading images",
    )
    args = parser.parse_args()

    load_env()
    get_api_key()  # Fail fast if key is missing

    args.count = min(max(args.count, 1), 10)

    # Apply brand defaults unless disabled
    orientation = args.orientation
    color = args.color
    if not args.no_brand_defaults:
        if orientation is None:
            orientation = BRAND_DEFAULTS["orientation"]
        if color is None:
            color = BRAND_DEFAULTS["color"]

    # Search
    print(f"Searching Unsplash for: {args.query}", file=sys.stderr)
    result = search_photos(
        query=args.query,
        orientation=orientation,
        color=color,
        per_page=args.count,
    )

    photos = result.get("results", [])
    total = result.get("total", 0)

    if not photos:
        print(f"Warning: No results found for '{args.query}'", file=sys.stderr)
        print(json.dumps({"images": [], "total": 0}))
        return

    print(f"Found {total} results, processing {len(photos)}.", file=sys.stderr)

    if args.raw_json:
        print(json.dumps(result, indent=2))
        return

    # Download
    os.makedirs(args.output_dir, exist_ok=True)
    images = []

    for photo in photos:
        photo_id = photo["id"]
        urls = photo.get("urls", {})
        image_url = urls.get(args.size, urls.get("regular"))

        if not image_url:
            print(f"Warning: No URL for size '{args.size}' on photo {photo_id}, skipping.", file=sys.stderr)
            continue

        ext = "jpg"
        output_path = os.path.join(args.output_dir, f"unsplash-{photo_id}.{ext}")

        print(f"  Downloading {photo_id}...", file=sys.stderr)
        if not download_image(image_url, output_path):
            continue

        # Track download (Unsplash API requirement)
        tracked = track_download(photo_id)

        attribution = build_attribution(photo)
        save_sidecar(output_path, photo, attribution, tracked)

        images.append({
            "file": output_path,
            "id": photo_id,
            "width": photo.get("width"),
            "height": photo.get("height"),
            "download_tracked": tracked,
            **attribution,
        })

    print(f"Downloaded {len(images)} image(s).", file=sys.stderr)
    print(json.dumps({"images": images, "total": total}))


if __name__ == "__main__":
    main()
