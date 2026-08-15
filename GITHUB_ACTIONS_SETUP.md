# GitHub Actions Setup - הרץ בוט בחינם

## 🚀 איך להגדיר

### שלב 1: הוסף Secrets ל-GitHub

1. **עבור לריפו שלך:**
   ```
   https://github.com/backuppppy/claude-code
   ```

2. **Settings → Secrets and variables → Actions**

3. **New repository secret** - הוסף 2 סודות:

   **Secret 1: TELEGRAM_BOT_TOKEN**
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: `8867679619:AAEHgXKMBhp_zBtB3eBRE8NS-NiNqk2YLUg`
   - Click: Add secret

   **Secret 2: TELEGRAM_CHAT_ID**
   - Name: `TELEGRAM_CHAT_ID`
   - Value: `<את ה-chat ID שלך>`
   - Click: Add secret

### שלב 2: אפשר GitHub Actions

1. **Settings → Actions → General**
2. **"Allow all actions and reusable workflows"**
3. **Save**

### שלב 3: בדוק את ה-Workflow

1. **עבור ל-Actions tab**
2. **בחר "FXP Bot - Continuous Monitoring"**
3. **Click "Run workflow" → "Run workflow"**

---

## 📊 מה הWorkflow עושה

### הרצה אוטומטית
- **כל 5 דקות** - כל דקה ודקה, הגיטהאב יריץ את הבוט
- **משך כל הרצה:** ~1-2 דקות
- **חופשי:** ✅ 2,000 דקות חינם/חודש

### בהרצה אחת:
1. 🔍 Clone הריפו
2. 🐍 Setup Python 3.11
3. 📦 התקן dependencies
4. 🧪 הרץ בדיקות (4 test files)
5. 🤖 הרץ את ה-FXP Bot (פעם אחת)
6. 💾 עדכן את database
7. 📤 דחוף לGitHub

---

## 🎯 השלבים בקצרה

### עבור לגיטהאב:
```
https://github.com/YOUR_USERNAME/claude-code
↓
Settings
↓
Secrets and variables → Actions
↓
New repository secret
↓
הוסף TELEGRAM_BOT_TOKEN
↓
הוסף TELEGRAM_CHAT_ID
↓
Save
```

### בדוק שהכל עובד:
```
Actions tab
↓
FXP Bot - Continuous Monitoring
↓
Run workflow
↓
ראה את ההרצה בזמן אמת
```

---

## 📈 Monitoring

### ראה את ההרצות:
1. **Actions tab**
2. **FXP Bot - Continuous Monitoring**
3. **Click על הרצה כלשהי**
4. **בדוק Logs**

### Logs כוללים:
- ✅ בדיקות עברו/נכשלו
- 🔍 כמה שאלות נמצאו
- 📬 כמה הודעות נשלחו
- ⚠️ שגיאות אם היו

---

## 💾 בסיס הנתונים

### זה מה שקורה:
1. **כל הרצה:** יוצרת/מעדכנת את `fxp_askol.db`
2. **Database נשמר** בגיטהאב כ-commit
3. **עתידות הרצות:** קוראות מה-DB ממקודם
4. **תוצאה:** אין דופליקט הודעות

### בדוק את Database:
```bash
git pull  # משוך את ה-DB העדכני
sqlite3 projects/fxp-askol-telegram/fxp_askol.db
SELECT COUNT(*) FROM processed_questions;
SELECT * FROM monitoring_log LIMIT 5;
```

---

## 🔔 קבל הודעות

### אם יש שגיאה:
- GitHub שולח email
- Telegram שולח הודעה (דרך ה-bot)
- GitHub Actions זורק סימן אדום

### אם הכל בסדר:
- ✅ Green checkmark ב-Actions
- ✅ הודעה בטלגרם עבור כל שאלה חדשה

---

## 💰 עלות

### GitHub Actions Free Tier:
- **חודשי:** 2,000 דקות בחינם
- **שלנו צורך:** ~10 דקות/שעה × 24 = 240 דקות/יום
- **סה״כ חודשי:** ~7,200 דקות
- **עלות:** ~$0.25/חודש (paid minutes)

### או לשמור בחינם:
- שנה את interval ל-30 דקות: `*/30 * * * *`
- שנה ל-hourly: `0 * * * *`
- שנה למרים ביום: `0 9,15,21 * * *`

---

## 🎮 Manual Trigger

### הרץ ידנית בכל זמן:

1. **Actions tab**
2. **FXP Bot - Continuous Monitoring**
3. **"Run workflow" → "Run workflow"**

---

## 📝 דוגמה: Workflow Run

```
FXP Bot Monitoring #42
Duration: 1m 23s

Logs:
- ✅ Clone Repository (5s)
- ✅ Setup Python (8s)
- ✅ Install Dependencies (15s)
- ✅ Run Tests (20s)
  - Scraper: 5/5 ✓
  - Database: 5/5 ✓
  - Telegram: 5/5 ✓
  - Integration: 6/6 ✓
- ✅ Run FXP Bot (10s)
  - Found 15 questions
  - 3 new questions
  - Sent 3 notifications ✓
- ✅ Commit Database Changes (3s)
- ✅ Push Changes (2s)

Result: ✅ SUCCESS
```

---

## 🚨 Troubleshooting

### "Secrets not found"
```
→ בדוק Settings → Secrets
→ וודא ש-TELEGRAM_BOT_TOKEN קיים
→ וודא ש-TELEGRAM_CHAT_ID קיים
```

### "Auth failed"
```
→ בדוק שהטוקן הוא נכון
→ וודא שלבוט יש permission לשלוח הודעות
```

### "Database conflict"
```
→ GitHub Actions pushes DB
→ אם pushed ידנית גם, עלול להיות conflict
→ Pull לפני push
```

### "Tests failing"
```
→ בדוק logs בActions
→ ראה בדיוק איזה test נכשל
→ Debug ב-local (python test_*.py)
```

---

## ✅ Checklist

- [ ] Forked/Cloned הריפו
- [ ] הוספת TELEGRAM_BOT_TOKEN ל-Secrets
- [ ] הוספת TELEGRAM_CHAT_ID ל-Secrets
- [ ] GitHub Actions מאופשרות
- [ ] Ran workflow ידנית וביצע בהצלחה
- [ ] ✅ Setup Complete!

---

## 🎉 עכשיו:

**הבוט שלך רץ אוטומטי בGitHub!**

- ✅ כל 5 דקות: בדוק שאלות חדשות
- ✅ שלח הודעות לטלגרם
- ✅ עדכן את database
- ✅ חינם לחלוטין!

```bash
# כל מה שצריך לעשות:
git add .github/workflows/fxp-bot.yml
git commit -m "Add GitHub Actions workflow"
git push origin main
```

**Done!** 🚀
