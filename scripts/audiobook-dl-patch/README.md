# audiobook-dl — פאץ' עקיפת המדף ל-Storytel

פאץ' ל-extractor של [audiobook-dl](https://github.com/jo1gi/audiobook-dl) (גרסה **0.7.3**)
שמאפשר להוריד ספר שמע מ-Storytel **בלי שהספר יהיה במדף** (bookshelf).

## הבעיה
ה-extractor המקורי (`audiobookdl/sources/storytel.py`) דורש שהספר יהיה במדף:
`download()` מושך את כל המדף (`getBookShelf.action`), מחפש בו את הספר, ואם הוא לא שם
זורק `MissingBookAccess`. לכן היה צריך "להוסיף למדף" לפני כל הורדה.

## הפתרון
התגלה endpoint שמחזיר את אותה רשומה בדיוק **בלי המדף**:

```
GET https://www.storytel.com/api/getBookInfoForContent.action?bookId=<book.id>&token=<singleSignToken>
```

מחזיר `slb` — מבנה **זהה לרשומת מדף** (`book`, `abook`, `owns`, `restriction`...),
כולל `book.AId` (program id לסטרימינג), `book.consumableId`, `abook.isbn` ומחברים/מקריאים.
עובד גם על ספרים שאינם במדף (`owns=0`).

### הערות מיפוי id
- ה-endpoint ממופתח ב-**book.id** (למשל `10517918`), **לא** ב-consumableId (`13457186`).
- המרה מ-consumableId ל-book.id:
  `GET https://api.storytel.net/book-details/consumables/<consumableId>` → שדה `bookId`.
- הפאץ' מנסה קודם את ה-id כ-bookId, ואם אין תוצאה — ממיר מ-consumableId. כך הוא עובד
  גם עם URL שמסתיים ב-book.id וגם עם URL שמסתיים ב-consumableId.
- (הצ'אפטרים דווקא ממופתחים ב-consumableId:
  `GET https://api.storytel.net/playback-metadata/consumable/<consumableId>` → `formats[abook].chapters`.)

## מה השתנה בקוד
- `download()` קורא ל-`get_book_info(book_id)` במקום `download_bookshelf()` + `find_book_info()`.
- נוספו: `get_book_info` / `_get_slb` / `_consumable_to_bookid`.
- ללא סודות בקוד — הקרדנציאלס נקראים מהקונפיג כמו במקור.

## התקנה
מחליפים את הקובץ בהתקנה של audiobook-dl (נתיב pipx לדוגמה):

```bash
TARGET=~/.local/share/pipx/venvs/audiobook-dl/lib/python3.13/site-packages/audiobookdl/sources/storytel.py
cp "$TARGET" "$TARGET.orig"          # גיבוי המקור
cp storytel.py "$TARGET"             # התקנת הגרסה המתוקנת
# לחלופין, החלה כ-diff מתוך תיקיית ה-sources:
#   patch -p1 < storytel-shelf-bypass.patch
```

## קבצים
- `storytel.py` — הקובץ המתוקן המלא (0.7.3).
- `storytel-shelf-bypass.patch` — diff אחיד מול המקור (`patch -p1`).

נבדק end-to-end דרך המחלקות האמיתיות: stream 206 `audio/mpeg`, 46 פרקים, מטא-דאטה מלא —
גם על ספר שלא במדף.
