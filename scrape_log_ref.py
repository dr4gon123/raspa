#!/usr/bin/env python3
"""
Scrape FortiGuard web filter categories page for all configured FortiOS versions.

Usage:
    python scrape_log_ref.py                    # all versions
    python scrape_log_ref.py --version 8.0.0    # one version
    python scrape_log_ref.py --force            # rescrape existing files
    python scrape_log_ref.py --quiet            # warnings and errors only
"""
from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from extract import table_to_pandoc
from scrape_cli_ref import _fetch, load_config, load_versions, merge_args

_HERE = Path(__file__).resolve().parent

_DOC_ID = "755423"
_CATEGORY_SLUG = "fortiguard-web-filter-categories"
_OUTPUT_SUBDIR = "wfc"

logger = logging.getLogger(__name__)


def category_url(version: str) -> str:
    return (
        f"https://docs.fortinet.com/document/fortigate/{version}"
        f"/fortios-log-message-reference/{_DOC_ID}/{_CATEGORY_SLUG}"
    )


def output_path(version: str) -> Path:
    major = ".".join(version.split(".")[:2])
    return _HERE / _OUTPUT_SUBDIR / major / version / f"{_CATEGORY_SLUG}.md"


def extract_categories(html: bytes) -> tuple[str, str]:
    """Extract (page_title, pandoc_table) from the categories page HTML."""
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else "FortiGuard web filter categories"
    table = soup.find("table")
    md_table = table_to_pandoc(str(table)) if table else "_No category table found._"
    return title, md_table


def build_markdown(title: str, table: str) -> str:
    return f"# {title}\n\n{table}\n"


async def scrape_version(
    client: httpx.AsyncClient,
    version: str,
    cfg: dict,
    failures: list[str],
) -> None:
    out = output_path(version)
    if not cfg["force"] and out.exists() and out.stat().st_size > cfg["min_size"]:
        logger.debug("[%s] SKIP (exists)", version)
        return
    url = category_url(version)
    logger.info("[%s] fetching %s", version, url)
    response = await _fetch(client, url, cfg)
    if response is None:
        failures.append(version)
        return
    try:
        title, table = extract_categories(response.content)
        content = build_markdown(title, table)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        logger.info("[%s] wrote %s", version, out.relative_to(_HERE))
    except Exception as exc:
        logger.error("[%s] ERROR: %s", version, exc)
        failures.append(version)
    await asyncio.sleep(cfg["delay"])


async def _run(args: argparse.Namespace) -> None:
    cfg = load_config()
    cfg = merge_args(cfg, args)

    versions = load_versions(args.version)
    if not versions:
        logger.warning("No versions matched — check versions.yaml or --version argument.")
        return

    logger.info("Scraping %d version(s): %s", len(versions), ", ".join(versions))

    failures: list[str] = []

    async with httpx.AsyncClient(
        headers={"User-Agent": cfg["user_agent"]},
        timeout=httpx.Timeout(cfg["timeout"]),
        follow_redirects=True,
        http2=True,
    ) as client:
        sem = asyncio.Semaphore(cfg["concurrency"])

        async def guarded(version: str) -> None:
            async with sem:
                await scrape_version(client, version, cfg, failures)

        await asyncio.gather(*(guarded(v) for v in versions))

    if failures:
        logger.warning("%d version(s) failed: %s", len(failures), ", ".join(failures))

    logger.info("Done.")


def main() -> None:
    cfg = load_config()

    parser = argparse.ArgumentParser(
        description="Scrape FortiGuard web filter categories for all FortiOS versions."
    )
    parser.add_argument("--version", help="Scrape only this version (e.g. 8.0.0)")
    parser.add_argument("--force", action=argparse.BooleanOptionalAction, default=None,
                        help="Force rescrape even if files exist")
    parser.add_argument("--retries", type=int, help="Max retry attempts per page")
    parser.add_argument("--delay", type=float, help="Seconds between requests per concurrent slot")
    parser.add_argument("--timeout", type=float, help="HTTP request timeout in seconds")
    parser.add_argument("--min-size", dest="min_size", type=int,
                        help="Min file size (bytes) to consider a file already scraped")
    parser.add_argument("--concurrency", type=int,
                        help="Max parallel fetches — semaphore size (default 5)")
    parser.add_argument("--quiet", action=argparse.BooleanOptionalAction, default=None,
                        help="Suppress INFO output (warnings and errors only)")
    args = parser.parse_args()

    cfg = merge_args(cfg, args)
    logging.basicConfig(
        level=logging.WARNING if cfg["quiet"] else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )

    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
