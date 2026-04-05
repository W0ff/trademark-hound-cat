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
  variant, title, url, snippet, position
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
def search_variant(variant, api_key):
    """Run an exact-match Serper.dev search for a single variant name."""
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {"q": f'"{variant}"', "num": 10}
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json().get("organic", [])


# ── Main ────────────────────────────────────────────────────────────────────────
def main():
    variants = load_variants(VARIANTS_FILE)
    if not variants:
        print(f"ERROR: No variants found in {VARIANTS_FILE}", file=sys.stderr)
        sys.exit(1)

    total = len(variants)
    all_results = []

    for i, variant in enumerate(variants, 1):
        print(f"[{i}/{total}] Searching: {variant}", flush=True)
        try:
            results = search_variant(variant, API_KEY)
            for r in results:
                all_results.append({
                    "variant": variant,
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
    base = os.path.splitext(os.path.basename(VARIANTS_FILE))[0]
    trademark = base.replace("variants-", "")
    output_file = os.path.join(variants_dir, f"hound_leads-{trademark}.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {len(all_results)} results written to {output_file}", flush=True)


if __name__ == "__main__":
    main()
