# ZeroClaw על Android/Termux — מדריך הקמה וxnintegration

**עדכון:** 2 באוגוסט 2026

## 📋 תוכן עניינים
1. [מה זה ZeroClaw?](#מה-זה-zeroclaw)
2. [דרישות חומרה](#דרישות-חומרה)
3. [תהליך ההקמה](#תהליך-ההקמה)
4. [מיגרציה מ-Ollama ל-Claude API](#מיגרציה-מ-ollama-ל-claude-api)
5. [תצורה סופית](#תצורה-סופית)
6. [אינטגרציית GitHub](#אינטגרציית-github)
7. [שימוש ב-ZeroClaw](#שימוש-ב-zeroclaw)

---

## מה זה ZeroClaw?

**ZeroClaw** הוא סוכן AI אגנטי (agentic AI assistant) קטן וחזק שנבנה בRust.

### יכולות:
- ✅ הרצת פקודות shell
- ✅ עבודה עם git ו-GitHub
- ✅ קריאה וכתיבה של קבצים
- ✅ ממשק אינטראקטיבי עם אישורים
- ✅ תמיכה מלאה בעברית
- ✅ בינארי קטן (34MB)

### מיקום:
https://github.com/zeroclaw-labs/zeroclaw

---

## דרישות חומרה

### המכשיר שלנו:
- **OnePlus 11** — Snapdragon 8 Gen 2
- **RAM:** 14.8GB (5-7GB פנויים בזמן ריצה)
- **סביבה:** Termux על Android

### דרישות מינימליות:
- RAM: 2-3GB פנויים
- מקום: ~2GB לבינארי וקבצים
- חיבור לאינטרנט (ל-Claude API)

---

## תהליך ההקמה

### 1️⃣ Rust Toolchain

```bash
pkg install rustup clang mold
rustup default stable
rustup target add aarch64-linux-android
```

### 2️⃣ בנייה מקוד מקור

```bash
git clone https://github.com/zeroclaw-labs/zeroclaw ~/zeroclaw
cd ~/zeroclaw

# קובץ config לאופטימיזציות
cat > .cargo/config.toml << 'EOF'
[target.aarch64-linux-android]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=mold"]

[profile.release]
codegen-units = 1
opt-level = "z"
lto = "thin"

[build]
incremental = false
EOF

# בנייה (~20 דקות)
cargo clean
cargo build --release --locked
cargo install --path . --locked
```

### 3️⃣ Quickstart

```bash
zeroclaw quickstart --model-provider ollama --model qwen2.5-8k
```

---

## מיגרציה מ-Ollama ל-Claude API

### 🔴 בעיות עם Ollama (מודל מקומי):
- ❌ Tool-calling לא עקבי (לפעמים 0, לפעמים 1)
- ❌ מודל קטן (3B) — flakiness
- ❌ שירות לא יציב
- ⚠️ איטי (2-10 t/s)

### ✅ פתרון: Claude API

```toml
[agents.agggeeeenttt]
model_provider = "anthropic.default"

[providers.models.anthropic.default]
model = "claude-opus-5"
api_key = "sk-ant-api03-..."
timeout_secs = 300
```

---

## תצורה סופית

### קובץ: `~/.zeroclaw/config.toml`

```toml
schema_version = 3

[agents.agggeeeenttt]
risk_profile = "balanced"
runtime_profile = "unbounded"
model_provider = "anthropic.default"
max_tool_iterations = 15
step_timeout_secs = 300

[memory]
backend = "sqlite.sqlite"

[risk_profiles.balanced]
require_approval_for_medium_risk = false
sandbox_enabled = true
workspace_only = true
allowed_commands = ["*"]

[risk_profiles.balanced.delegation_policy]
mode = "allow"

[onboard_state]
quickstart_completed = true

[providers.models.anthropic.default]
model = "claude-opus-5"
api_key = "sk-ant-api03-..."
timeout_secs = 300
```

---

## אינטגרציית GitHub

### Setup:

```bash
gh auth login
# בחר: HTTPS, web browser, device code
```

### גישה מ-ZeroClaw:

```bash
gh repo list          # רשימת ריפוזיטוריים
gh pr list           # pull requests
gh issue list        # issues
git clone <url>      # clone ריפו
```

---

## שימוש ב-ZeroClaw

### הרצה בסיסית:

```bash
~/.cargo/bin/zeroclaw agent -a agggeeeenttt -m "הוראה בעברית"
```

### דוגמות:

```bash
# הרץ shell command
echo "Y" | ~/.cargo/bin/zeroclaw agent -a agggeeeenttt \
  -m "הרץ את הפקודה: ls -la"

# בדוק GitHub
echo "Y" | ~/.cargo/bin/zeroclaw agent -a agggeeeenttt \
  -m "רשום את הריפוזיטוריים שלי"
```

---

## סטטוס נוכחי

✅ **מה עובד:**
- Claude API מחובר (Opus 5)
- Tool-calling 100% עקבי
- GitHub integration דרך `gh`
- תמיכה בעברית
- Shell commands מורצים בהצלחה

📂 **קבצים חשובים:**
- Config: `~/.zeroclaw/config.toml`
- Workspace: `~/.zeroclaw/data`
- Binary: `~/.cargo/bin/zeroclaw`

---

**עודכן:** 2 באוגוסט 2026
