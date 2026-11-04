#!/usr/bin/env bash
# Copy the splicelogic explainer animations (offline standalone HTMLs) into
# static/, where the pages under content/software/splicelogic/ embed them.
# Source: the local splicelogic-annimations project (not a git repo, so the
# copies are committed here). Rerun after rebuilding the standalones there.
#   bash scripts/sync-splicelogic-animations.sh [path/to/splicelogic-annimations]
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="${1:-../splicelogic-annimations}"
DEST=static/software/splicelogic/animations
mkdir -p "$DEST"

cp "$SRC/splicelogic-prepare-exons-standalone.html" "$DEST/prepare-exons.html"
cp "$SRC/splicelogic-event-types-standalone.html" "$DEST/event-types.html"
# Shown inline on the splicelogic page itself ({{< embed >}} in _index.md)
cp "$SRC/splicelogic-summary-standalone.html" "$DEST/summary.html"
for c in atss a5ss se mxe a3ss ri ates; do
  cp "$SRC/mini/splicelogic-mini-$c-standalone.html" "$DEST/mini-$c.html"
done
ls -la "$DEST"
