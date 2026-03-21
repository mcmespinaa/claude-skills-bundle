#!/usr/bin/env python3
"""Analyze a YouTube channel — engagement patterns, top videos, posting frequency.

Usage:
  python3 yt_channel_analysis.py --channel-id UCxxxx [--max-videos 20]
  python3 yt_channel_analysis.py --handle "@channelhandle" [--max-videos 20]

Output: JSON report to stdout.

Requires: YOUTUBE_API_KEY env var.
"""

import argparse
import json
import os
import re
import ssl
import sys
import urllib.request
import urllib.parse
import urllib.error
from collections import Counter
from datetime import datetime

API_BASE = "https://www.googleapis.com/youtube/v3"


def get_api_key():
    key = os.environ.get("YOUTUBE_API_KEY", "")
    if not key:
        print(json.dumps({
            "error": "YOUTUBE_API_KEY not set",
            "setup": (
                "1. Go to https://console.cloud.google.com/apis/credentials\n"
                "2. Create an API key\n"
                "3. Enable 'YouTube Data API v3'\n"
                "4. Add YOUTUBE_API_KEY to .claude/settings.local.json under env"
            )
        }), file=sys.stderr)
        sys.exit(1)
    return key


def api_get(endpoint, params):
    """Make a GET request to the YouTube Data API."""
    params["key"] = get_api_key()
    url = f"{API_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(json.dumps({"error": f"HTTP {e.code}", "detail": body}), file=sys.stderr)
        sys.exit(1)


def resolve_handle(handle):
    """Resolve a @handle to a channel ID."""
    # Strip @ if present
    handle = handle.lstrip("@")
    data = api_get("channels", {
        "part": "id,snippet",
        "forHandle": handle,
    })
    items = data.get("items", [])
    if not items:
        # Fallback: search for the channel
        data = api_get("search", {
            "part": "snippet",
            "q": handle,
            "type": "channel",
            "maxResults": 1,
        })
        items = data.get("items", [])
        if items:
            return items[0]["id"].get("channelId", "")
        return ""
    return items[0]["id"]


def get_channel_info(channel_id):
    """Fetch channel metadata and statistics."""
    data = api_get("channels", {
        "part": "snippet,statistics,contentDetails,brandingSettings",
        "id": channel_id,
    })
    items = data.get("items", [])
    if not items:
        return None
    item = items[0]
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    return {
        "channelId": channel_id,
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "customUrl": snippet.get("customUrl", ""),
        "publishedAt": snippet.get("publishedAt", ""),
        "country": snippet.get("country", ""),
        "subscriberCount": stats.get("subscriberCount", "0"),
        "videoCount": stats.get("videoCount", "0"),
        "viewCount": stats.get("viewCount", "0"),
        "thumbnailUrl": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
    }


def get_recent_videos(channel_id, max_results=50):
    """Fetch recent uploads from a channel with full stats."""
    # Search for channel's videos, ordered by date
    data = api_get("search", {
        "part": "snippet",
        "channelId": channel_id,
        "type": "video",
        "order": "date",
        "maxResults": min(max_results, 50),
    })
    items = data.get("items", [])
    video_ids = [it["id"]["videoId"] for it in items if it["id"].get("videoId")]

    if not video_ids:
        return []

    # Fetch full stats
    stats_data = api_get("videos", {
        "part": "snippet,statistics,contentDetails",
        "id": ",".join(video_ids),
    })

    videos = []
    for item in stats_data.get("items", []):
        snippet = item.get("snippet", {})
        st = item.get("statistics", {})
        cd = item.get("contentDetails", {})
        videos.append({
            "videoId": item["id"],
            "title": snippet.get("title", ""),
            "publishedAt": snippet.get("publishedAt", ""),
            "description": snippet.get("description", "")[:300],
            "tags": snippet.get("tags", [])[:10],
            "viewCount": int(st.get("viewCount", "0")),
            "likeCount": int(st.get("likeCount", "0")),
            "commentCount": int(st.get("commentCount", "0")),
            "duration": cd.get("duration", ""),
        })

    return videos


def parse_iso_duration(dur):
    """Parse ISO 8601 duration (PT1H2M3S) to seconds."""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", dur)
    if not match:
        return 0
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    return h * 3600 + m * 60 + s


def analyze_channel(channel_id, max_videos=20):
    """Build a full channel analysis report."""
    info = get_channel_info(channel_id)
    if not info:
        return {"error": f"Channel {channel_id} not found"}

    videos = get_recent_videos(channel_id, max_results=max_videos)

    if not videos:
        info["analysis"] = {"note": "No public videos found"}
        return info

    # Sort by views for top videos
    top_by_views = sorted(videos, key=lambda v: v["viewCount"], reverse=True)[:10]

    # Engagement analysis
    total_views = sum(v["viewCount"] for v in videos)
    total_likes = sum(v["likeCount"] for v in videos)
    total_comments = sum(v["commentCount"] for v in videos)
    avg_views = total_views / len(videos) if videos else 0
    avg_likes = total_likes / len(videos) if videos else 0
    avg_comments = total_comments / len(videos) if videos else 0

    # Like-to-view ratio (engagement proxy)
    engagement_rate = (total_likes / total_views * 100) if total_views > 0 else 0

    # Posting frequency
    dates = []
    for v in videos:
        try:
            dt = datetime.fromisoformat(v["publishedAt"].replace("Z", "+00:00"))
            dates.append(dt)
        except (ValueError, KeyError):
            pass

    posting_frequency = ""
    if len(dates) >= 2:
        dates.sort()
        gaps = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        if avg_gap <= 1:
            posting_frequency = "daily"
        elif avg_gap <= 3:
            posting_frequency = f"every {avg_gap:.0f} days (~2-3x/week)"
        elif avg_gap <= 7:
            posting_frequency = f"weekly (every {avg_gap:.0f} days)"
        elif avg_gap <= 14:
            posting_frequency = f"biweekly (every {avg_gap:.0f} days)"
        else:
            posting_frequency = f"every {avg_gap:.0f} days"

    # Day-of-week distribution
    day_counts = Counter()
    for dt in dates:
        day_counts[dt.strftime("%A")] += 1
    top_days = day_counts.most_common(3)

    # Common tags/topics
    all_tags = []
    for v in videos:
        all_tags.extend(v.get("tags", []))
    top_tags = [tag for tag, _ in Counter(all_tags).most_common(15)]

    # Average video duration
    durations = [parse_iso_duration(v["duration"]) for v in videos if v.get("duration")]
    avg_duration_sec = sum(durations) / len(durations) if durations else 0
    avg_duration_min = avg_duration_sec / 60

    report = {
        "channel": info,
        "analysis": {
            "videosAnalyzed": len(videos),
            "averageViews": round(avg_views),
            "averageLikes": round(avg_likes),
            "averageComments": round(avg_comments),
            "engagementRate": f"{engagement_rate:.2f}%",
            "postingFrequency": posting_frequency,
            "preferredDays": [{"day": d, "count": c} for d, c in top_days],
            "averageDurationMinutes": round(avg_duration_min, 1),
            "topTags": top_tags,
        },
        "topVideosByViews": [
            {
                "title": v["title"],
                "videoId": v["videoId"],
                "url": f"https://youtube.com/watch?v={v['videoId']}",
                "viewCount": v["viewCount"],
                "likeCount": v["likeCount"],
                "commentCount": v["commentCount"],
                "publishedAt": v["publishedAt"],
            }
            for v in top_by_views
        ],
        "recentUploads": [
            {
                "title": v["title"],
                "videoId": v["videoId"],
                "url": f"https://youtube.com/watch?v={v['videoId']}",
                "viewCount": v["viewCount"],
                "publishedAt": v["publishedAt"],
            }
            for v in videos[:5]
        ],
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="YouTube channel analysis")
    parser.add_argument("--channel-id", help="YouTube channel ID (UCxxxx)")
    parser.add_argument("--handle", help="YouTube @handle (e.g., @mkbhd)")
    parser.add_argument("--max-videos", type=int, default=20, help="Number of recent videos to analyze (default 20)")

    args = parser.parse_args()

    channel_id = args.channel_id
    if args.handle and not channel_id:
        channel_id = resolve_handle(args.handle)
        if not channel_id:
            print(json.dumps({"error": f"Could not find channel for handle: {args.handle}"}))
            sys.exit(1)

    if not channel_id:
        parser.print_help()
        sys.exit(1)

    report = analyze_channel(channel_id, max_videos=args.max_videos)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
