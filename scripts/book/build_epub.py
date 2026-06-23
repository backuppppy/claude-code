#!/usr/bin/env python3
import re
from collections import Counter
from ebooklib import epub

# ── 1. Remove emojis ──────────────────────────────────────────────────────────
EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F700-\U0001F77F"  # alchemical
    "\U0001F780-\U0001F7FF"  # geometric extended
    "\U0001F800-\U0001F8FF"  # supplemental arrows-c
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA00-\U0001FA6F"  # chess symbols
    "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"  # enclosed characters
    "\U0001F004-\U0001F0CF"  # mahjong / playing cards
    "☀-⛿"          # misc symbols
    "✀-➿"          # dingbats block
    "︀-️"          # variation selectors
    "‍"                 # zero width joiner
    "⃣"                 # combining enclosing keycap
    "]+",
    flags=re.UNICODE,
)

def strip_emojis(text):
    return EMOJI_RE.sub('', text).strip()

# ── 2. Load posts ─────────────────────────────────────────────────────────────
with open('/root/all_posts.txt', 'r', encoding='utf-8') as f:
    raw = f.read()

blocks = re.split(r'===POST_\d+===', raw)
posts = []
for block in blocks:
    text = strip_emojis(block.strip())
    if len(text) >= 300:
        posts.append(text)

print(f"Loaded {len(posts)} posts (>=300 chars after emoji removal)")

# ── 3. Classify posts ─────────────────────────────────────────────────────────
CHAPTERS = [
    {
        'name': 'על הכתיבה',
        'keywords': ['כתיבה','כותב','לכתוב','מחברת','פוסט','כתב את','הכתיבה עושה','לכתוב כל יום',
                     'לכתוב בחוץ','לכתוב בחוף','הכתיבה שלי','כתיבה משחררת','כתיבה גורמת',
                     'לכתוב ברגל','פסיכולוג הציע לכתוב'],
    },
    {
        'name': 'הרגישות שלי',
        'keywords': ['רגיש מאוד','אדם רגיש','רגישות','HSP','הספר אדם רגיש','הרגשות שלי',
                     'מרגיש מותקף','מרגיש פגוע','רגש','שפת הרגש','כאב לי','הכאיב לי',
                     'קשה לי להרגיש','הרגשה קשה','מרגיש רע מעצמי'],
    },
    {
        'name': 'עבודה עם ילדים מיוחדים',
        'keywords': ['אוטיסט','ילדים מיוחדים','דיירים','דייר','מדריך','בית הספר','הוסטל',
                     'רכז','הילד','ילד אחד','ילד חדש','בית ספר','דירה ב','דירה ק',
                     'ילד עם חרדות','הילדים','ישנים בדירה'],
    },
    {
        'name': 'משפחה',
        'keywords': ['אימא שלי','אבא שלי','אח שלי','אחות שלי','הורים שלי','משפחה שלי',
                     'אחים שלי','אחותי','בית ההורים','ליל שבת','סעודה','משפחה',
                     'אחי','האחים','בבית ההורים'],
    },
    {
        'name': 'בדידות וחיפוש קשר',
        'keywords': ['בדידות','בודד','חסר','חסך','חיבוק','אין לי חברים','אין לי עם מי',
                     'מתגעגע','להכיר אנשים','קשר זוגי','בחורה','אהבה','בודד בעולם',
                     'הרגשת חוסר','בודדות'],
    },
    {
        'name': 'ימים קשים',
        'keywords': ['למות','לא רוצה לקום','מחשבות שליליות','דיכאון','יאוש','לא רוצה לחיות',
                     'עדיף לא להיות קיים','רוצה למות','חשבתי למות','חשבתי שעדיף',
                     'אין לי סיבה לחיות','אין למה לקום','אין סיבה לחיים','ימים קשים',
                     'מחשבות קשות','חושב שאין לי תיקוה'],
    },
    {
        'name': 'אמונה ורוחניות',
        'keywords': ['ברסלב','ליקוטי','ישיבה','שבת','תורה','תפילה','בעזרת השם','ברוך השם',
                     'הרמב"ם','יהדות','אמונה','השם','ספר מוסר','חגים','ראש השנה',
                     'יום כיפור','סוכות','חנוכה','ליקוטי עיצות','ליקוטי עצות'],
    },
    {
        'name': 'עצמאות ועתיד',
        'keywords': ['לעזוב את הבית','עצמאות','ללמוד אנגלית','סייבר','האקינג','לימודים',
                     'עתיד שלי','תוכניות','לגדול','חלומות','רוצה להתקדם','לקבל דירה',
                     'לצאת מבית ההורים','מגורים','עסק'],
    },
    {
        'name': 'מחשבות על החיים',
        'keywords': ['מחשבה על','חשבתי על','להתבונן','חשבון נפש','הבנתי ש','מסקנה',
                     'הרהורים','תחושה ש','עניין של','לחשוב על זה','חשבתי לעצמי',
                     'מה שלמדתי','נרקסיזם','פסיכולוגיה','דפוסי חשיבה','מחשבות על'],
    },
]
DEFAULT_CHAPTER = 'יומיום'

def score(text, kws):
    return sum(text.count(k) for k in kws)

classified = []
for text in posts:
    scores = [score(text, ch['keywords']) for ch in CHAPTERS]
    best = max(range(len(scores)), key=lambda i: scores[i])
    chapter = CHAPTERS[best]['name'] if scores[best] > 0 else DEFAULT_CHAPTER
    classified.append({'text': text, 'chapter': chapter})

counts = Counter(p['chapter'] for p in classified)
for ch in CHAPTERS:
    print(f"  {ch['name']}: {counts.get(ch['name'], 0)}")
print(f"  {DEFAULT_CHAPTER}: {counts.get(DEFAULT_CHAPTER, 0)}")

# ── 4. Build EPUB ─────────────────────────────────────────────────────────────
book = epub.EpubBook()
book.set_identifier('sefer-bezalel-001')
book.set_title('ספר בצלאל')
book.set_language('he')
book.add_author('בצלאל')

CSS = '''
body {
    direction: rtl;
    text-align: right;
    font-family: "David", "Times New Roman", serif;
    font-size: 1em;
    line-height: 1.7;
    margin: 1.5em 2em;
    color: #1a1a1a;
}
h1.book-title {
    font-size: 2.5em;
    color: #1a1a8c;
    text-align: center;
    margin-top: 3em;
}
h2.chapter-title {
    font-size: 1.6em;
    color: #1a1a8c;
    border-bottom: 2px solid #1a1a8c;
    padding-bottom: 0.3em;
    margin-top: 2em;
}
.post {
    margin-bottom: 1.5em;
    padding-bottom: 1em;
    border-bottom: 1px solid #ccc;
}
'''

style = epub.EpubItem(
    uid='style',
    file_name='style/main.css',
    media_type='text/css',
    content=CSS.encode('utf-8'),
)
book.add_item(style)

# Title page
title_html = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="he" dir="rtl">
<head><meta charset="utf-8"/><title>ספר בצלאל</title>
<link rel="stylesheet" href="../style/main.css"/></head>
<body><h1 class="book-title">ספר בצלאל</h1></body>
</html>'''

title_chapter = epub.EpubHtml(title='ספר בצלאל', file_name='title.xhtml', lang='he')
title_chapter.content = title_html.encode('utf-8')
title_chapter.add_item(style)
book.add_item(title_chapter)

spine = ['nav', title_chapter]
toc = []

chapter_order = [ch['name'] for ch in CHAPTERS] + [DEFAULT_CHAPTER]
for ch_name in chapter_order:
    ch_posts = [p['text'] for p in classified if p['chapter'] == ch_name]
    if not ch_posts:
        continue

    posts_html = ''.join(
        f'<div class="post"><p>{post.replace(chr(10), "<br/>")}</p></div>'
        for post in ch_posts
    )

    html = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="he" dir="rtl">
<head><meta charset="utf-8"/><title>{ch_name}</title>
<link rel="stylesheet" href="../style/main.css"/></head>
<body>
<h2 class="chapter-title">{ch_name}</h2>
{posts_html}
</body>
</html>'''

    slug = ch_name.replace(' ', '_').replace('"', '')
    epub_ch = epub.EpubHtml(title=ch_name, file_name=f'ch_{slug}.xhtml', lang='he')
    epub_ch.content = html.encode('utf-8')
    epub_ch.add_item(style)
    book.add_item(epub_ch)
    spine.append(epub_ch)
    toc.append(epub.Link(f'ch_{slug}.xhtml', ch_name, slug))

book.toc = toc
book.spine = spine
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

out_path = '/root/sefer_bezalel.epub'
epub.write_epub(out_path, book)
print(f"\nSaved: {out_path}")
print(f"Total posts: {len(classified)}")
