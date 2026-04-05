#!/usr/bin/env python3
"""
hound_leads_template.py — Serper.dev search template for Trademark Hound

Placeholders substituted by /trademark-hound at run time:
  [INSERT API KEY]       → Serper.dev API key (from dashboard)
  [INSERT VARIANTS FILE] → path to variants-[TRADEMARK].txt

Usage (after substitution):
  python3 hound-SERP-[TRADEMARK].py

Output:
  hound_leads-[TRADEMARK].json — one record per SERP result with fields:
  variant, search_type ("literal" | "variant"), title, url, snippet, position
  First 50 records are literal mark results; remaining are per-variant (10 each).
"""
import json
import os
import time
import sys
import requests

# ── Configuration ──────────────────────────────────────────────────────────────
API_KEY = "[INSERT API KEY]"
VARIANTS_FILE = "[INSERT VARIANTS FILE]"
DELAY_SECONDS = 0.5  # configurable: seconds between Serper.dev requests


# ── Variant loading ─────────────────────────────────────────────────────────────
def load_variants(path):
    """Read variants file; skip # comment/header lines; strip inline annotations."""
    variants = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue
            # Strip inline annotation comment (e.g. "Ackme  # phonetic: vowel shift")
            variant_name = stripped.split("#")[0].strip()
            if variant_name:
                variants.append(variant_name)
    return variants


# ── Serper.dev search ───────────────────────────────────────────────────────────
def search_serper(query, api_key, num):
    """Run an exact-match Serper.dev search and return organic results."""
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {"q": f'"{query}"', "num": num}
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json().get("organic", [])


def search_variant(variant, api_key):
    """Run an exact-match Serper.dev search for a single variant name (10 results)."""
    return search_serper(variant, api_key, num=10)


# ── Main ────────────────────────────────────────────────────────────────────────
def main():
    variants = load_variants(VARIANTS_FILE)
    if not variants:
        print(f"ERROR: No variants found in {VARIANTS_FILE}", file=sys.stderr)
        sys.exit(1)

    # Derive the literal mark name from the variants file path
    variants_base = os.path.splitext(os.path.basename(VARIANTS_FILE))[0]
    literal_mark = variants_base.replace("variants-", "")

    total = len(variants)
    all_results = []

    # ── Literal mark search (top 50) ────────────────────────────────────────────
    print(f"[0/{total}] Searching literal mark: {literal_mark} (top 50)", flush=True)
    try:
        literal_results = search_serper(literal_mark, API_KEY, num=50)
        for r in literal_results:
            all_results.append({
                "variant": literal_mark,
                "search_type": "literal",
                "title": r.get("title", ""),
                "url": r.get("link", ""),
                "snippet": r.get("snippet", ""),
                "position": r.get("position", 0),
            })
        print(f"  → {len(literal_results)} results", flush=True)
    except requests.HTTPError as e:
        print(f"  ERROR [literal mark]: {e}", file=sys.stderr, flush=True)
    except requests.RequestException as e:
        print(f"  ERROR [literal mark]: {e}", file=sys.stderr, flush=True)

    if total:
        time.sleep(DELAY_SECONDS)

    for i, variant in enumerate(variants, 1):
        print(f"[{i}/{total}] Searching: {variant}", flush=True)
        try:
            results = search_variant(variant, API_KEY)
            for r in results:
                all_results.append({
                    "variant": variant,
                    "search_type": "variant",
                    "title": r.get("title", ""),
                    "url": r.get("link", ""),      # Serper returns "link"; stored as "url"
                    "snippet": r.get("snippet", ""),
                    "position": r.get("position", 0),
                })
        except requests.HTTPError as e:
            print(f"  ERROR [{variant}]: {e}", file=sys.stderr, flush=True)
        except requests.RequestException as e:
            print(f"  ERROR [{variant}]: {e}", file=sys.stderr, flush=True)

        if i < total:
            time.sleep(DELAY_SECONDS)

    # Derive output filename from variants file path, preserving directory
    variants_dir = os.path.dirname(os.path.abspath(VARIANTS_FILE))
    output_file = os.path.join(variants_dir, f"hound_leads-{literal_mark}.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {len(all_results)} results written to {output_file}", flush=True)


if __name__ == "__main__":
    main()
