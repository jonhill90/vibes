#!/bin/bash
# Screenshot with resolution presets

URL="$1"
PRESET="${2:-hd}"

case "$PRESET" in
    "mobile"|"phone")
        echo "Taking mobile screenshot (375x667)..."
        WIDTH=375 HEIGHT=667 ./tools/visual/take-screenshot.sh "$URL"
        ;;
    "tablet")
        echo "Taking tablet screenshot (768x1024)..."
        WIDTH=768 HEIGHT=1024 ./tools/visual/take-screenshot.sh "$URL"
        ;;
    "hd"|"desktop")
        echo "Taking HD desktop screenshot (1920x1080)..."
        WIDTH=1920 HEIGHT=1080 ./tools/visual/take-screenshot.sh "$URL"
        ;;
    "2k"|"desktop-hi")
        echo "Taking 2K screenshot (2560x1440)..."
        WIDTH=2560 HEIGHT=1440 ./tools/visual/take-screenshot.sh "$URL"
        ;;
    "4k"|"desktop-4k")
        echo "Taking 4K screenshot (3840x2160)..."
        WIDTH=3840 HEIGHT=2160 ./tools/visual/take-screenshot.sh "$URL"
        ;;
    "fullpage")
        echo "Taking full page screenshot..."
        FULL_PAGE=true ./tools/visual/take-screenshot.sh "$URL"
        ;;
    *)
        echo "Usage: $0 <URL> [preset]"
        echo "Available presets:"
        echo "  mobile/phone     - 375x667 (iPhone)"
        echo "  tablet           - 768x1024 (iPad)"
        echo "  hd/desktop       - 1920x1080 (default)"
        echo "  2k/desktop-hi    - 2560x1440"
        echo "  4k/desktop-4k    - 3840x2160"
        echo "  fullpage         - Full page capture (800px width)"
        echo ""
        echo "Custom resolution: WIDTH=1280 HEIGHT=800 ./tools/visual/take-screenshot.sh <URL>"
        echo "Full page: FULL_PAGE=true ./tools/visual/take-screenshot.sh <URL>"
        exit 1
        ;;
esac
