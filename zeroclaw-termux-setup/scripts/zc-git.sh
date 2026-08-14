#!/bin/bash
# Check git status via zeroclaw
# Usage: ./zc-git.sh [repo_path]

REPO_PATH="${1:-.}"

echo "🔧 Git status for: $REPO_PATH"

zeroclaw agent -a agggeeeenttt -m "בתיקייה $REPO_PATH הרץ: git status && git log --oneline -5" <<< "Y"
