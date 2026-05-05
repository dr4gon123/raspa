# RASPA — FortiOS CLI Reference Scraper

Playwright-based scraper that fetches all FortiOS CLI `config` command
reference pages from docs.fortinet.com and saves them as structured
Markdown files with Pandoc Grid Tables.

The `config/` directory contains the pre-scraped output, organized as:

    config/<major>/<patch>/<section>/<config_command>.md

## Versions covered

See `versions.yaml` for the full list. Currently: 7.4.x, 7.6.x, 8.0.x.

## Usage

```bash
pip install -r requirements.txt
playwright install chromium

# Scrape a single version + section (quick test)
python scrape_cli_ref.py --version 8.0.0 --section alertemail

# Scrape one full version
python scrape_cli_ref.py --version 7.4.0

# Scrape everything (skip already-scraped files)
python scrape_cli_ref.py

# Force re-scrape
python scrape_cli_ref.py --force
```

## Running tests

```bash
pytest tests/ -v
```

## Prerequisites

- Python 3.11+
- Pandoc system binary: `sudo dnf install pandoc` (Fedora) or `sudo apt install pandoc` (Debian/Ubuntu)
