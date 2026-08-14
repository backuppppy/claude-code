#!/bin/bash
# ZeroClaw Aliases for quick access
# Source this in ~/.bashrc: source ~/.zeroclaw/scripts/aliases.sh

# Check if zeroclaw is installed
if ! command -v zeroclaw &> /dev/null; then
    echo "Warning: zeroclaw not found in PATH"
    echo "Install: cargo install --path ~/zeroclaw"
    return 1
fi

# Basic aliases
alias zcs="zeroclaw status"
alias zcls="zeroclaw workspace list"
alias zcgit="zeroclaw workspace execute -- git status"

# Send message to ZeroClaw (Hebrew supported)
alias zc='zeroclaw agent -a agggeeeenttt -m'

# Streaming mode (auto-approve)
alias zcstream='zeroclaw agent -a agggeeeenttt -m --stream'

# GitHub repos check
alias zcgh='~/.zeroclaw/scripts/zc-gh.sh'

# Git status via ZeroClaw
alias zcgitcheck='~/.zeroclaw/scripts/zc-git.sh'

# Run command via ZeroClaw
alias zccmd='~/.zeroclaw/scripts/zc-cmd.sh'
