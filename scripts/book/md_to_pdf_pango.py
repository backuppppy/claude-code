#!/usr/bin/env python3
import re
import sys
from pathlib import Path

import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo


A4_WIDTH = 595.28
A4_HEIGHT = 841.89
MARGIN = 42
BODY_SIZE = 10
LINE_SPACING = 1.15


def chunk_text(text, max_chars=900):
    text = text.rstrip("\n")
    if not text:
        return [""]
    chunks = []
    while len(text) > max_chars:
        split_at = text.rfind(" ", 0, max_chars)
        if split_at < max_chars * 0.45:
            split_at = max_chars
        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()
    if text:
        chunks.append(text)
    return chunks


def block_style(line):
    match = re.match(r"^(#{1,6})\s+(.*)$", line)
    if not match:
        return line, "DejaVu Sans", BODY_SIZE, 4
    level = len(match.group(1))
    size = max(11, 17 - level)
    return match.group(2), "DejaVu Sans Bold", size, 8


def make_layout(context, text, font_family, size, width):
    layout = PangoCairo.create_layout(context)
    layout.set_text(text, -1)
    layout.set_width(int(width * Pango.SCALE))
    layout.set_wrap(Pango.WrapMode.WORD_CHAR)
    layout.set_alignment(Pango.Alignment.RIGHT)
    layout.set_auto_dir(True)
    layout.set_spacing(int((size * (LINE_SPACING - 1)) * Pango.SCALE))
    layout.set_font_description(Pango.FontDescription(f"{font_family} {size}"))
    return layout


def main():
    if len(sys.argv) != 3:
        print("Usage: md_to_pdf_pango.py input.md output.pdf", file=sys.stderr)
        return 2

    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    text = source.read_text(encoding="utf-8", errors="replace")

    surface = cairo.PDFSurface(str(target), A4_WIDTH, A4_HEIGHT)
    context = cairo.Context(surface)
    context.set_source_rgb(0, 0, 0)

    width = A4_WIDTH - (MARGIN * 2)
    bottom = A4_HEIGHT - MARGIN
    y = MARGIN

    def new_page():
        nonlocal y
        context.show_page()
        context.set_source_rgb(0, 0, 0)
        y = MARGIN

    for raw_line in text.splitlines():
        if not raw_line.strip():
            y += 8
            if y > bottom:
                new_page()
            continue

        display, font, size, after = block_style(raw_line)
        for chunk in chunk_text(display):
            layout = make_layout(context, chunk, font, size, width)
            _, logical = layout.get_extents()
            height = logical.height / Pango.SCALE

            if y + height > bottom and y > MARGIN:
                new_page()

            context.move_to(MARGIN, y)
            PangoCairo.show_layout(context, layout)
            y += height + after

    surface.finish()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
