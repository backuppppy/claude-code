import json
import re
from datetime import datetime
from fpdf import FPDF

INPUT = "/storage/emulated/0/Download/AyuGram/your_posts_check_ins_photos_and_videos_1.json"
OUTPUT = "/storage/emulated/0/Download/הספר_שלי.pdf"
FONT_HEB = "/system/fonts/NotoSansHebrew-Regular.ttf"
FONT_HEB_BOLD = "/system/fonts/NotoSansHebrew-Bold.ttf"
FONT_LAT = "/system/fonts/Roboto-Regular.ttf"


def fix_encoding(text):
    try:
        return text.encode("latin1").decode("utf-8")
    except Exception:
        return text


def clean_text(text):
    # הסר תווי RTL/LTR ותווי בקרה
    text = re.sub(r"[‎‏‪‫‬‭‮⁦⁧⁨⁩]", "", text)
    # הסר תווי בקרה אחרים (מלבד שורה חדשה וטאב)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()


def format_date(ts):
    try:
        return datetime.fromtimestamp(ts).strftime("%d/%m/%Y")
    except Exception:
        return ""


with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

# אסוף פוסטים עם טקסט בסדר המקורי
posts = []
for item in data:
    for d in item.get("data", []):
        if "post" in d:
            text = fix_encoding(d["post"])
            text = clean_text(text)
            if text:
                posts.append({
                    "timestamp": item.get("timestamp", 0),
                    "text": text,
                })
            break

print(f"סה\"כ פוסטים: {len(posts)}")


class BookPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("Hebrew", size=9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, str(self.page_no()), align="C")
        self.set_text_color(0, 0, 0)


pdf = BookPDF()
pdf.add_font("Hebrew", style="", fname=FONT_HEB)
pdf.add_font("Hebrew", style="B", fname=FONT_HEB_BOLD)
pdf.add_font("Latin", style="", fname=FONT_LAT)
pdf.set_fallback_fonts(["Latin"])
pdf.set_right_margin(15)
pdf.set_left_margin(15)
pdf.set_auto_page_break(auto=True, margin=20)

# שער
pdf.add_page()
pdf.set_font("Hebrew", style="B", size=28)
pdf.ln(60)
pdf.cell(0, 20, "הספר שלי", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Hebrew", size=14)
pdf.ln(10)
pdf.cell(0, 10, f"{len(posts)} פוסטים", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Hebrew", size=12)
pdf.ln(5)
if posts:
    first_date = format_date(posts[-1]["timestamp"])
    last_date = format_date(posts[0]["timestamp"])
    pdf.cell(0, 10, f"{first_date} — {last_date}", align="C")

# פוסטים
for i, post in enumerate(posts):
    pdf.add_page()

    # תאריך
    date_str = format_date(post["timestamp"])
    pdf.set_font("Hebrew", size=10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, date_str, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)

    pdf.ln(3)

    # טקסט הפוסט
    pdf.set_font("Hebrew", size=13)
    pdf.multi_cell(0, 8, post["text"], align="R")

    if i % 50 == 0:
        print(f"  עיבוד {i}/{len(posts)}...")

print("שומר PDF...")
pdf.output(OUTPUT)
print(f"נשמר בהצלחה: {OUTPUT}")
