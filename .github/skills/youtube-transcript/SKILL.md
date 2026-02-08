---
name: youtube-transcript
description: Fetch YouTube video transcripts and metadata. Use when the user shares a YouTube link, wants context on a video they watched, or needs a video transcribed.
argument-hint: <youtube-url> [language]
---

Fetch a YouTube video's transcript and metadata so you have full context on what the user watched.

## Usage

Run the fetch script with the provided URL:

```bash
python3 .github/skills/youtube-transcript/scripts/fetch-transcript.py "$ARGUMENTS"
```

Uses only Python stdlib — no pip install or dependencies needed.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| URL or video ID | Yes | YouTube URL (`youtube.com/watch?v=...`, `youtu.be/...`) or bare video ID |
| `--lang CODE` | No | Language code (default: `en`). Example: `--lang es` |
| `--timed` | No | Include timestamps in output |

## Examples

```bash
# Basic transcript
python3 .github/skills/youtube-transcript/scripts/fetch-transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Spanish transcript
python3 .github/skills/youtube-transcript/scripts/fetch-transcript.py "https://youtu.be/dQw4w9WgXcQ" --lang es

# With timestamps
python3 .github/skills/youtube-transcript/scripts/fetch-transcript.py "dQw4w9WgXcQ" --timed
```

## Output

The script prints video metadata followed by the full transcript:

```
# Video: <title>
Channel: <channel>
Duration: <duration>
Language: <lang>
URL: <url>
Available languages: <list>

## Transcript
<full transcript text>
```

## How It Works

Uses YouTube's innertube API (same as the Android app) to fetch caption data directly. No API key, no pip packages, no authentication needed.

## Notes

- Default language is English; specify `--lang` for other languages
- Falls back to English, then first available language if requested language not found
- If no transcript is available, the script reports an error
