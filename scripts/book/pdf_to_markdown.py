#!/usr/bin/env python3
import sys
from pypdf import PdfReader

pdf_path = "/storage/emulated/0/Download/Librera/הספר_שלי.pdf"
output_path = "/storage/emulated/0/Download/Librera/הספר_שלי.md"

print(f"פותח קובץ: {pdf_path}")
reader = PdfReader(pdf_path)
total = len(reader.pages)
print(f"סה\"כ עמודים: {total}")

lines = []
# RTL direction marker for the whole document
lines.append('<div dir="rtl">\n')
lines.append("# הספר שלי\n")

for i, page in enumerate(reader.pages):
    if i % 100 == 0:
        print(f"מעבד עמוד {i+1}/{total}...")
    text = page.extract_text()
    if text and text.strip():
        lines.append(f"\n---\n*עמוד {i+1}*\n")
        lines.append(text.strip())
        lines.append("\n")

lines.append("\n</div>")

with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\nהסתיים! הקובץ נשמר ב: {output_path}")
