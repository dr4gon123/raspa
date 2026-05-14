# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

RASPA scrapes the Fortinet CLI configuration command reference for all configured FortiOS versions
and saves each command as a Markdown file (heading + syntax block + pipe-table parameters).

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run scraper (all versions)
python scrape_cli_ref.py

# Run scraper (targeted)
python scrape_cli_ref.py --version 8.0.0
python scrape_cli_ref.py --version 8.0.0 --section alertemail
python scrape_cli_ref.py --force          # rescrape existing files
python scrape_cli_ref.py --concurrency 10 # more parallel slots
python scrape_cli_ref.py --quiet          # warnings and errors only

# Run tests
pytest
```

## Architecture

Three modules + one config file + one versions file:

```
scrape_cli_ref.py   — async orchestrator, CLI, retry logic, concurrency
discover.py         — fetches TOC page, returns list of (section, slug, url)
extract.py          — parses SSR HTML, builds markdown; pure functions, no I/O
scraper.yaml        — all runtime tunables (see Configuration below)
versions.yaml       — list of FortiOS versions to scrape
```

### Data flow

1. `load_versions()` reads `versions.yaml`
2. For each version, `discover_commands(client, version)` fetches the TOC page and returns
   `list[tuple[section, slug, url]]` where every URL is a **numeric-ID URL**
   (e.g. `/cli-reference/239356323/config-alertemail-setting`).
3. Commands not yet on disk are gathered with `asyncio.gather` behind an
   `asyncio.Semaphore(cfg["concurrency"])`.
4. Each slot calls `_fetch` (with exponential backoff), then `extract_page` (BS4 parse),
   then `build_markdown`, then writes the `.md` file.

### Why numeric-ID URLs

The slug-based URL (e.g. `/cli-reference/alertemail/config-alertemail-setting`) serves
an SPA shell — same 1 MB JS bundle for every URL, content rendered client-side.
The numeric-ID URL (embedded in the TOC HTML) is fully server-rendered: `<h1>`, `<pre>`,
`<table>` are all present in the raw response. No browser or JavaScript needed.
The WAF only requires a real User-Agent header (not a full browser fingerprint).

## Configuration (`scraper.yaml`)

| Key | Default | Effect |
|-----|---------|--------|
| `force` | `false` | Rescrape files that already exist |
| `retries` | `3` | Max attempts per page |
| `delay` | `1.5` | Seconds between requests per concurrent slot |
| `timeout` | `30.0` | HTTP request timeout in seconds |
| `min_size` | `200` | Bytes — files larger than this are considered complete |
| `output_dir` | `"config"` | Output subdirectory under repo root |
| `user_agent` | Chrome 124 | User-Agent header for all requests |
| `quiet` | `false` | Suppress INFO logs |
| `concurrency` | `5` | `asyncio.Semaphore` size — max parallel fetches |

All keys can be overridden via CLI flags. Run `python scrape_cli_ref.py --help` for the full list.

## Output structure

```
config/
└── <major>/              # e.g. 7.6/
    └── <version>/        # e.g. 7.6.0/
        └── <section>/    # e.g. alertemail/
            └── <slug>.md # e.g. config_alertemail_setting.md
```

## Code conventions

All new code must follow these conventions.

### Language & imports
- **Python 3.10+** — use `X | None` unions, built-in generics, `match` where appropriate.
- **`from __future__ import annotations`** at the top of every module.
- **No `typing` module** — use built-in generics only: `list[str]`, `dict[str, str]`,
  `tuple[str, ...]`, `X | None`. Never `List`, `Dict`, `Optional`, `Tuple`.

### Type hints
- All function signatures must be fully annotated (parameters and return type).
- Return `None` explicitly when a function returns nothing meaningful.
- Use `X | None` for optional values — never `Optional[X]`.
- Use `list[str]`, `dict[str, int]`, `tuple[str, str]` — never `List`, `Dict`, `Tuple`.
- Annotate local variables when the type is not obvious from the right-hand side: `seen: set[str] = set()`.
- Type hints are not enforced at runtime — they exist for static checkers (mypy/pyright) and readability. Do not add `isinstance` guards based solely on a hint.

### File & path operations
- **`pathlib.Path` only** — never `os.path`, `os.makedirs`, `os.getcwd`, or `open()` with
  string paths. Use `Path.read_text()`, `Path.write_text()`, `Path.mkdir(parents=True, exist_ok=True)`.

### HTTP & async
- **`httpx.AsyncClient`** for all HTTP — never `requests` or `urllib`.
- One shared `AsyncClient` per run (created in `_run()`), passed down to all callers.
- All network functions are `async def`.
- **Retry via `_fetch()`** in `scrape_cli_ref.py` — exponential backoff
  (`delay * 2**attempt + jitter`), 429/Retry-After handling, 404 treated as permanent.
- **Concurrency via `asyncio.Semaphore(cfg["concurrency"])`** — never `ThreadPoolExecutor`.
  The semaphore wraps the fetch + write block; the politeness sleep is inside the semaphore.

### Logging
- **`logging.getLogger(__name__)`** in every module — never `print()`.
- Level conventions: `DEBUG` for skip messages, `INFO` for normal progress,
  `WARNING` for recoverable issues, `ERROR` for failures.
- Use `%`-style formatting in log calls (not f-strings): `logger.info("msg %s", var)`.

### HTML parsing
- **BeautifulSoup with `lxml` parser**: `BeautifulSoup(html_bytes, "lxml")`.
- Never use regex to parse HTML structure. Use BS4 tree traversal and `find`/`find_all`.

### Markdown tables
- **Pandoc grid tables** — `table_to_pandoc()` in `extract.py`. Must stay as grid tables.
  The Fortinet parameter table embeds nested option sub-tables inside cells; only pandoc's
  grid table format preserves this structure correctly. Pipe tables flatten nested HTML
  and produce unreadable output.
- `pypandoc_binary` is used (bundles the `pandoc` binary via pip — no system install needed).

### General style
- **`@dataclass` for structured results** — use when a function returns or accumulates multiple related fields with a fixed schema. Prefer attribute access over string-keyed dicts; typos become parse-time errors instead of silent `None`.
- **No `from __future__` workarounds for older Pythons** — target 3.10+ only.
- **`DEFAULT_CONFIG.copy()`** not `dict(DEFAULT_CONFIG)`.
- **`merge_args` stays a dict comprehension** — do not expand it back to per-key `if` blocks.
- **`argparse.BooleanOptionalAction`** for boolean flags (`--force/--no-force`).
- **One `_HERE = Path(__file__).resolve().parent`** at module top — never repeat the expression.
- Docstrings: one short line only. No `Args:`/`Returns:` blocks that restate the signature.
- No comments that describe *what* the code does — only *why* (hidden constraints, workarounds).

### Tests
- Unit-test pure utility functions in `tests/`.
- No `sys.path.insert` hacks — `conftest.py` at repo root handles path setup.
- Tests must not make real HTTP requests. Mock or use local HTML fixtures for network-dependent logic.
