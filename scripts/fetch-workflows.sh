#!/usr/bin/env bash
# Download the rendered workflow HTMLs from the (public) splicelogic-paper repo
# into static/ so they're always the latest pushed versions.
# Run by the deploy workflow before `hugo`; run it locally before `hugo server`.
set -euo pipefail

REPO_RAW='https://raw.githubusercontent.com/beamimc/splicelogic-paper/main'
DEST="$(cd "$(dirname "$0")/.." && pwd)/static/projects/ptbp1-splicelogic"

mkdir -p "$DEST"
for f in RBP_workflow.html NovelTxps_workflow.html; do
  echo "Fetching workflows/$f"
  curl -fsSL "$REPO_RAW/workflows/$f" -o "$DEST/$f"
done
