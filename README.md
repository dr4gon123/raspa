# RASPA — FortiOS CLI Reference Scraper

Async `httpx`-based scraper that fetches FortiOS CLI `config` command
reference pages from docs.fortinet.com and saves them as structured
Markdown files with Pandoc Grid Tables. No browser or JavaScript required —
numeric-ID URLs are fully server-rendered.

The `config/` directory contains the pre-scraped output, organized as:

    config/<major>/<patch>/<section>/<config_command>.md

## Versions covered

See `versions.yaml` for the full list. Currently: 7.4.x, 7.6.x, 8.0.x.

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
