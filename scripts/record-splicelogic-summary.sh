#!/usr/bin/env bash
# Record the splicelogic summary animation to a silent looping MP4 (shown like a
# GIF on the splicelogic page via {{< embed doc="...mp4" >}}), plus its poster.
# Needs Google Chrome, Node 22+ and ffmpeg. Rerun after rebuilding the
# standalone in ../splicelogic-annimations.
#   bash scripts/record-splicelogic-summary.sh [path/to/splicelogic-annimations]
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="${1:-../splicelogic-annimations}/splicelogic-summary-standalone.html"
DEST=static/software/splicelogic/animations
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
node scripts/record-animation.mjs "$SRC" "$TMP" 30
ffmpeg -y -loglevel error -framerate 30 -i "$TMP/f%05d.png" -c:v libx264 -preset slow -crf 22 \
  -pix_fmt yuv420p -movflags +faststart -an "$DEST/summary.mp4"
# Poster: a frame near the end (19.5s), when the events table is full
ffmpeg -y -loglevel error -i "$TMP/f00585.png" -vf scale=1280:-1 -q:v 3 "$DEST/summary-poster.jpg"
ls -la "$DEST"/summary*
