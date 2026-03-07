#!/bin/bash
# Auto-push goal files to GitHub after local changes
cd ~/goals || exit 1

# Skip if no changes
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  exit 0
fi

git add -A
git commit -m "auto-sync: $(date '+%Y-%m-%d %H:%M')" --quiet 2>/dev/null
git push --quiet 2>/dev/null
