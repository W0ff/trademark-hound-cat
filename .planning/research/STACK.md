# Stack Research

**Domain:** Claude Code skills for trademark monitoring (web search automation + agentic browsing + file-based state)
**Researched:** 2026-04-03
**Confidence:** HIGH (Claude Code skill format verified from official docs; Python/Serper patterns verified from multiple sources)

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Claude Code Skills | current (`.claude/skills/`) | Slash command delivery format | Official format as of 2025; supersedes `.claude/commands/`; supports frontmatter, supporting files, subagent forking, argument substitution |
| Python | 3.13 (system) | Serper.dev API script execution | Already installed; skills invoke via `Bash(python3 *)`; no subprocess wrapper needed — Claude's Bash tool runs scripts directly |
| `requests` | 2.x (stdlib-adjacent) | HTTP POST to Serper.dev | Best choice for synchronous one-shot API calls in CLI scripts; no async needed; simpler than httpx for scripts that run once per invocation |
| `json` + `pathlib` | stdlib | Read/write JSON state files | Zero-dependency; `pathlib.Path` handles cross-OS paths; `json.dumps(indent=2)` produces human-readable output attorneys can inspect |
| Markdown (plain files) | — | Report output format | No dependencies; renders in GitHub, VS Code, Claude Code itself; attorneys review offline |

### Skill File Architecture

| Location | Path Pattern | Scope | Notes |
|----------|-------------|-------|-------|
| Project skill | `.claude/skills/trademark-cat/SKILL.md` | This project only | Invoke with `/trademark-cat` |
| Project skill | `.claude/skills/trademark-hound/SKILL.md` | This project only | Invoke with `/trademark-hound` |
| Supporting scripts | `.claude/skills/trademark-hound/scripts/search.py` | Bundled with skill | Referenced in SKILL.md; Claude executes via Bash tool |
| Supporting templates | `.claude/skills/trademark-hound/templates/report.md` | Bundled with skill | Claude fills in template |

### Supporting Libraries (Python only, no npm)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `requests` | `>=2.28` | Serper.dev API calls | Only in `search.py`; installed via `pip install requests` |
| `json` | stdlib | Safelist + state serialization | Everywhere; no install needed |
| `pathlib` | stdlib | File path resolution | Everywhere; prefer over `os.path` |
| `sys` | stdlib | Exit codes, CLI args to script | `sys.argv[1]` for trademark name passed from skill |
| `datetime` | stdlib | Timestamped report filenames | `datetime.date.today().isoformat()` → `report-2026-04-03.md` |
| `argparse` | stdlib | Named args in `search.py` | Use when script needs `--trademark`, `--api-key`, `--num` flags |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Claude Code | Skill authoring, testing, invocation | Run `/trademark-cat` and `/trademark-hound` directly in session |
| `python -m json.tool` | Validate safelist/state JSON files | Quick sanity check: `python -m json.tool safelist-MARK.json` |

---

## Skill File Format (Authoritative — from official docs)

**Canonical SKILL.md structure:**

```yaml
---
name: trademark-hound
description: Search web for trademark infringement variants. Runs Serper.dev search, browses top results, scores threats, writes dated Markdown report. Use when: monitoring a trademark, checking for infringement, updating safe list.
disable-model-invocation: true
allowed-tools: Bash(python3 *) WebSearch WebFetch Read Write
effort: high
---

# Trademark Hound

Investigate trademark `$ARGUMENTS` for web-based infringement.

...instructions...
```

**Key frontmatter fields for this project:**

| Field | Value | Why |
|-------|-------|-----|
| `disable-model-invocation: true` | Required for both skills | Prevents Claude from auto-triggering a search during normal conversation; must be attorney-initiated |
| `allowed-tools` | `Bash(python3 *) WebSearch WebFetch Read Write` | Pre-approves all tools the skill needs; avoids per-action permission prompts during a run |
| `effort: high` | Recommended for Hound | Multi-step investigation; higher effort = more thorough browsing and scoring |
| `argument-hint` | `<TRADEMARK> [company context]` | Shows in autocomplete: `/trademark-hound DELTA "aviation company"` |
| `$ARGUMENTS` | Used inline in skill body | Receives everything after `/trademark-hound` — trademark name + optional context |

**Argument pattern:**
```
/trademark-hound APEX "software company, project management tools"
```
Inside SKILL.md: `The trademark to investigate is: $ARGUMENTS`

---

## Python Script Patterns

### Serper.dev API Call (`search.py`)

**Endpoint:** `https://google.serper.dev/search` (POST)
**Auth:** `X-API-KEY` header (not Bearer token)
**Response fields used:** `organic[].title`, `organic[].link`, `organic[].snippet`, `organic[].position`

```python
#!/usr/bin/env python3
"""
search.py — Serper.dev search for trademark variants
Usage: python3 search.py --trademark "APEX" --api-key "xxx" --num 20
Outputs: JSON array to stdout, one result per organic hit
"""
import argparse
import json
import sys
import requests

def search(query: str, api_key: str, num: int = 10) -> list[dict]:
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {"q": query, "num": num}
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    data = response.json()
    return data.get("organic", [])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trademark", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--num", type=int, default=10)
    args = parser.parse_args()

    results = search(args.trademark, args.api_key, args.num)
    json.dump(results, sys.stdout, indent=2)

if __name__ == "__main__":
    main()
```

Claude invokes this from the skill body via:
```
!`python3 ${CLAUDE_SKILL_DIR}/scripts/search.py --trademark "$TRADEMARK" --api-key "$SERPER_API_KEY" --num 20`
```

Or, since Claude has the Bash tool, Claude constructs and runs the call itself — the skill instructs it to do so.

### Safelist State File (`safelist-[TRADEMARK].json`)

```python
# Pattern: atomic load-or-create with pathlib
from pathlib import Path
import json

def load_safelist(trademark: str, workdir: Path) -> dict:
    path = workdir / f"safelist-{trademark.upper()}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"trademark": trademark, "safe_entries": [], "last_updated": None}

def save_safelist(data: dict, trademark: str, workdir: Path) -> None:
    path = workdir / f"safelist-{trademark.upper()}.json"
    # Write to temp, then atomic rename
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)
```

---

## File Naming Conventions

All runtime files land in the **workspace directory** where the skill is invoked (i.e., the project root where the attorney runs Claude Code).

| File | Pattern | Example |
|------|---------|---------|
| Variants list (Cat output) | `variants-[TRADEMARK].txt` | `variants-APEX.txt` |
| Safe list (persistent) | `safelist-[TRADEMARK].json` | `safelist-APEX.json` |
| Threat report | `report-[TRADEMARK]-[YYYY-MM-DD].md` | `report-APEX-2026-04-03.md` |
| Raw Serper results (optional debug) | `search-[TRADEMARK]-[YYYY-MM-DD].json` | `search-APEX-2026-04-03.json` |

**Why this convention:**
- Trademark name in CAPS matches legal convention
- Date suffix allows multiple runs without overwriting
- All files are grep-able and human-readable without tooling
- No subdirectory nesting needed at MVP scale

---

## Agentic Browsing Pattern

The Hound skill uses Claude's native **WebSearch** and **WebFetch** tools for investigation — no third-party browsing library needed.

**Pattern in SKILL.md:**
```markdown
For each variant URL from the Serper results:
1. Use WebFetch to load the page
2. Assess: Is this a commercial use of the mark? What goods/services?
3. Score against the 8-factor threat matrix
4. Record: URL, company name, goods/services, score breakdown
```

**Why native tools over Playwright/Selenium:**
- Zero install friction — no `npm install` or browser binary
- Works inside Claude Code's permission model without extra config
- WebFetch converts HTML to markdown automatically — no parsing code needed
- Sufficient for commercial page assessment (not JS-heavy SPAs)

**Caveat:** WebFetch cannot execute JavaScript or handle login-walled pages. If a URL 302-redirects to a login page, Claude should note "access restricted" and move to next result. This is a known limitation, not a bug.

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Skill location | `.claude/skills/` | `.claude/commands/` | Commands format is legacy as of 2025; skills add supporting files, subagent forking, frontmatter |
| HTTP client | `requests` | `httpx` | httpx async advantage irrelevant for single-shot scripts; requests is simpler and universally understood |
| HTTP client | `requests` | `urllib` (stdlib) | urllib requires manual JSON encoding, header management; requests is cleaner for 5 lines of API code |
| Web browsing | Native WebFetch/WebSearch | Playwright | Playwright requires browser install, node_modules, async Python — massive overhead for URL content extraction |
| Web browsing | Native WebFetch/WebSearch | Firecrawl | External paid service; adds dependency and cost; WebFetch sufficient for commercial page reading |
| State format | JSON files | SQLite | SQLite requires sqlite3 schema, migrations, tooling; JSON is human-readable and portable |
| State format | JSON files | YAML | YAML requires PyYAML (non-stdlib); JSON parses with zero dependencies |
| Report format | Markdown | HTML | HTML requires rendering; Markdown is reviewable in any editor, Claude Code, GitHub |
| Report format | Markdown | PDF | PDF requires WeasyPrint or pandoc; unacceptable install overhead for a CLI tool |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `.claude/commands/` directory | Legacy format; no supporting files support; skills supersede it | `.claude/skills/[name]/SKILL.md` |
| `os.path` for file operations | Verbose; error-prone on Windows paths | `pathlib.Path` |
| `print()` to write files from Python scripts | Race conditions; no atomicity | `path.write_text()` with atomic rename |
| Global `~/.claude/skills/` for project skills | Makes skills available in all projects; trademark skills should be project-scoped | `.claude/skills/` in project root |
| `$ARGUMENTS` in `user-invocable: false` skills | Skills hidden from user should not require manual argument passing | n/a |
| Hardcoded API key in `search.py` | Security risk; keys in version history | `--api-key` CLI arg; Claude reads from `$SERPER_API_KEY` env var or prompts attorney |
| `subprocess.run` inside SKILL.md via bash injection | Fragile quoting; not needed | `allowed-tools: Bash(python3 *)` + direct Bash tool invocation by Claude |

---

## Stack Patterns by Variant

**If the attorney provides the Serper API key at skill invocation time:**
- Skill prompts: "Please provide your Serper API key" or reads `$SERPER_API_KEY`
- Pass as `--api-key` argument to `search.py`
- Never write key to any state file

**If running multiple trademarks in sequence:**
- Run `/trademark-cat MARK1` then `/trademark-hound MARK1` per trademark
- State files are named per-trademark; no cross-contamination
- No orchestration layer needed at MVP

**If a variants file already exists:**
- Hound skill checks for `variants-[TRADEMARK].txt` at startup using Read tool
- If found: proceeds directly to search
- If missing: instructs attorney to run `/trademark-cat` first (or routes to Cat inline)

---

## Version Compatibility

| Component | Version | Compatibility Notes |
|-----------|---------|---------------------|
| Python | 3.13.x (system) | `requests` 2.x fully compatible; no breaking changes expected |
| `requests` | `>=2.28` | `response.raise_for_status()` and `response.json()` stable since 2.x |
| Claude Code skills | current | Frontmatter format stable; `CLAUDE_SKILL_DIR` variable available in current release |
| Serper.dev API | v1 (implicit) | No versioned endpoint in URL; POST to `https://google.serper.dev/search` stable |

---

## Installation

```bash
# Python dependency (one-time, per machine)
pip3 install requests

# No npm, no node_modules, no other installs required
# All other dependencies are Python stdlib
```

---

## Sources

- [Extend Claude with Skills — Claude Code Docs](https://code.claude.com/docs/en/slash-commands) — Frontmatter reference, skill directory structure, argument substitution, `CLAUDE_SKILL_DIR` variable (HIGH confidence — official docs, verified 2026-04-03)
- [Serper.dev API — Python POST example](https://www.restack.io/p/serper-api-key-answer-python-search-engine-cat-ai) — Endpoint URL `https://google.serper.dev/search`, `X-API-KEY` header, `requests.post` pattern (MEDIUM confidence — secondary source; pattern consistent across multiple community references)
- [HTTPX vs Requests comparison 2025](https://www.morethanmonkeys.co.uk/article/comparing-requests-and-httpx-in-python-which-http-client-should-you-use-in-2025/) — Rationale for choosing `requests` over `httpx` for synchronous CLI scripts (MEDIUM confidence — multiple sources agree)
- [Python pathlib + JSON best practices](https://cr88.hashnode.dev/using-pythons-pathlib-to-work-with-json-files-why-and-how) — Atomic write pattern, `Path.read_text`/`write_text` idioms (HIGH confidence — stdlib docs + community consensus)
- [Web Search Agent Skills in Claude Code](https://websearchapi.ai/blog/claude-code-web-search-agent-skills) — WebFetch/WebSearch as native tools for agentic browsing inside skills (MEDIUM confidence — corroborated by official Claude Code docs)

---

*Stack research for: Trademark Hound + Cat — Claude Code skills for trademark monitoring*
*Researched: 2026-04-03*
