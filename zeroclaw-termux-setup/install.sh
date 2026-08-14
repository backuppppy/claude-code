#!/bin/bash
# ZeroClaw Termux Setup Installation Script
# Installs config and scripts to ~/.zeroclaw/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.zeroclaw"
SCRIPTS_DIR="${TARGET_DIR}/scripts"

echo "🚀 Installing ZeroClaw Termux Setup..."
echo "📍 Source: $SCRIPT_DIR"
echo "📍 Target: $TARGET_DIR"
echo ""

# Check if zeroclaw is installed
if ! command -v zeroclaw &> /dev/null; then
    echo "❌ zeroclaw not found in PATH"
    echo "   Install first: cargo install --path ~/zeroclaw"
    exit 1
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p "$SCRIPTS_DIR"
mkdir -p "${TARGET_DIR}/logs"

# Backup existing config if it exists
if [ -f "${TARGET_DIR}/config.toml" ]; then
    echo "⚠️  Backing up existing config..."
    cp "${TARGET_DIR}/config.toml" "${TARGET_DIR}/config.toml.backup"
fi

# Copy config
echo "📋 Installing config.toml..."
cp "${SCRIPT_DIR}/config.toml" "${TARGET_DIR}/config.toml"

# Copy scripts
echo "🔧 Installing scripts..."
cp "${SCRIPT_DIR}/scripts/"*.sh "${SCRIPTS_DIR}/"
chmod +x "${SCRIPTS_DIR}"/*.sh

# Copy aliases
echo "⚙️  Setting up aliases..."
if grep -q "zc-streams" ~/.bashrc 2>/dev/null; then
    echo "   ℹ️  Aliases already in ~/.bashrc"
else
    echo "   📝 Adding aliases to ~/.bashrc..."
    echo "" >> ~/.bashrc
    echo "# ZeroClaw aliases (installed by zeroclaw-termux-setup)" >> ~/.bashrc
    cat "${SCRIPT_DIR}/scripts/aliases.sh" >> ~/.bashrc
    source ~/.bashrc
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit config: nano ~/.zeroclaw/config.toml"
echo "      → Add your API key: sk-ant-api03-YOUR_KEY"
echo ""
echo "   2. Test: zcs"
echo "      → Should show: Claude Opus 5 + permissive"
echo ""
echo "   3. Try: zc \"בדוק את הרפוזיטוריים שלי\""
echo ""
echo "🎯 Available commands:"
echo "   zc \"<text>\"        — Send message to ZeroClaw"
echo "   zcstream \"<text>\"  — Streaming mode (auto-approve)"
echo "   zcgh               — List GitHub repos"
echo "   zcs                — Status check"
echo "   zcgit              — Git status"
