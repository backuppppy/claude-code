"""Shared helpers: HTTP, subprocess, DuckDuckGo dorks, console + report."""
from __future__ import annotations
import os, sys, json, shutil, subprocess, time, datetime
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

# Make locally-installed CLI tools reachable (pipx / go).
for p in (Path.home() / ".local/bin", Path.home() / "go/bin"):
    if p.is_dir() and str(p) not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{p}:{os.environ.get('PATH','')}"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 osint-recon/1.0"

# ------- console -------
try:
    from rich.console import Console
    from rich.panel import Panel
    _c = Console()
    def info(m):  _c.print(f"[cyan]•[/cyan] {m}")
    def good(m):  _c.print(f"[green]✓[/green] {m}")
    def warn(m):  _c.print(f"[yellow]![/yellow] {m}")
    def err(m):   _c.print(f"[red]✗[/red] {m}")
    def head(m):  _c.print(Panel(m, style="bold magenta"))
except Exception:  # rich missing -> plain
    def info(m):  print("[*]", m)
    def good(m):  print("[+]", m)
    def warn(m):  print("[!]", m)
    def err(m):   print("[x]", m)
    def head(m):  print("\n=== " + m + " ===")


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def run_cmd(cmd, timeout=300):
    """Run a command, return (ok, stdout+stderr). Never raises."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, env=os.environ)
        return p.returncode == 0, (p.stdout or "") + (p.stderr or "")
    except FileNotFoundError:
        return False, f"not-installed: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s: {' '.join(cmd)}"
    except Exception as e:
        return False, f"error: {e}"


def http_json(url, timeout=25, params=None, headers=None):
    if requests is None:
        return None
    try:
        h = {"User-Agent": UA}
        if headers:
            h.update(headers)
        r = requests.get(url, timeout=timeout, params=params, headers=h)
        if r.status_code == 200 and r.text.strip():
            return r.json()
    except Exception:
        return None
    return None


def http_text(url, timeout=25, headers=None, params=None):
    if requests is None:
        return None
    try:
        h = {"User-Agent": UA}
        if headers:
            h.update(headers)
        r = requests.get(url, timeout=timeout, headers=h, params=params)
        if r.status_code == 200:
            return r.text
    except Exception:
        return None
    return None


# ------- DuckDuckGo dork search -------
def ddg(query, max_results=15, backend=None):
    """Return list of {title, href, body}. Tries HTML + Lite backends."""
    try:
        from ddgs import DDGS
    except Exception:
        return []
    out = []
    try:
        with DDGS() as d:
            for r in d.text(query, max_results=max_results):
                out.append({
                    "title": r.get("title", ""),
                    "href": r.get("href") or r.get("url", ""),
                    "body": r.get("body", ""),
                })
    except Exception:
        pass
    time.sleep(0.6)  # be gentle / avoid rate-limit
    return out


def now_stamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


class Report:
    """Collects findings and renders Markdown + JSON."""
    def __init__(self, target, ttype, outdir: Path):
        self.target = target
        self.ttype = ttype
        self.outdir = outdir
        self.sections = []   # list of (title, list[str])
        self.data = {"target": target, "type": ttype,
                     "generated": datetime.datetime.now().isoformat(),
                     "findings": {}}

    def add(self, title, lines, raw=None):
        lines = [l for l in (lines or []) if l]
        self.sections.append((title, lines))
        if raw is not None:
            self.data["findings"][title] = raw
        elif lines:
            self.data["findings"][title] = lines
        # live echo
        if lines:
            good(f"{title}: {len(lines)} item(s)")
        else:
            warn(f"{title}: nothing found")

    def save(self):
        self.outdir.mkdir(parents=True, exist_ok=True)
        md = self.outdir / "report.md"
        js = self.outdir / "report.json"
        with md.open("w", encoding="utf-8") as f:
            f.write(f"# OSINT Report — `{self.target}`\n\n")
            f.write(f"- **Type:** {self.ttype}\n")
            f.write(f"- **Generated:** {self.data['generated']}\n\n")
            total = sum(len(l) for _, l in self.sections)
            f.write(f"- **Total findings:** {total}\n\n---\n\n")
            for title, lines in self.sections:
                f.write(f"## {title}\n\n")
                if not lines:
                    f.write("_nothing found_\n\n")
                    continue
                for l in lines:
                    f.write(f"- {l}\n")
                f.write("\n")
        js.write_text(json.dumps(self.data, indent=2, ensure_ascii=False),
                      encoding="utf-8")
        return md, js
