#!/bin/bash
# Run arbitrary shell command via zeroclaw
# Usage: ./zc-cmd.sh "ls -la" or ./zc-cmd.sh "pwd && git status"

if [ -z "$1" ]; then
    echo "Usage: $0 \"<command>\""
    echo "Example: $0 \"ls -la\""
    exit 1
fi

COMMAND="$1"
echo "⚡ Running: $COMMAND"

zeroclaw agent -a agggeeeenttt -m "הרץ את הפקודה: $COMMAND" <<< "Y"
