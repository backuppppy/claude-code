# Storytel Scripts — Audiobook Scraping

Scripts for downloading and managing audiobooks from **Storytel Premium**.

## 📂 Files

### `storytel.py`
Main Storytel API client. Handles authentication and basic book operations.

**Features:**
- Login to Storytel account
- Retrieve bookshelf
- Fetch book metadata
- Manage sessions

**Usage:**
```bash
python storytel.py
# Provides class-based API for Storytel operations
```

### `storytel_direct_download.py`
**Direct audiobook downloader** — Downloads MP3 streams directly from Storytel's API.

**Features:**
- Authenticates with Storytel account
- Retrieves audio stream URLs
- Downloads MP3s with embedded metadata
- Automatically embeds cover art & tags

**Requirements:**
- Python 3.8+
- `requests`, `beautifulsoup4`, `eyed3` (audio tagging)

**Usage:**
```bash
python storytel_direct_download.py "<url>" [output_name]

# Example:
python storytel_direct_download.py "https://www.storytel.com/books/123456" "My Audiobook"
```

**Output:**
```
My Audiobook.mp3  (MP3 with embedded metadata and cover art)
```

### `storytel_search.py`
Search Storytel's catalog for books.

**Features:**
- Search by title, author, genre
- Filter by language
- Fetch search results

**Usage:**
```bash
python storytel_search.py "Harry Potter"
python storytel_search.py --author "JK Rowling"
python storytel_search.py --genre "fantasy" --language "he"
```

## 🔐 Authentication

You'll need valid Storytel Premium credentials:

```bash
STORYTEL_USERNAME="your_email@example.com"
STORYTEL_PASSWORD="your_password"
```

Store in environment or `.env` file:
```bash
# .env
STORYTEL_USERNAME=your_email@example.com
STORYTEL_PASSWORD=your_password
```

Load before running:
```bash
export STORYTEL_USERNAME="your_email@example.com"
export STORYTEL_PASSWORD="your_password"
python storytel_direct_download.py "<url>"
```

## 📦 Installation

```bash
# Install dependencies
pip install requests beautifulsoup4 eyed3

# Or from requirements
pip install -r ../../projects/stips-monitor/requirements.txt
```

## ⚠️ Disclaimer

These scripts are for **personal use only** with content you own/have access to. Respect Storytel's ToS and copyright laws.

## 🔗 Related

- Main repo: [`../.`](..)
- Spec-kit scripts: [`../spec-kit`](../spec-kit)
- STIPS Monitor: [`../../projects/stips-monitor`](../../projects/stips-monitor)
- Full documentation: [`../../memory/project_audiobook_dl_storytel.md`](../../memory/project_audiobook_dl_storytel.md)
