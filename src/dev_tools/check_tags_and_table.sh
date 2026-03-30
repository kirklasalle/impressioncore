#!/bin/bash
# check_tags_and_table.sh
# ImpressionCore CI/CD tag health and table regeneration script
# Usage: bash check_tags_and_table.sh

set -e

# Step 1: Run tag updater
echo "[CI] Running tag updater..."
python docs/developer/add_or_update_tags.py --auto

# Step 2: Regenerate tag table
echo "[CI] Regenerating tag table..."
python docs/developer/tags_index.py --table --sort --wrap 6

# Step 3: Check for uncommitted changes (git diff --exit-code returns 1 if there are changes)
echo "[CI] Checking for uncommitted changes (tags or tag table updates)..."
git diff --exit-code docs/ src/ || {
  echo "[CI] ERROR: Tag updates or tag table changes detected. Please commit these changes." >&2
  exit 1
}

echo "[CI] Tag health and table check passed."
exit 0
