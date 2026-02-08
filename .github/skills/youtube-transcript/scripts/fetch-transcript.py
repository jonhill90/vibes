#!/usr/bin/env python3
"""Fetch YouTube video transcript using only Python stdlib. No pip install needed."""

import sys
import re
import json
import argparse
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
INNERTUBE_CONTEXT = {"client": {"clientName": "ANDROID", "clientVersion": "20.10.38"}}


def extract_video_id(url_or_id):
    """Extract video ID from various YouTube URL formats or bare ID."""
    patterns = [
        r"(?:youtube\.com/watch\?.*v=)([\w-]{11})",
        r"(?:youtu\.be/)([\w-]{11})",
        r"(?:youtube\.com/embed/)([\w-]{11})",
        r"(?:youtube\.com/v/)([\w-]{11})",
        r"(?:youtube\.com/shorts/)([\w-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    if re.match(r"^[\w-]{11}$", url_or_id):
        return url_or_id
    return None


def _http_get(url):
    """Make an HTTP GET request and return the response body as string."""
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _http_post_json(url, payload):
    """Make an HTTP POST request with JSON body and return parsed JSON."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def fetch_video_data(video_id):
    """Fetch video details and caption tracks via YouTube's innertube API."""
    # Step 1: Get the watch page to extract the innertube API key
    html = _http_get(f"https://www.youtube.com/watch?v={video_id}")

    match = re.search(r'"INNERTUBE_API_KEY":\s*"([a-zA-Z0-9_-]+)"', html)
    if not match:
        print("Error: Could not extract YouTube API key. The video may be unavailable.", file=sys.stderr)
        sys.exit(1)
    api_key = match.group(1)

    # Step 2: Call innertube API with Android client to get caption URLs
    innertube_url = f"https://www.youtube.com/youtubei/v1/player?key={api_key}"
    data = _http_post_json(innertube_url, {
        "context": INNERTUBE_CONTEXT,
        "videoId": video_id,
    })

    # Extract video info
    details = data.get("videoDetails", {})
    info = {
        "title": details.get("title", "Unknown"),
        "channel": details.get("author", "Unknown"),
        "duration_seconds": int(details.get("lengthSeconds", 0)),
    }

    # Extract caption tracks
    captions = data.get("captions", {}).get("playerCaptionsTracklistRenderer", {})
    tracks = captions.get("captionTracks", [])

    return info, tracks


def select_track(tracks, lang):
    """Select the best matching caption track for the requested language."""
    # Try exact match
    for track in tracks:
        if track.get("languageCode") == lang:
            return track
    # Try English fallback
    if lang != "en":
        for track in tracks:
            if track.get("languageCode") == "en":
                return track
    # Fall back to first available
    if tracks:
        return tracks[0]
    return None


def fetch_transcript(track_url, timed=False):
    """Fetch and parse a transcript from a caption track URL."""
    clean_url = track_url.replace("&fmt=srv3", "")
    xml_text = _http_get(clean_url)
    root = ET.fromstring(xml_text)

    lines = []
    for elem in root.iter("text"):
        text = re.sub(r"<[^>]*>", "", unescape(elem.text or "")).strip()
        if not text:
            continue
        if timed:
            start = float(elem.get("start", 0))
            minutes = int(start // 60)
            seconds = int(start % 60)
            lines.append(f"[{minutes:02d}:{seconds:02d}] {text}")
        else:
            lines.append(text)

    return "\n".join(lines)


def format_duration(seconds):
    """Format seconds into human-readable duration."""
    if seconds <= 0:
        return "Unknown"
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"


def track_language_name(track):
    """Extract the display name from a caption track."""
    name = track.get("name", {})
    if isinstance(name, dict):
        runs = name.get("runs")
        if runs and isinstance(runs, list):
            return runs[0].get("text", "Unknown")
        return name.get("simpleText", "Unknown")
    return str(name)


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube video transcript")
    parser.add_argument("url", help="YouTube URL or video ID")
    parser.add_argument("--lang", default="en", help="Language code (default: en)")
    parser.add_argument("--timed", action="store_true", help="Include timestamps")
    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    if not video_id:
        print(f"Error: Could not extract video ID from '{args.url}'", file=sys.stderr)
        sys.exit(1)

    info, tracks = fetch_video_data(video_id)

    if not tracks:
        print("Error: No captions found for this video.", file=sys.stderr)
        sys.exit(1)

    track = select_track(tracks, args.lang)
    if not track:
        print(f"Error: No transcript found for language '{args.lang}'.", file=sys.stderr)
        sys.exit(1)

    transcript = fetch_transcript(track["baseUrl"], timed=args.timed)

    lang_name = track_language_name(track)
    lang_code = track.get("languageCode", "??")
    kind = "auto-generated" if track.get("kind") == "asr" else "manual"

    print(f"# Video: {info['title']}")
    print(f"Channel: {info['channel']}")
    print(f"Duration: {format_duration(info['duration_seconds'])}")
    print(f"Language: {lang_name} ({lang_code}, {kind})")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")
    if len(tracks) > 1:
        available = [
            f"{track_language_name(t)} ({t.get('languageCode', '?')})"
            for t in tracks
        ]
        print(f"Available languages: {', '.join(available)}")
    print()
    print("## Transcript")
    print()
    print(transcript)


if __name__ == "__main__":
    main()
