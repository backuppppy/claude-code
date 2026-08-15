# Claude Code — Project Specification

**Version:** 1.0.0  
**Last Updated:** 2026-08-15  
**Status:** Active  
**Owner:** backuppppy

---

## 📋 Project Overview

Claude Code is a comprehensive backup and management system for all development work, projects, scripts, and configurations. It serves as a complete environment snapshot that can be restored at any time.

### Key Objectives
1. ✅ Maintain complete backup of all work
2. ✅ Document project structure and dependencies
3. ✅ Enable easy restoration of environment
4. ✅ Track all changes and versions
5. ✅ Organize projects by domain

---

## 🏗️ Architecture

### Directory Structure
```
claude-code/
├── .specify/                    ← Spec-kit configuration
├── projects/                    ← Active projects (10+ repos)
├── scripts/                     ← Utilities (spec-kit, storytel, etc)
├── zeroclaw-termux-setup/      ← ZeroClaw + Claude API setup
├── memory/                      ← Project memory & history
├── docs/                        ← Documentation
└── config-templates/            ← Configuration templates
```

### Core Components

#### 1. Projects
- **tg-backup-apk** — Telegram backup application (Kivy + Flask)
- **stips-monitor** — Telegram monitoring bot (SQLite + asyncio)
- **wa-counter** — WhatsApp groups counter
- **osint-recon** — OSINT reconnaissance tool
- **fxp_bot** — FXP monitoring bot
- **web** — Web scraping projects
- **font_maker** — Font creation utility

#### 2. Scripts & Utilities
- **spec-kit/** — GitHub specification toolkit (bash + python)
- **audiobook-dl/** — Storytel audiobook scraping
- **zeroclaw-termux-setup/** — ZeroClaw agent setup
- **book/** — EPUB/PDF book generation

#### 3. Infrastructure
- **ZeroClaw v0.8.3** — Agentic AI with Claude API
- **Claude Opus 5** — Language model provider
- **GitHub integration** — Repos, PRs, issues management
- **Telegram API** — Bot communications

---

## 🎯 Development Phases

### Phase 1: Setup & Infrastructure ✅ In Progress
- Initialize spec-kit configuration
- Setup GitHub workflows
- Configure memory system
- Document project structure

**Timeline:** 2026-08-15 → 2026-08-20

### Phase 2: ZeroClaw Integration ✅ Completed
- Install ZeroClaw binary
- Configure Claude API
- Setup YOLO mode
- Create helper scripts

**Completed:** 2026-08-02

### Phase 3: Spec-Kit & Tools 🔄 In Progress
- Import spec-kit scripts
- Setup feature scaffolding
- Configure prerequisites
- Create task management

**Timeline:** 2026-08-15 → 2026-08-25

### Phase 4: Project Management ⏳ Pending
- Setup STIPS Monitor
- Configure Storytel scripts
- Organize structure
- Create dashboards

**Timeline:** 2026-08-25 → 2026-09-15

---

## 🔒 Security & Access

### Secrets Management
Sensitive data (API keys, tokens) stored in GitHub Secrets:
- `ANTHROPIC_API_KEY` — Claude API token
- `GITHUB_TOKEN` — GitHub PAT
- `TELEGRAM_BOT_TOKEN` — Bot credentials
- `STORYTEL_USERNAME/PASSWORD` — Storytel access

### Environment Variables
Loaded from `.env` files (not committed):
```bash
CLAUDE_API_KEY=sk-ant-api03-...
ZEROCLAW_AGENT=agggeeeenttt
TELEGRAM_BOT_TOKEN=...
```

### Access Control
- **Public:** Project README, documentation, non-sensitive code
- **Private:** Credentials, secrets, personal configs
- **GitHub Secrets:** Only accessible in CI/CD workflows

---

## 📦 Dependencies

### Core Requirements
```
python >= 3.11
git >= 2.40
bash >= 5.0
rust >= 1.70 (for zeroclaw build)
```

### Python Packages
```
requests, beautifulsoup4, eyed3    # Storytel
python-telegram-bot                # Telegram bots
telethon, kivy, flask              # TG Backup APK
```

### External Tools
- **GitHub CLI** (`gh`) — Repo management
- **Spec-kit** — Feature scaffolding
- **ZeroClaw** — Agentic AI
- **audiobook-dl** — Audiobook downloader

---

## 🚀 Getting Started

### Quick Setup
```bash
# Clone repo
git clone https://github.com/backuppppy/claude-code
cd claude-code

# Install dependencies
pip install -r projects/stips-monitor/requirements.txt
bash scripts/spec-kit/bash/check-prerequisites.sh

# Setup ZeroClaw (on Termux)
bash zeroclaw-termux-setup/install.sh
```

### First Steps
1. Read `README.md` for overview
2. Check `memory/` for project history
3. Review `scripts/spec-kit/README.md` for development workflow
4. Run `bash scripts/spec-kit/bash/check-prerequisites.sh`

---

## 📊 Metrics & Status

### Projects Count: 10+
| Project | Status | Type | Language |
|---------|--------|------|----------|
| tg-backup-apk | Active | Kivy App | Python |
| stips-monitor | Active | Telegram Bot | Python |
| osint-recon | Active | CLI Tool | Python |
| zeroclaw-setup | Active | Setup | Shell |
| spec-kit | Active | Utilities | Bash/Python |

### Code Statistics
- **Files:** 125+
- **Python Scripts:** 45+
- **Bash Scripts:** 20+
- **Documentation:** 30+ markdown files
- **Memory Records:** 15+ project memories

### Infrastructure
- **Git Commits:** 100+
- **Branches:** main (primary)
- **Remote:** GitHub (backuppppy/claude-code)
- **CI/CD:** GitHub Actions workflows

---

## 📝 Documentation

### Main Documentation
- [`README.md`](../README.md) — Project overview
- [`ZEROCLAW_ANDROID_SETUP.md`](../ZEROCLAW_ANDROID_SETUP.md) — ZeroClaw guide
- [`scripts/spec-kit/README.md`](../scripts/spec-kit/README.md) — Spec-kit usage

### Project Memory
Each project has detailed memory:
- `memory/project_*.md` — History, issues, solutions
- `memory/zeroclaw_*.md` — ZeroClaw configuration
- `memory/technical_*.md` — Technical details

### Specification Files
- `.specify/feature.json` — Project metadata
- `.specify/plans/main-plan.json` — Development plan
- `.specify/tasks/*.json` — Task tracking

---

## 🔄 Workflow

### Development Cycle
1. **Plan** → Define feature in spec-kit
2. **Create** → Use `create-new-feature.sh`
3. **Develop** → Write code
4. **Test** → Run prerequisites check
5. **Document** → Update memory & README
6. **Commit** → Push to GitHub
7. **Review** → Check CI/CD status

### Spec-Kit Commands
```bash
# Check environment
bash scripts/spec-kit/bash/check-prerequisites.sh

# Create feature
bash scripts/spec-kit/bash/create-new-feature.sh "feature-name"

# Setup plan
python scripts/spec-kit/python/setup_plan.py

# Manage tasks
python scripts/spec-kit/python/setup_tasks.py
```

---

## 🎓 Learning Resources

### For New Contributors
1. Read project memory in `memory/`
2. Check related project README
3. Review spec-kit setup in `.specify/`
4. Follow existing patterns in similar projects

### For Maintenance
1. Update `memory/` when changes occur
2. Keep README.md in sync
3. Run spec-kit prerequisites check
4. Update version in `.specify/feature.json`

---

## 📞 Support & Contact

**Owner:** backuppppy (9917099@gmail.com)  
**Repository:** https://github.com/backuppppy/claude-code  
**Issues:** GitHub Issues  
**Discussions:** GitHub Discussions

---

**Last Updated:** 2026-08-15  
**Next Review:** 2026-09-15  
**Status:** Active & Maintained ✅
