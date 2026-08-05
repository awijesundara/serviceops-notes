#!/usr/bin/env bash
# Mirrors docs/API_REFERENCE.md (maintained original, private repo) into the
# sibling ServiceOps repo's docs/API_REFERENCE.md (public, byte-identical
# copy). Run this in the same change as any API_REFERENCE.md edit -- see
# CLAUDE.md's "Documentation control" section for why this file specifically
# is the one deliberate public carve-out.
set -euo pipefail
cd "$(dirname "$0")/.."
SERVICEOPS_ROOT="${SERVICEOPS_REPO:-$(pwd)/../ServiceOps}"
SOURCE="docs/API_REFERENCE.md"
DEST="$SERVICEOPS_ROOT/docs/API_REFERENCE.md"

if [ ! -d "$SERVICEOPS_ROOT" ]; then
  echo "error: ServiceOps repo not found at $SERVICEOPS_ROOT (set SERVICEOPS_REPO)" >&2
  exit 1
fi

cp "$SOURCE" "$DEST"
echo "Synced $SOURCE -> $DEST"
