#!/bin/bash
# List GitHub repositories using zeroclaw
# Usage: ./zc-gh.sh

echo "🔍 Checking GitHub repositories..."

zeroclaw agent -a agggeeeenttt -m "הרץ את הפקודה: gh repo list --limit 100 --source all" <<< "Y"

echo ""
echo "📊 Summary:"
gh repo list --limit 100 --source all | wc -l
