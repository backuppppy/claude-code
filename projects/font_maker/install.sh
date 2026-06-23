#!/bin/bash
set -e
echo "=== Font Maker — Installing dependencies ==="

PIP_FLAGS="--break-system-packages --quiet"

pip install $PIP_FLAGS Pillow numpy fonttools

pip install $PIP_FLAGS PyMuPDF 2>/dev/null \
    && echo "PyMuPDF installed  ✓  (PDF support enabled)" \
    || echo "PyMuPDF not available — PDF support disabled (image & drawing still work)"

echo ""
echo "=== Done! Run with: ==="
echo "  python3 font_maker.py"
echo "  python3 font_maker.py myimage.png   # auto-open segmentation dialog"
echo "  python3 font_maker.py document.pdf  # auto-open PDF dialog"
