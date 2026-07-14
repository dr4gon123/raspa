# RASPA — Developers Guide

This guide covers the internal architecture of the RASPA scrapers, the end-to-end
data flow for both targets (CLI command reference and FortiGuard web filter
categories), how HTML is parsed into Markdown, how to extend or retune the
scrapers, and a key-functions reference. It is written for maintainers and AI
assistants working on the codebase.

---

## Architecture Overview

RASPA is a four-module async scraper plus two YAML config files:

```
scrape_cli_ref.py   # CLI command reference: async orchestrator, CLI, retry, concurrency
scrape_log_ref.py   # log reference: FortiGuard web filter categories (one URL per version)
discover.py         # fetches CLI TOC page; returns list of (section, slug, url)
extract.py          # SSR HTML → Markdown; pure functions, no I/O
scraper.yaml        # all runtime tunables (shared by both scrapers)
versions.yaml       # list of FortiOS versions to scrape
```

There is no browser and no JavaScript. The original design used Playwright; that
was replaced by a plain `httpx` client once it was discovered that the
**numeric-ID URLs** returned by the table-of-contents page are fully
server-rendered (SSR) — `<h1>`, `<pre>`, and `<table>` are all present in the
raw response. The slug-based URL (e.g. `/cli-reference/alertemail/config-...`)
only serves a ~1 MB SPA shell and renders content client-side, so it is never
used for fetching. See [Why numeric-ID URLs](#why-numeric-id-urls) below.

All network I/O goes through a single shared `httpx.AsyncClient` per run
(`_run()`), created with HTTP/2 enabled, `follow_redirects=True`, and a real
Chrome User-Agent header. The WAF only requires a plausible User-Agent; no
browser fingerprint is needed.

---

## Script Flow — CLI command reference (`scrape_cli_ref.py`)

```
  versions.yaml          scraper.yaml
  (FortiOS versions)    (force, retries, delay,
                         timeout, min_size,
                         output_dir, user_agent,
                         quiet, concurrency)
          │                        │
          └───────────┬───────────┘
                      ▼
              load_config()  →  merge_args()
                      │
                      ▼
                load_versions(args.version)
                (flatten versions.yaml; optional --version filter)
                      │
                      ▼
                _run()  [async]
          ┌──────────────────────────────────────┐
          │ one shared httpx.AsyncClient for run  │
          │ for each version (sequential):         │
          │   scrape_version()                     │
          │     discover_commands(client, version) │
          │       GET TOC page                     │
          │       parse <a class="toc"> links      │
          │       → list[(section, slug, url)]     │
          │     optional --section / --command      │
          │     skip files already on disk          │
          │     asyncio.Semaphore(N)               │
          │     asyncio.gather(                     │
          │       process_one() × M                │
          │     )  ← M commands concurrent         │
          └──────────────────┬────────────────────┘
                             │ async HTTP GET (numeric-ID url)
                             ▼
                       _fetch()  [async]
                       ├─ 429 → honor Retry-After, retry
                       ├─ 404 → permanent; return None
                       ├─ raise_for_status()
                       └─ TransportError / HTTPStatusError
                          → exponential backoff + jitter, retry
                             │
                             ▼  (successful response)
                       extract_page(response.content)
                       BeautifulSoup("lxml")
                       ├─ <h1> followed by <pre>  → command_name
                       ├─ next <p> sibling         → description
                       ├─ first <pre> starting     │
                       │   with "config"            → syntax
                       └─ first <table>             → table_html
                             │
                  ┌──────────┴───────────┐
                  │                       │
                  ▼                       ▼
        table_to_pandoc(table_html)   build_markdown()
        pypandoc (HTML→grid table)    "# name\n\ndesc\n## Syntax\n..."
                  │                       │
                  └───────────┬───────────┘
                              ▼
                 output_path(repo_root, version, section, slug)
                 config/<major>/<version>/<section>/<slug>.md
                 out.write_text(content)
                              │
                              ▼
                   asyncio.sleep(cfg["delay"])  ← inside semaphore
```

---

## Script Flow — FortiGuard web filter categories (`scrape_log_ref.py`)

This scraper has **no discovery step**. One fixed URL is constructed per version
and all versions are fetched concurrently.

```
  versions.yaml          scraper.yaml
          │                        │
          └───────────┬───────────┘
                      ▼
                load_config() → merge_args()
                load_versions(args.version)
                      │
                      ▼
                _run()  [async]
          ┌──────────────────────────────────────┐
          │ one shared httpx.AsyncClient          │
          │ asyncio.Semaphore(N)                 │
          │ asyncio.gather( guarded(v) × V )      │
          │   guarded: scrape_version(client, v)  │
          └──────────────────┬────────────────────┘
                             │
                             ▼
              category_url(version)
              https://docs.fortinet.com/document/fortigate/<version>/
                fortios-log-message-reference/755423/
                fortiguard-web-filter-categories
                             │
                             ▼
                       _fetch()  (same retry/backoff as CLI scraper)
                             │
                             ▼
                       extract_categories(html)
                       ├─ <h1>                → title
                       └─ first <table>       → table_to_pandoc()
                             │
                             ▼
                       build_markdown(title, table)
                       "# title\n\n<table>\n"
                             │
                             ▼
                  output_path(version)
                  wfc/<major>/<version>/
                    fortiguard-web-filter-categories.md
                  out.write_text(content)
                             │
                             ▼
                   asyncio.sleep(cfg["delay"])
```

`scrape_log_ref.py` reuses the retry and config machinery from the CLI scraper
by importing `_fetch`, `load_config`, `load_versions`, and `merge_args` from
`scrape_cli_ref` — there is no duplicated fetch logic.

---

## Module Reference

### `discover.py` — `discover_commands(client, version)`

Fetches the CLI reference TOC page (`/document/fortigate/<version>/cli-reference/`)
and parses its `<a class="toc">` links with BeautifulSoup. Returns
`list[tuple[section, slug, url]]`.

Logic:
- Walk links until `slug == "cli-configuration-commands"`; only links after this
  marker are in the config-command section.
- Track the most recent **non-`config-`** slug as `current_section`. The first
  non-config slug before a block of `config-*` commands is the section name
  (e.g. `alertemail`).
- Each `config-*` link produces `(current_section, slug, numeric_id_url)`.
- Stop at `_SECTION_TERMINATORS` (`cli-diagnose-commands`, `cli-execute-commands`)
  — these mark the end of the config section.
- De-duplicate by slug via `seen_slugs`.
- Raise `RuntimeError` if nothing was found, so a restructured TOC page fails
  loudly instead of silently producing empty output.

The URLs returned are always the **numeric-ID URLs** embedded in the TOC HTML,
which is what makes the rest of the pipeline JS-free.

### `extract.py` — pure HTML → Markdown functions

No I/O here. All functions take bytes/strings and return strings or tuples.

| Function | Input | Output | Notes |
|----------|-------|--------|-------|
| `slug_to_filename(slug)` | `"config-alertemail-setting"` | `"config_alertemail_setting.md"` | Hyphens → underscores |
| `output_path(repo_root, version, section, slug, output_dir="config")` | path parts | `repo_root/output_dir/<major>/<version>/<section>/<slug>.md` | `major` = first two version components |
| `extract_page(html)` | raw bytes | `(command_name, description, syntax|None, table_html|None)` | Locates the content `<h1>` as the one followed by a `<pre>` (nav duplicates other `<h1>`s); syntax = first `<pre>` whose text starts with `"config"`; SSR `<pre>` uses `\r\n`, normalized to `\n` |
| `table_to_pandoc(table_html)` | HTML `<table>` string | Pandoc grid-table Markdown | Disables simple/multiline/pipe table extensions to force grid output (required for nested option sub-tables in cells) |
| `build_markdown(command_name, description, syntax, pandoc_table)` | extracted fields | full Markdown document | `# name`, description, `## Syntax` fenced block, `## Parameters` table. Falls back to a stub syntax and `_No parameter table found._` when extraction misses |

### `scrape_cli_ref.py` — orchestration

| Function | What it does |
|----------|--------------|
| `load_config()` | `DEFAULT_CONFIG.copy()` then overlay `scraper.yaml`. CLI flags override via `merge_args`. |
| `merge_args(cfg, args)` | Dict comprehension: keep only `args` keys present in `_OVERRIDABLE` with a non-`None` value. |
| `load_versions(filter_version)` | Flatten `versions.yaml` (a `{major: [patches]}` map) into a flat version list; optional exact `--version` filter. |
| `_fetch(client, url, cfg)` | Retry loop: 429 honors `Retry-After`; 404 is permanent (returns `None`); other errors use exponential backoff `delay * 2**attempt + random.uniform(0,1)`. Returns `httpx.Response | None`. |
| `scrape_version(client, version, filter_section, filter_command, cfg, failures)` | Discover → filter → skip existing → `asyncio.gather` over `process_one` behind a `Semaphore(cfg["concurrency"])`. |
| `process_one(section, slug, url, out)` | The per-command worker: fetch → extract → pandoc → build → write, all inside the semaphore; sleeps `cfg["delay"]` after writing. Appends to `failures` on fetch/parse failure. |
| `main()` | Build argparse, merge config, configure `logging`, `asyncio.run(_run(...))`. |

### `scrape_log_ref.py` — orchestration

| Function | What it does |
|----------|--------------|
| `category_url(version)` | Builds the fixed FortiGuard URL for a version. |
| `output_path(version)` | `wfc/<major>/<version>/fortiguard-web-filter-categories.md`. |
| `extract_categories(html)` | `(title, pandoc_table)` from the page's `<h1>` and first `<table>`; title falls back to `"FortiGuard web filter categories"`. |
| `build_markdown(title, table)` | `"# title\n\n<table>\n"`. |
| `scrape_version(client, version, cfg, failures)` | Skip-if-exists, fetch, extract, write; appends to `failures` on failure. |
| `_run(args)` | Load config/versions, shared `AsyncClient`, `Semaphore` + `gather` over all versions. |

---

## Why numeric-ID URLs

The TOC page links commands two ways:

- **Slug URL** — `/document/fortigate/7.6.0/cli-reference/alertemail/config-alertemail-setting`.
  This serves an SPA shell: the same ~1 MB JS bundle for every URL, content
  rendered client-side. Fetching it returns no `<h1>`/`<pre>`/`<table>` in the
  raw HTML, so BeautifulSoup finds nothing.
- **Numeric-ID URL** — embedded in the TOC HTML as
  `/document/fortigate/7.6.0/cli-reference/239356323/config-alertemail-setting`.
  This is the server-rendered permalink: all content is in the raw response.

`discover_commands` harvests the numeric-ID form directly from the TOC HTML, so
every downstream fetch is SSR and no browser is needed. If Fortinet changes the
TOC structure, `discover_commands` raises (no silent empty output).

---

## Configuration Reference

`scraper.yaml` holds all tunables. Every key can be overridden per-run by a CLI
flag (flags win). `output_dir` is read only by `scrape_cli_ref.py`;
`scrape_log_ref.py` always writes to `wfc/`.

| Key | Default | Effect |
|-----|---------|--------|
| `force` | `false` | Rescrape files that already exist |
| `retries` | `3` | Max attempts per page |
| `delay` | `1.5` | Seconds between requests per concurrent slot (politeness sleep, inside the semaphore) |
| `timeout` | `30.0` | HTTP request timeout in seconds |
| `min_size` | `200` | Bytes — files larger than this are considered complete and skipped |
| `output_dir` | `"config"` | Output subdirectory under repo root (CLI scraper only) |
| `user_agent` | Chrome 124 | User-Agent header for all requests |
| `quiet` | `false` | Suppress INFO logs (warnings/errors only) |
| `concurrency` | `5` | `asyncio.Semaphore` size — max parallel fetches |

With `delay=1.5` and `concurrency=5` the effective request rate per the
semaphore is ~3.3 req/s.

### CLI flags (`scrape_cli_ref.py`)

| Flag | Overrides | Notes |
|------|-----------|-------|
| `--version` | — | Scrape only this exact version |
| `--section` | — | Scrape only this section (e.g. `alertemail`) |
| `--command` | — | Partial slug match (spaces→hyphens); e.g. `--command "system global"` |
| `--force` / `--no-force` | `force` | `BooleanOptionalAction` |
| `--retries` | `retries` | |
| `--delay` | `delay` | |
| `--timeout` | `timeout` | |
| `--min-size` | `min_size` | |
| `--concurrency` | `concurrency` | |
| `--quiet` / `--no-quiet` | `quiet` | |

`scrape_log_ref.py` supports the same flags except `--section` and `--command`
(there is only one page per version).

---

## Adding a New FortiOS Version

Edit `versions.yaml`. The file is a map of `major → [patches]`:

```yaml
"8.0":
  - 8.0.0
  - 8.0.1
```

Adding a patch creates a new `<major>/<version>/` output tree on the next run.
No code change is required. For the CLI scraper, discovery is automatic from the
TOC page. For the web filter scraper, the URL is built from the version string
plus the fixed doc ID `755423`.

---

## Extending Extraction

All parsing lives in `extract.py` and is pure (no network, no disk). To handle a
new page shape:

1. **New command-page structure** — adjust `extract_page` (the `<h1>`/`<pre>`/`<table>`
   heuristics). Add a unit test in `tests/test_utils.py` with a local HTML fixture
   (never a real network call).
2. **Nested parameter tables** — keep `table_to_pandoc` forcing grid tables. If
   Pandoc ever drops grid support, the nested option sub-tables in parameter
   cells will flatten and become unreadable; do not switch to pipe tables.
3. **New scrape target** (e.g. IPS signatures, see `notes/`) — follow the
   `scrape_log_ref.py` pattern: a `category_url`-style builder, an
   `extract_*` function, a `build_markdown`, and a `output_path`, reusing
   `_fetch`/`load_config`/`load_versions`/`merge_args` from `scrape_cli_ref`.

---

## Retry & Backoff Behavior

`_fetch` (shared by both scrapers) retries up to `cfg["retries"]` times:

- **429 Too Many Requests** — sleep `int(Retry-After or delay * 2**attempt)`, then retry (does not count against the exponential backoff path).
- **404 Not Found** — treated as permanent; returns `None` and the command/version is recorded in `failures`.
- **Transport / HTTP status errors** — sleep `delay * 2**attempt + random.uniform(0,1)` (jitter) and retry.
- Final attempt failure → logged as `ERROR` and recorded in `failures`.

After a successful fetch, `process_one` (CLI) or `scrape_version` (log) sleeps
`cfg["delay"]` **inside the semaphore**, so concurrency is bounded and polite.

---

## Testing

`tests/` contains only pure-function unit tests (no network):

- `tests/test_utils.py` — `slug_to_filename`, `output_path`, `build_markdown`, `table_to_pandoc` from `extract.py`.
- `tests/test_log_ref.py` — `output_path`, `extract_categories`, `build_markdown` from `scrape_log_ref.py`.

Run with:

```bash
pytest -v
```

`conftest.py` at repo root adds the repo to `sys.path` so tests import
`extract`/`scrape_log_ref` directly. Tests must not make real HTTP requests —
use local HTML fixtures for any network-dependent logic.
