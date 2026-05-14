#!/usr/bin/env python3
"""
Scrape Fortinet CLI configuration command reference pages and save as markdown.

Usage:
    python scrape_cli_ref.py                                        # all versions
    python scrape_cli_ref.py --version 8.0.0                        # one version
    python scrape_cli_ref.py --version 8.0.0 --section alertemail   # one section
    python scrape_cli_ref.py --force                                # rescrape everything
    python scrape_cli_ref.py --no-force                             # skip existing (default)
    python scrape_cli_ref.py --retries 5 --timeout 60              # more patient
    python scrape_cli_ref.py --concurrency 10                       # more parallel slots
    python scrape_cli_ref.py --quiet                               # warnings and errors only
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import random
from pathlib import Path

import httpx
import yaml

from discover import discover_commands
from extract import build_markdown, extract_page, output_path, table_to_pandoc

_HERE = Path(__file__).resolve().parent
VERSIONS_FILE = _HERE / "versions.yaml"
CONFIG_FILE = _HERE / "scraper.yaml"

DEFAULT_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
DEFAULT_CONFIG: dict = {
    "force": False,
    "retries": 3,
    "delay": 1.5,        # seconds between requests per concurrent slot
    "timeout": 30.0,     # HTTP request timeout in seconds
    "min_size": 200,     # bytes — skip existing files larger than this
    "output_dir": "config",
    "user_agent": DEFAULT_UA,
    "quiet": False,
    "concurrency": 5,    # asyncio.Semaphore size
}
_OVERRIDABLE = frozenset(DEFAULT_CONFIG)

logger = logging.getLogger(__name__)


def load_config() -> dict:
    cfg = DEFAULT_CONFIG.copy()
    if CONFIG_FILE.exists():
        file_cfg = yaml.safe_load(CONFIG_FILE.read_text())
        if file_cfg:
            cfg.update(file_cfg)
    return cfg


def merge_args(cfg: dict, args: argparse.Namespace) -> dict:
    overrides = {k: v for k, v in vars(args).items() if k in _OVERRIDABLE and v is not None}
    return {**cfg, **overrides}


def load_versions(filter_version: str | None = None) -> list[str]:
    data = yaml.safe_load(VERSIONS_FILE.read_text())
    versions = [str(v) for patch_list in data.values() for v in patch_list]
    if filter_version:
        versions = [v for v in versions if v == filter_version]
    return versions


async def _fetch(client: httpx.AsyncClient, url: str, cfg: dict) -> httpx.Response | None:
    for attempt in range(cfg["retries"]):
        try:
            r = await client.get(url)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", cfg["delay"] * (2 ** attempt)))
                logger.warning("Rate limited (429) on %s — waiting %ss (attempt %d/%d)",
                               url, wait, attempt + 1, cfg["retries"])
                await asyncio.sleep(wait)
                continue
            if r.status_code == 404:
                logger.warning("Not found (404): %s", url)
                return None
            r.raise_for_status()
            return r
        except (httpx.TransportError, httpx.HTTPStatusError) as exc:
            if attempt < cfg["retries"] - 1:
                wait = cfg["delay"] * (2 ** attempt) + random.uniform(0, 1)
                logger.warning("Error on %s: %s — retrying in %.1fs (attempt %d/%d)",
                               url, exc, wait, attempt + 1, cfg["retries"])
                await asyncio.sleep(wait)
            else:
                logger.error("Failed %s after %d attempts: %s", url, cfg["retries"], exc)
    return None


async def scrape_version(
    client: httpx.AsyncClient,
    version: str,
    filter_section: str | None,
    filter_command: str | None,
    cfg: dict,
    failures: list[str],
) -> None:
    logger.info("=== Discovering %s ===", version)
    commands = await discover_commands(client, version)

    if filter_section:
        commands = [(s, sl, u) for s, sl, u in commands if s == filter_section]
    if filter_command:
        cmd_filter = filter_command.lower().replace(" ", "-")
        commands = [(s, sl, u) for s, sl, u in commands if cmd_filter in sl.lower()]

    to_fetch: list[tuple[str, str, str, Path]] = []
    for section, slug, url in commands:
        out = output_path(_HERE, version, section, slug, output_dir=cfg["output_dir"])
        if not cfg["force"] and out.exists() and out.stat().st_size > cfg["min_size"]:
            logger.debug("[%s] SKIP %s/%s", version, section, slug)
        else:
            to_fetch.append((section, slug, url, out))

    logger.info("[%s] %d to fetch, %d skipped", version, len(to_fetch), len(commands) - len(to_fetch))

    sem = asyncio.Semaphore(cfg["concurrency"])

    async def process_one(section: str, slug: str, url: str, out: Path) -> None:
        async with sem:
            logger.info("[%s] %s/%s", version, section, slug)
            response = await _fetch(client, url, cfg)
            if response is None:
                failures.append(f"{version}/{section}/{slug}")
                return
            try:
                name, desc, syntax, table_html = extract_page(response.content)
                pandoc_table = table_to_pandoc(table_html) if table_html else None
                content = build_markdown(name, desc, syntax, pandoc_table)
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(content, encoding="utf-8")
            except Exception as exc:
                logger.error("[%s] ERROR processing %s/%s: %s", version, section, slug, exc)
                failures.append(f"{version}/{section}/{slug}")
            await asyncio.sleep(cfg["delay"])

    await asyncio.gather(*(process_one(s, sl, u, out) for s, sl, u, out in to_fetch))


async def _run(args: argparse.Namespace) -> None:
    config = load_config()
    config = merge_args(config, args)

    versions = load_versions(args.version)
    if not versions:
        logger.warning("No versions matched — check versions.yaml or --version argument.")
        return

    logger.info("Scraping %d version(s): %s", len(versions), ", ".join(versions))

    failures: list[str] = []
    async with httpx.AsyncClient(
        headers={"User-Agent": config["user_agent"]},
        timeout=httpx.Timeout(config["timeout"]),
        follow_redirects=True,
        http2=True,
    ) as client:
        for version in versions:
            await scrape_version(client, version, args.section, args.command, config, failures)

    if failures:
        logger.warning("%d command(s) failed:", len(failures))
        for f in failures:
            logger.warning("  %s", f)

    logger.info("Done.")


def main() -> None:
    config = load_config()

    parser = argparse.ArgumentParser(description="Scrape Fortinet CLI reference docs.")
    parser.add_argument("--version", help="Scrape only this version (e.g. 8.0.0)")
    parser.add_argument("--section", help="Scrape only this section (e.g. alertemail)")
    parser.add_argument("--command", help="Scrape commands matching this slug (spaces→hyphens, partial match)")
    parser.add_argument("--force", action=argparse.BooleanOptionalAction, default=None,
                        help="Force rescrape even if files exist")
    parser.add_argument("--retries", type=int, help="Max retry attempts per page")
    parser.add_argument("--delay", type=float, help="Seconds between requests per concurrent slot")
    parser.add_argument("--timeout", type=float, help="HTTP request timeout in seconds")
    parser.add_argument("--min-size", dest="min_size", type=int,
                        help="Min file size (bytes) to consider a file already scraped")
    parser.add_argument("--concurrency", type=int,
                        help="Max parallel page fetches — semaphore size (default 5)")
    parser.add_argument("--quiet", action=argparse.BooleanOptionalAction, default=None,
                        help="Suppress INFO output (warnings and errors only)")
    args = parser.parse_args()

    config = merge_args(config, args)
    logging.basicConfig(
        level=logging.WARNING if config["quiet"] else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )

    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
