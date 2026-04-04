---
description: "Investigate trademark infringement leads. Runs SERP search across variants, filters against safelist, investigates each lead via WebFetch, and scores using the 8-factor weighted threat matrix. Use after /trademark-cat has generated a variants file."
allowed_tools: ["WebFetch", "Bash", "Read", "Write"]
---

## Intake

Parse `$ARGUMENTS` to extract:
1. The trademark name (first token or first quoted string)
2. The second argument (optional — remaining token after the trademark name)

Sanitize the trademark name for filenames: replace spaces with hyphens, convert to lowercase, remove any characters that are not letters, numbers, or hyphens. Store as `sanitized_name`.

**Second-argument detection (re-invocation branch):**

After extracting the trademark name (first token), check whether a second argument is present and matches the pattern `HOUND_REPORT_*.md` (the filename starts with `HOUND_REPORT_` and ends with `.md`), OR the second token is a path to an existing file with that naming pattern.

If a second argument matching this pattern is detected:
  - Store the report path as `reviewed_report_path`
  - Set `mode = 'safelist_ingestion'`
  - Do NOT ask for goods/services description
  - Skip directly to the **Safelist Ingestion** section below
  - Do NOT run SERP search, content triage, or scoring

If no second argument (or second argument does not match `HOUND_REPORT_*.md` pattern):
  - Set `mode = 'investigate'`
  - Continue with normal intake below
  - Ask for goods/services if not provided:

    > "What goods or services does [TRADEMARK] cover? For example: 'software for project management' or 'retail clothing stores'."

  - Do not proceed until you have BOTH the trademark name AND a goods/services description.

---

## Step 1: Check Prerequisites (variants file)

Use the Read tool to check whether `variants-[sanitized_name].txt` exists in the current directory.

If the file does NOT exist, output exactly:
> "No variants file found for [TRADEMARK]. Please run `/trademark-cat [TRADEMARK]` first to generate the variants list."
Then stop. Do not proceed.

If it exists, read it and extract:
- The `# Context:` line (first line starting with "# Context:"): store the goods/services description as `protected_mark_context` (everything after "# Context: "). If no Context line is found, use the goods/services description provided at intake.
- The variant names: for each non-empty line, skip lines starting with "#", then strip inline annotation (everything from " #" onward). Collect the clean variant names.

Report: "Variants loaded: [N] variants for [TRADEMARK] | Context: [protected_mark_context]"

---

## Step 2: Load Safelist

Check whether `safelist-[sanitized_name].json` exists.

If it does:
  Read the file. Parse as JSON. Extract the list of safe URLs.
  Store as a set: safelist_urls = set of all URL strings in the JSON array.
  Report: "Safelist loaded: [N] entries"

If it does not exist:
  Set safelist_urls = empty set.
  Report: "No safelist found — starting fresh"

---

## Step 3: Generate or Reuse SERP Script

Check whether `hound-SERP-[sanitized_name].py` exists.

If it EXISTS:
  Report: "SERP script found: hound-SERP-[sanitized_name].py — reusing existing script."
  Proceed to Step 4.

If it does NOT exist:
  Ask the attorney:
  > "What is your Serper.dev API key? (It will be written to hound-SERP-[sanitized_name].py and should not be committed to git.)"
  Wait for the key. Do not proceed until it is provided.

  Read the file `hound_leads_template.py` from the project root using the Read tool.
  Replace the literal string `[INSERT API KEY]` with the attorney's API key.
  Replace the literal string `[INSERT VARIANTS FILE]` with `variants-[sanitized_name].txt`.
  Write the result to `hound-SERP-[sanitized_name].py` using the Write tool.

  Do NOT display the generated script content in your response.
  Report: "SERP script generated: hound-SERP-[sanitized_name].py"
  Note to attorney: "Note: hound-SERP-[sanitized_name].py contains your API key — do not commit it to git."

---

## Step 4: Run SERP Search

Execute using the Bash tool:
  python3 hound-SERP-[sanitized_name].py

This script will print progress as it runs: "[1/N] Searching: [variant]" for each variant.
With ~100 variants and 0.5s delay, expect approximately 50–60 seconds of runtime.
When complete, the script reports how many results were written to `hound_leads-[sanitized_name].json`.

If the script exits with a non-zero exit code or "ERROR" appears in output:
  Report the error message to the attorney and stop.
  Common causes: invalid API key, network timeout, variants file not found.

After successful completion, read `hound_leads-[sanitized_name].json`.
Report: "SERP search complete. [N] raw leads found across [M] variants."

---

## Step 5: Apply Safelist Filter

For each lead in the raw leads list:
  If the lead's `url` field is an exact string match for any URL in safelist_urls: discard silently.
  Otherwise: keep for investigation.

Use exact string equality only. Do not normalize URLs, strip query strings, or do subdomain matching.

Report: "[N] leads after safelist filtering ([M] leads excluded by safelist)"

---

## Step 6: Informational Content Exclusion

Before spending WebFetch calls, apply two-stage triage.

**Stage 1 — URL domain triage (no fetch needed):**
Exclude a lead without fetching if its URL's hostname (stripped of `www.`) matches or is a subdomain of any domain in the following list:

```
# Encyclopedias / dictionaries / reference
wikipedia.org, wikimedia.org, wiktionary.org, dictionary.com,
merriam-webster.com, vocabulary.com, dictzone.com

# News outlets
bbc.co.uk, reuters.com, apnews.com, nytimes.com, wsj.com,
theguardian.com, cnn.com, npr.org

# Social media & profiles
linkedin.com, facebook.com, twitter.com, x.com, instagram.com,
youtube.com, reddit.com, tiktok.com, pinterest.com,
soundcloud.com, tumblr.com

# Business directories & company databases
yelp.com, mapquest.com, yellowpages.com, manta.com, bbb.org,
rocketreach.co, zoominfo.com, dnb.com, foursquare.com,
opencorporates.com, bizapedia.com, endole.co.uk,
find-and-update.company-information.service.gov.uk,
crunchbase.com, f6s.com, waze.com, topline.com

# People / background-check sites
cyberbackgroundchecks.com, truthfinder.com, fastbackgroundcheck.com,
whitepages.com, beenverified.com, spokeo.com, peoplefinders.com

# App stores & app-rating sites
play.google.com, apps.apple.com, chromewebstore.google.com,
appbrain.com, aptoide.com, apk.dog

# Stock photo / icon / clip-art
shutterstock.com, vecteezy.com, freepik.com, alamy.com,
stock.adobe.com, icons8.com, dreamstime.com, 123rf.com,
istockphoto.com, gettyimages.com

# E-commerce product listings (non-brand storefronts)
amazon.com, amazon.co.uk, ebay.com, alibaba.com, aliexpress.com,
walmart.com, etsy.com, abebooks.com

# Job sites
indeed.com, glassdoor.com, monster.com, ziprecruiter.com

# Developer documentation
developer.android.com, developer.mozilla.org, developer.cisco.com,
developer.codesignal.com, docs.gtk.org, docs.junit.org,
learn.microsoft.com, javadoc.io, composables.com,
proandroiddev.com, community.appian.com, mathworks.com,
doc.akka.io, docs.rs, go.dev, tip.golang.org, pkg.go.dev,
baeldung.com, webdriver.io, pypi.org, docs.gradle.org,
angular.dev, harmony.apache.org, docs.testkube.io

# Q&A / forums / dev communities
stackoverflow.com, quora.com, stackexchange.com, community.unix.com,
medium.com, scribd.com, juejin.cn, bbs.kafan.cn, askfilo.com,
forum.getodk.org, groups.google.com, coderanch.com,
slack-chats.kotlinlang.org

# Academic / research
jstor.org, dl.acm.org, scirp.org, arxiv.org, sciencedirect.com,
emerald.com, studocu.com, coursehero.com, researchgate.net

# Government archives / regulatory PDFs
osha.gov, epa.gov, nepis.epa.gov, apps.fcc.gov, pta.gov.pk,
nist.gov, fldoe.org, dau.edu

# Patent / trademark search
patents.google.com, trademarkia.com, justia.com,
trademark-clearinghouse.com

# Emoji / symbols / fonts / icons
emojipedia.org, wumbo.net, fontawesome.com

# Code hosting (repo/profile pages — not company product sites)
github.com, gitlab.com, bitbucket.org

# Auction / collectibles (non-software)
db.stevealbum.com, sarc.auction

# Gaming / Roblox / Minecraft
rolimons.com, fandom.com, miraheze.org, minecraft-statistic.net

# Music / entertainment
spotify.com, open.spotify.com, volt.fm, music.apple.com,
shazam.com, jiosaavn.com, edmtrain.com, insomniac.com, deviantart.com

# Crypto / blockchain / finance
coinmarketcap.com, coinswitch.co, binance.com, phantom.com,
poocoin.app, bitget.com, finance.yahoo.com

# Dutch / German / other-language product & shopping noise
tweakers.net, coolblue.nl, bol.com, onderdeeltotaal.nl,
mercateo.com, kedahead.de, weinmann-schanz.de,
hippeschoentjes.be, simplexcars.be, autobild.de

# Miscellaneous noise
oil-club.ru, zapodarkom.com.ua, runeberg.org,
universe.roboflow.com, sourceforge.net, figma.com, discogs.com,
slideshare.net, tumgik.com, trustpilot.com, getapp.ca,
softwareworld.co, reviews.llvm.org, mindat.org, yr.no,
wanderlog.com, irrigation-mart.com, rrproducts.com,
amacrongolf.com.au, rdmparts.com
```

Apply domain-level exclusion only. Do NOT exclude based on URL path segments like /blog/ or /article/ — a brand site may have a blog and still be a commercial competitor.

Log each excluded URL: "Excluded [URL]: known informational domain"

**Stage 1.5 — Batch URL review (attorney approval gate):**

Before fetching anything, present all post-Stage-1 leads as a numbered table:

```
[N] URLs cleared domain triage. Review before fetching:

 #  | URL                                      | Variant
----|------------------------------------------|----------
 1  | https://example.com/testmark             | Testmark
 2  | https://another.io/                      | TestmarkIO
...
```

Then ask:
> "Reply **'proceed'** to fetch all, or list numbers to skip (e.g. '3, 7, 12')."

Wait for the attorney's reply before continuing. Apply any numbered exclusions — log each: `"Skipped [URL]: excluded by attorney at triage review"`. Store the remaining approved leads as the fetch queue.

**Stage 2 — Content signal triage (parallel batch fetch):**

Split the approved fetch queue into batches of 10. Launch each batch as a parallel Agent sub-call, instructing each agent to:
- Fetch all 10 URLs
- Return a one-line signal per URL: `"N | SIGNAL | one sentence"` where SIGNAL is one of: `commercial`, `developer-docs`, `academic`, `government`, `informational`, `crypto/finance`, or `error/inaccessible`

Wait for all batches to complete, then apply triage rules to the returned signals:

Exclude if signal is: `developer-docs`, `academic`, `government`, `informational`, `crypto/finance`, `error/inaccessible`
→ Log: "Excluded [URL]: [signal]"

Keep if signal is: `commercial`
→ Carry forward to Step 7.

Additional commercial-but-no-overlap check: if the commercial description makes clear the entity operates in a completely unrelated industry (e.g., physical construction equipment, automotive dealerships, bathroom building products) with no plausible consumer overlap with `protected_mark_context`, exclude it.
→ Log: "Excluded [URL]: commercial but no goods/services overlap"

Report: "[N] leads after informational exclusion ([M] excluded in Stage 1, [P] skipped by attorney, [Q] excluded in Stage 2)"

---

## Step 7: Agentic Investigation and 8-Factor Threat Scoring

Process each remaining commercial lead ONE AT A TIME. Do not batch.

For each lead, using the WebFetch content already retrieved in Step 6 (or fetch now if not yet fetched):

**Assessment (three dimensions):**

1. COMMERCIALITY — Is this a for-profit entity selling goods or services?
   Evidence: prices, Buy/Shop/Cart buttons, service descriptions, subscription offers
   If clearly non-commercial (nonprofit with no commercial arm): skip scoring. Log: "Excluded [URL]: non-commercial entity"

2. TRADEMARK USAGE — Is the searched variant used as a brand identifier (source designator)?
   Evidence: variant appears in site title, logo alt text, domain name, product name, or as the company name
   Distinguish: variant used as a brand name vs. merely mentioned in passing

3. MARKET OVERLAP — Does the entity target a similar audience to the protected mark?
   Use `protected_mark_context` (extracted in Step 1) as the comparison baseline.
   Evidence: product category, customer descriptions, pricing tier, industry language

If both COMMERCIALITY and TRADEMARK USAGE are No: exclude. Log: "Excluded [URL]: no commercial trademark usage"

**8-Factor Scoring (for leads that pass assessment):**

Score using this table. For each factor, cite specific text from the fetched page content. Do not infer — quote or paraphrase directly from the page.

| Factor | Scale | Weight |
|--------|-------|--------|
| Mark Criticality | 0–3 | ×3 |
| Similarity (sight/sound/meaning) | 0–4 | ×3 |
| Goods/Services & Channels Overlap | 0–3 | ×3 |
| Geography Priority | 0–3 | ×2 |
| Evidence of Confusion/Association | 0–2 | ×2 |
| Rights Posture (ours vs. theirs) | 0–2 | ×2 |
| Counterparty Profile | 0–2 | ×1 |
| Enforcement Cost vs. Budget | 0–2 | ×1 |

Display the score block for each lead:

```
## [Entity Name] — [URL]
Variant: [variant name]

| Factor | Score | Weight | Subtotal | Evidence |
|--------|-------|--------|----------|---------|
| Mark Criticality | [0-3] | ×3 | [n] | [one sentence from page] |
| Similarity | [0-4] | ×3 | [n] | [one sentence from page] |
| Goods/Services Overlap | [0-3] | ×3 | [n] | [one sentence from page] |
| Geography Priority | [0-3] | ×2 | [n] | [one sentence from page] |
| Confusion Evidence | [0-2] | ×2 | [n] | [one sentence from page] |
| Rights Posture | [0-2] | ×2 | [n] | [one sentence from page] |
| Counterparty Profile | [0-2] | ×1 | [n] | [one sentence from page] |
| Enforcement Cost | [0-2] | ×1 | [n] | [one sentence from page] |

**Total: [N] — [High/Medium/Low]**
```

**Risk tier assignment:**
  Total ≥ 15 → High
  Total 10–14 → Medium
  Total < 10 → Low (drop — do not write to output)

**After scoring each lead:**
- If Low (< 10): log "Dropped [URL]: Low risk (score [N])" — do not include in output file
- If Medium or High: write the lead immediately to `hound_scored-[sanitized_name].json` (append to array)
- After writing, release the fetched page content from your working memory before processing the next lead

**Writing hound_scored-[TRADEMARK].json:**
Accumulate Medium and High leads. After all leads are processed, write the complete array to `hound_scored-[sanitized_name].json` using the Write tool.

Each entry must follow this JSON structure:
```json
{
  "url": "https://...",
  "variant": "VariantName",
  "title": "Page title",
  "entity_name": "Company or entity name",
  "industry": "Industry description",
  "factors": {
    "mark_criticality": {"score": N, "weight": 3, "evidence": "..."},
    "similarity": {"score": N, "weight": 3, "evidence": "..."},
    "goods_services_overlap": {"score": N, "weight": 3, "evidence": "..."},
    "geography_priority": {"score": N, "weight": 2, "evidence": "..."},
    "confusion_evidence": {"score": N, "weight": 2, "evidence": "..."},
    "rights_posture": {"score": N, "weight": 2, "evidence": "..."},
    "counterparty_profile": {"score": N, "weight": 1, "evidence": "..."},
    "enforcement_cost": {"score": N, "weight": 1, "evidence": "..."}
  },
  "total_score": N,
  "risk_tier": "High"
}
```

Report after all leads are processed:
> "[N] leads scored — High: [X], Medium: [Y], Low: [Z] (dropped)
> Scored leads written to: hound_scored-[sanitized_name].json"

After writing hound_scored-[sanitized_name].json, display the following run summary block in the conversation:

```
=== Trademark Hound Run Summary ===
Trademark: [TRADEMARK]
Run date: [today's date in YYYY-MM-DD]

  Raw SERP leads:              [N from Step 4 post-SERP count]
  Excluded by safelist:        [M from Step 5]
  Excluded by domain triage:   [Stage 1 count from Step 6]
  Skipped by attorney:         [Stage 1.5 count from Step 6]
  Excluded by content triage:  [Stage 2 count from Step 6]
  Scored leads (Med + High):   [count_high + count_medium]

  High (>= 15):                [count_high]
  Medium (10-14):              [count_medium]
  Low (< 10, dropped):         [count_low — calculate as investigated_count minus count_high minus count_medium]

Next step: Run `/trademark-report [TRADEMARK]` to generate the attorney report.
```

Track count_low as a running counter during the scoring loop: increment it each time a lead scores below 10 and is dropped.

This completes the Trademark Hound investigation phase. Run `/trademark-hound` again with a reviewed report path to update the safelist (Phase 3).

---

CRITICAL: Do NOT write any report file in this command. Report generation (HOUND_REPORT_[TRADEMARK]_[DATE].md) is handled separately. This command's terminal output is hound_scored-[sanitized_name].json.

---

## Safelist Ingestion (re-invocation mode only)

*Execute this section only when `mode = 'safelist_ingestion'`. Skip entirely in normal investigation mode (`mode = 'investigate'`).*

**Step SI-1: Verify report file exists**

Use the Read tool to check whether `[reviewed_report_path]` exists.

If it does NOT exist, output:
> "Report file not found: [reviewed_report_path]. Check the filename and try again."
Then stop.

Sanitize the trademark name for filenames (same rule as normal intake). Store as `sanitized_name`.

**Step SI-2: Load current safelist**

Check whether `safelist-[sanitized_name].json` exists.
- If yes: read it, parse as JSON array, store as `current_safelist`
- If no: set `current_safelist = []`

**Step SI-3: Parse THREAT? column from Attorney Review Table**

Read `[reviewed_report_path]`. Locate the "## Attorney Review Table" section.

For each data row in that table:
- Extract the THREAT? column value (last column). Trim whitespace. Compare case-insensitively.
- If THREAT? == "NO": collect the URL from the URL column of that row
- If THREAT? == "YES": note this URL as retained (count for summary)
- If THREAT? is blank, "-", "?", or any other value: skip this row (count as unreviewed / blank)

Track:
- `urls_to_add` = list of URLs where THREAT? == "NO" that are NOT already in `current_safelist`
- `count_yes` = number of YES rows
- `count_blank` = number of blank/unreviewed rows
- `count_already_in_safelist` = URLs where THREAT? == "NO" but URL is already in `current_safelist` (skip silently, do not re-add, do not increment add count)

**Blank THREAT? guard:** Blank, "-", "?", and any value other than "NO" or "YES" are explicitly skipped. These unreviewed entries are NOT added to safelist under any circumstances.

**Step SI-4: Atomic safelist write**

Merge `current_safelist` + `urls_to_add` into a single array (no duplicates — already filtered in SI-3).

Check for orphaned tmp file: use the Bash tool to run `ls safelist-[sanitized_name].json.tmp 2>/dev/null`. If it exists, run `rm safelist-[sanitized_name].json.tmp`.

Write the merged array to `safelist-[sanitized_name].json.tmp` using the Write tool.
Then run `mv safelist-[sanitized_name].json.tmp safelist-[sanitized_name].json` using the Bash tool to atomically replace the live file.

**Step SI-5: Report outcome (HND-19)**

Output:
> "=== Safelist Update Complete ===
> Trademark: [TRADEMARK]
> Report reviewed: [reviewed_report_path]
>
>   Entries marked NO (added to safelist):  [len(urls_to_add)]
>   Already in safelist (skipped):          [count_already_in_safelist]
>   Entries marked YES (retained):          [count_yes]
>   Entries blank / not yet reviewed:       [count_blank]
>
>   safelist-[sanitized_name].json now contains [len(merged)] total entries.
>   These URLs will be excluded from all future /trademark-hound runs."
