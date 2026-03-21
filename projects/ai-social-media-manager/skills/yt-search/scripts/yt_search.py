#!/usr/bin/env python3
"""YouTube Data API v3 — Search videos and fetch metadata.

Usage:
  python3 yt_search.py --query "AI leadership" [--max-results 10] [--type video] [--order relevance]
  python3 yt_search.py --channel-id UCxxxx [--max-results 10] [--order date]
  python3 yt_search.py --video-id dQw4w9WgXcQ   # single video metadata

Output: JSON to stdout.

Requires: YOUTUBE_API_KEY env var.
"""

import argparse
import json
import os
import ssl
import sys
import urllib.request
import urllib.parse
import urllib.error

API_BASE = "https://www.googleapis.com/youtube/v3"


def get_api_key():
    key = os.environ.get("YOUTUBE_API_KEY", "")
    if not key:
        print(json.dumps({
            "error": "YOUTUBE_API_KEY not set",
            "setup": (
                "1. Go to https://console.cloud.google.com/apis/credentials\n"
                "2. Create an API key (or reuse your Google Cloud project)\n"
                "3. Enable 'YouTube Data API v3' at https://console.cloud.google.com/apis/library/youtube.googleapis.com\n"
                "4. Add YOUTUBE_API_KEY to .claude/settings.local.json under env"
            )
        }), file=sys.stderr)
        sys.exit(1)
    return key


def api_get(endpoint, params, max_retries=2):
    """Make a GET request to the YouTube Data API with retry on transient errors."""
    import time

    params["key"] = get_api_key()
    url = f"{API_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"

    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={"Accept": "application/json"})

    for attempt in range(max_retries + 1):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            # Retry on transient 5xx errors
            if e.code in (500, 502, 503) and attempt < max_retries:
                wait = 2 ** (attempt + 1)
                print(json.dumps({"warning": f"HTTP {e.code}, retrying in {wait}s..."}), file=sys.stderr)
                time.sleep(wait)
                continue
            error_info = {"error": f"HTTP {e.code}", "detail": body}
            if e.code == 403:
                error_info["hint"] = "Quota exceeded or API not enabled. Check Google Cloud Console."
            print(json.dumps(error_info), file=sys.stderr)
            sys.exit(1)
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < max_retries:
                wait = 2 ** (attempt + 1)
                print(json.dumps({"warning": f"Connection error: {e}, retrying in {wait}s..."}), file=sys.stderr)
                time.sleep(wait)
                continue
            print(json.dumps({"error": f"Connection failed after {max_retries + 1} attempts", "detail": str(e)}), file=sys.stderr)
            sys.exit(1)


def search_videos(query, max_results=10, search_type="video", order="relevance", channel_id=None):
    """Search YouTube and return results with full metadata."""
    params = {
        "part": "snippet",
        "q": query,
        "maxResults": min(max_results, 50),
        "type": search_type,
        "order": order,
    }
    if channel_id:
        params["channelId"] = channel_id

    data = api_get("search", params)
    items = data.get("items", [])

    # Collect video IDs for stats lookup
    video_ids = [
        it["id"]["videoId"] for it in items
        if it["id"].get("videoId")
    ]

    stats = {}
    if video_ids:
        stats = get_video_stats(video_ids)

    results = []
    for it in items:
        vid = it["id"].get("videoId", "")
        snippet = it.get("snippet", {})
        s = stats.get(vid, {})
        results.append({
            "videoId": vid,
            "title": snippet.get("title", ""),
            "channelTitle": snippet.get("channelTitle", ""),
            "channelId": snippet.get("channelId", ""),
            "publishedAt": snippet.get("publishedAt", ""),
            "description": snippet.get("description", ""),
            "thumbnailUrl": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "viewCount": s.get("viewCount", ""),
            "likeCount": s.get("likeCount", ""),
            "commentCount": s.get("commentCount", ""),
            "duration": s.get("duration", ""),
        })

    return results


def get_video_stats(video_ids):
    """Fetch statistics and content details for a list of video IDs."""
    stats = {}
    # API allows max 50 IDs per call
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        data = api_get("videos", {
            "part": "statistics,contentDetails",
            "id": ",".join(batch),
        })
        for item in data.get("items", []):
            vid = item["id"]
            st = item.get("statistics", {})
            cd = item.get("contentDetails", {})
            stats[vid] = {
                "viewCount": st.get("viewCount", "0"),
                "likeCount": st.get("likeCount", "0"),
                "commentCount": st.get("commentCount", "0"),
                "duration": cd.get("duration", ""),
            }
    return stats


def get_single_video(video_id):
    """Fetch full metadata for a single video."""
    data = api_get("videos", {
        "part": "snippet,statistics,contentDetails",
        "id": video_id,
    })
    items = data.get("items", [])
    if not items:
        return {"error": f"Video {video_id} not found or is private"}

    item = items[0]
    snippet = item.get("snippet", {})
    st = item.get("statistics", {})
    cd = item.get("contentDetails", {})

    return {
        "videoId": video_id,
        "title": snippet.get("title", ""),
        "channelTitle": snippet.get("channelTitle", ""),
        "channelId": snippet.get("channelId", ""),
        "publishedAt": snippet.get("publishedAt", ""),
        "description": snippet.get("description", ""),
        "tags": snippet.get("tags", []),
        "thumbnailUrl": snippet.get("thumbnails", {}).get("maxres", snippet.get("thumbnails", {}).get("high", {})).get("url", ""),
        "viewCount": st.get("viewCount", "0"),
        "likeCount": st.get("likeCount", "0"),
        "commentCount": st.get("commentCount", "0"),
        "duration": cd.get("duration", ""),
        "categoryId": snippet.get("categoryId", ""),
    }


def get_channel_uploads(channel_id, max_results=10, order="date"):
    """Get recent uploads from a channel."""
    return search_videos("", max_results=max_results, order=order, channel_id=channel_id)


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


def main():
    parser = argparse.ArgumentParser(description="YouTube Data API v3 search & metadata")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--video-id", help="Fetch metadata for a single video ID")
    parser.add_argument("--video-url", help="Fetch metadata for a video URL")
    parser.add_argument("--channel-id", help="List uploads from a channel ID")
    parser.add_argument("--max-results", type=int, default=10, help="Max results (default 10, max 50)")
    parser.add_argument("--type", default="video", choices=["video", "channel", "playlist"], help="Search type")
    parser.add_argument("--order", default="relevance", choices=["relevance", "date", "viewCount", "rating"], help="Sort order")

    args = parser.parse_args()

    if args.video_url:
        vid = parse_video_id_from_url(args.video_url)
        if not vid:
            print(json.dumps({"error": f"Could not parse video ID from URL: {args.video_url}"}))
            sys.exit(1)
        result = get_single_video(vid)
        print(json.dumps(result, indent=2))

    elif args.video_id:
        result = get_single_video(args.video_id)
        print(json.dumps(result, indent=2))

    elif args.channel_id and not args.query:
        results = get_channel_uploads(args.channel_id, max_results=args.max_results, order=args.order)
        print(json.dumps(results, indent=2))

    elif args.query:
        results = search_videos(
            args.query,
            max_results=args.max_results,
            search_type=args.type,
            order=args.order,
            channel_id=args.channel_id,
        )
        print(json.dumps(results, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
