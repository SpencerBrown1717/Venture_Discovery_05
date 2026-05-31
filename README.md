# AI Incorporation Scout Agent

> An autonomous agent that discovers newly formed companies from public sources,
> classifies how AI-related they are, builds intelligence on them, and surfaces
> the results in an investor-facing dashboard — *before* they hit mainstream
> startup databases.

This is a **Week 1** submission for the AI Incorporation Scout assignment, plus
a few **Week 2 stretch goals** (research memos, trend detection, and a natural
language query interface).

---

## What it does

```
            ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌──────────┐
 public ──▶ │  COLLECT   │─▶ │ CLASSIFY   │─▶ │ RESEARCH   │─▶ │  STORE   │
 sources    │ connectors │   │ AI score   │   │ memo agent │   │ SQLite   │
            └────────────┘   └────────────┘   └────────────┘   └────┬─────┘
                                                                     │ export
                                                                     ▼
                                                            ┌──────────────────┐
                                                            │ static dashboard │
                                                            │  (GitHub Pages)  │
                                                            └──────────────────┘
```

1. **Collect** newly formed company records from public sources (live SEC EDGAR
   Form D filings, plus a bundled offline sample dataset).
2. **Classify** each company's AI-relatedness with a transparent, calibrated
   confidence score (`0..1`) and a subsector category. Optional LLM upgrade.
3. **Research** (stretch goal) each promising company: visit its website,
   estimate market category & stage, and draft a one-page investment memo.
4. **Store** everything in a structured SQLite database (idempotent upserts).
5. **Export** a precomputed `data.json` powering a static, GitHub Pages–ready
   dashboard with grouping, sorting, filtering, trend charts, and NL search.

---

## Quick start

**Requirements:** Python 3.10+. The core pipeline uses only the standard
library — **no install required**.

```bash
# 1. Generate the bundled sample dataset (synthetic but realistic)
python -m scout gen-sample

# 2. Discover + classify + research from the offline sample, then export
python -m scout run --source sample --research --export

# 3. Open the dashboard
cd dashboard && python -m http.server 8000
# visit http://localhost:8000
```

That's it. The committed `dashboard/data.json` means the dashboard also works
the instant you deploy it — no pipeline run needed.

### Run against the live SEC EDGAR source

Form D filings (notices of exempt securities offerings) are filed by recently
formed entities raising their first private capital — a strong leading signal
for "newly formed company" discovery.

```bash
python -m scout run \
  --source sec_edgar \
  --query '"artificial intelligence"' \
  --days-back 120 --limit 50 \
  --user-agent "AI-Incorporation-Scout/0.1 (you@example.com)" \
  --research --export
```

> SEC's fair-access policy asks for a descriptive `User-Agent` with a contact
> email. No API key is required.

### Optional: LLM-powered classification & memos

```bash
pip install -r requirements.txt        # installs the optional `openai` client
export OPENAI_API_KEY=sk-...
python -m scout run --source sample --llm --research --export
```

If the key or package is missing, the pipeline **automatically falls back** to
the heuristic classifier and heuristic memos — it never hard-fails.

### CLI reference

| Command | Description |
| --- | --- |
| `python -m scout gen-sample` | (Re)generate the bundled sample dataset |
| `python -m scout run` | Discover → classify → (research) → store |
| `python -m scout export` | Re-export `dashboard/data.json` from the DB |
| `python -m scout stats` | Print database stats |

Useful `run` flags: `--source {sample,sec_edgar}`, `--limit N`, `--llm`,
`--research`, `--no-fetch-site`, `--export`, `--query`, `--days-back`,
`--forms`, `--user-agent`.

---

## Deploying the dashboard to GitHub Pages

The `dashboard/` folder is fully static (HTML/CSS/JS + `data.json`).

1. Commit `dashboard/` (including `data.json`).
2. In your repo settings → **Pages**, set the source to the `dashboard/` folder
   (or copy its contents to `/docs` or a `gh-pages` branch).
3. Done — the dashboard reads `data.json` relative to itself.

To refresh the data: re-run the pipeline with `--export`, then commit the
updated `dashboard/data.json`.

---

## Architecture

```
scout/
├── __main__.py          # CLI entrypoint (argparse)
├── pipeline.py          # orchestration: collect → classify → research → store
├── models.py            # Company dataclass + stable IDs (idempotent upserts)
├── db.py                # SQLite storage layer (schema, upsert, queries, stats)
├── export.py            # DB → dashboard/data.json + trend aggregation
├── seed.py              # deterministic sample-dataset generator
├── sources/             # pluggable data-source connectors
│   ├── base.py          #   Source ABC
│   ├── sample.py        #   offline bundled dataset
│   └── sec_edgar.py     #   live SEC EDGAR Form D full-text search
├── classify/            # AI-relatedness classification
│   ├── heuristic.py     #   transparent, calibrated keyword/logistic scorer
│   └── llm.py           #   optional OpenAI classifier (graceful fallback)
├── research/            # autonomous research agent (stretch goal 1)
│   └── memo.py          #   website visit + investment-memo generation
└── data/
    └── sample_companies.json

dashboard/               # static, GitHub Pages–ready front-end
├── index.html
├── styles.css
├── app.js
└── data.json            # precomputed export (committed for instant deploy)
```

### Data model

A `Company` carries collection metadata (name, source, jurisdiction, formation
date, website, description), classifier output (`ai_score`, `is_ai`,
`ai_signals`, `ai_category`), and an optional research `memo`. IDs are a
deterministic hash of `source + source_id`, so re-running the pipeline
**upserts** rather than duplicating.

### Classifier

The default heuristic classifier is intentionally **transparent**: every score
ships with the exact signals that produced it (e.g. `"machine learning (name)"`),
which matters for investor trust and for debugging false positives. Weighted
evidence (strong phrases like *"large language model"* count more than weak,
ambiguous tokens like a bare *"AI"*) is squashed through a logistic function
into a calibrated `0..1` confidence, with field weighting (a name match counts
more than a description match) and whole-word matching to avoid false positives
like *"Mountain **AI**r"*.

### Research agent (stretch goal 1)

For companies above a confidence threshold, the agent optionally fetches the
company website (dependency-free HTML→text extraction), estimates market
category and funding stage, and drafts a one-page memo: one-liner, thesis,
reasoning, market read, and key risks. It always produces a memo, degrading
from *LLM prose* → *site-enriched heuristic* → *metadata-only heuristic*.

### Trend detection (stretch goal 6)

`export.py` precomputes AI discovery momentum by month, category & geographic
distributions, and which categories are accelerating vs. cooling month over
month — rendered as charts in the dashboard's **Trend Intelligence** panel.

### Natural language interface (stretch goal 7)

The dashboard search box accepts queries like *"AI infrastructure companies
founded this month"* or *"developer tools last 30 days"*. A lightweight
client-side intent parser maps category synonyms, time windows, and confidence
intent onto the existing filter controls — no backend required.

---

## Design decisions

- **Standard-library core, optional everything else.** The pipeline runs with
  zero `pip install`. The LLM is an *enhancement*, never a dependency, so the
  project is reproducible on any machine. This keeps the "unlock" friction-free.
- **SQLite, not Postgres.** A single-file DB keeps the project portable and
  zero-setup while still giving real schema, indexes, and idempotent upserts.
  The `db.py` interface is small enough to swap for Postgres later.
- **Static dashboard with precomputed data.** All aggregation happens in Python
  and is baked into `data.json`. The front-end stays dependency-free and
  deploys to GitHub Pages with no build step — exactly the assignment's target.
- **Pluggable source connectors.** A `Source` ABC + registry means adding
  Companies House (UK), OpenCorporates, or state registries is a single new
  file. SEC EDGAR Form D was chosen as the first *live* source because it is
  free, key-less, and a genuine early-formation signal.
- **Fail-soft everywhere.** A bad record or flaky network degrades a single
  item, never the whole run — essential for an unattended, continuously running
  agent.
- **Transparent scoring.** Explainable signals over a black box, so an investor
  can trust (and audit) why a company surfaced.

---

## Known limitations

- **Sample data is synthetic.** `gen-sample` produces realistic-but-fake records
  so the demo runs offline. The live `sec_edgar` source pulls real filings.
- **Form D ≠ all new companies.** EDGAR Form D captures entities raising exempt
  securities; it misses companies that haven't raised, and includes some funds
  /SPVs. It's a high-signal *slice*, not full incorporation coverage. Adding a
  state-registry or Companies House connector would broaden the funnel.
- **Heuristic classifier has blind spots.** It keys on names/descriptions, so a
  genuinely-AI company with a generic name and no description can be missed
  (false negative), and a buzzword-stuffed non-AI company can score high (false
  positive). The `--llm` path mitigates this.
- **Website fetch is best-effort.** JS-heavy sites yield little text via the
  static fetch; many brand-new companies have no site yet.
- **Stage estimation is coarse.** Inferred from on-page/registry text cues only;
  no funding database is wired in yet.
- **No scheduler included.** Continuous operation (stretch goal 8) is a `cron`/
  GitHub Action away — the pipeline is already idempotent and incremental.

---

## Stretch goals included

- ✅ **Goal 1 — Autonomous Research Agent:** website visit + one-page investment
  memo (market category, stage, thesis, risks, reasoning).
- ✅ **Goal 6 — Trend Detection Engine:** month-over-month AI momentum, category
  & geographic distributions, accelerating/cooling sectors.
- ✅ **Goal 7 — Natural Language Interface:** plain-English dashboard queries.
- 🔜 Goals 2–5 & 8 (founders, scoring engine, multi-agent swarm, competitive
  maps, always-on platform) are natural extensions of the same architecture.
