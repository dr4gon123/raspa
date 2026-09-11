# RASPA — FortiOS CLI Reference Scraper

Async `httpx`-based scraper that fetches FortiOS CLI `config` command
reference pages from docs.fortinet.com and saves them as structured
Markdown files with Pandoc Grid Tables. No browser or JavaScript required —
numeric-ID URLs are fully server-rendered.

The `config/` directory contains the pre-scraped output, organized as:

    config/<major>/<patch>/<section>/<config_command>.md

## Versions covered

See `versions.yaml` for the full list. Currently: 7.4.x, 7.6.x, 8.0.x.

New releases are picked up automatically: a scheduled GitHub Action
(`.github/workflows/check-fortios-releases.yml`) checks docs.fortinet.com every
Monday at 06:00 UTC for FortiOS versions (7.4+) missing from `versions.yaml`,
adds them, runs both scrapers, and pushes the result to `main`. On the 1st of
each month (and on manual runs) both scrapers also run when nothing is new,
backfilling pages that failed in earlier runs — commits are only made when
files actually changed. It can also be triggered manually via
*Actions → Check FortiOS releases → Run workflow*. To
check locally without modifying `versions.yaml`: `python check_new_versions.py`.

## Usage

```bash
pip install -r requirements.txt

# Scrape a single version + section (quick test)
python scrape_cli_ref.py --version 8.0.0 --section alertemail

# Scrape one full version
python scrape_cli_ref.py --version 7.4.0

# Scrape everything (skip already-scraped files)
python scrape_cli_ref.py

# Force re-scrape
python scrape_cli_ref.py --force

# Scrape FortiGuard web filter categories
python scrape_log_ref.py
```

See `scrape_cli_ref.py --help` and `scrape_log_ref.py --help` for all flags.
Runtime tunables (concurrency, retries, timeouts, etc.) live in `scraper.yaml`.

## Running tests

```bash
pytest -v
```

## Prerequisites

- Python 3.10+
- `pypandoc_binary` bundles the Pandoc binary, so no system Pandoc install is needed.
