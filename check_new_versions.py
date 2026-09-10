#!/usr/bin/env python3
"""
Check docs.fortinet.com for FortiOS releases missing from versions.yaml
and optionally add them.

Usage:
    python check_new_versions.py                    # report only
    python check_new_versions.py --update-config    # add new versions to versions.yaml
    python check_new_versions.py --github-output    # emit GitHub Actions outputs
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import random
import re
from dataclasses import dataclass, field
from pathlib import Path

import httpx
import yaml
from bs4 import BeautifulSoup

from scrape_cli_ref import DEFAULT_UA

_HERE = Path(__file__).resolve().parent
VERSIONS_FILE = _HERE / "versions.yaml"

# "Major" = the two-digit FortiOS branch (7.4, 7.6, 8.0, ...). Only branches at
# or above this floor are discovered; e.g. 7.2 and lower are never auto-added.
MIN_TRACKED_MAJOR = "7.4"

PRODUCT_URL = "https://docs.fortinet.com/product/fortigate"
BRANCH_URL = "https://docs.fortinet.com/product/fortigate/{branch}"
BASE_DELAY = 1.5
RETRIES = 3

BRANCH_KEY_RE = re.compile(r'^"(\d+\.\d+)":\s*$')
ENTRY_RE = re.compile(r"^\s+-\s+(\d+\.\d+\.\d+)\s*$")
BRANCH_HREF_RE = re.compile(r"product/fortigate/(\d+\.\d+)(?:[/?#]|$)")
CLI_HREF_RE = re.compile(r"/document/fortigate/(\d+\.\d+\.\d+)/cli-reference(?:[/?#]|$)")
LMR_HREF_RE = re.compile(
    r"/document/fortigate/(\d+\.\d+\.\d+)/fortios-log-message-reference(?:[/?#]|$)"
)

logger = logging.getLogger(__name__)


@dataclass
class ReleaseCheck:
    configured: list[str] = field(default_factory=list)
    discovered: list[str] = field(default_factory=list)
    new_versions: list[str] = field(default_factory=list)


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def branch_of(version: str) -> str:
    return ".".join(version.split(".")[:2])


async def _fetch(client: httpx.AsyncClient, url: str) -> httpx.Response:
    for attempt in range(RETRIES):
        try:
            logger.info("Fetching: %s", url)
            r = await client.get(url)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", BASE_DELAY * (2**attempt)))
                logger.warning("Rate limited (429) on %s — waiting %ss (attempt %d/%d)",
                               url, wait, attempt + 1, RETRIES)
                await asyncio.sleep(wait)
                continue
            r.raise_for_status()
            await asyncio.sleep(BASE_DELAY)
            return r
        except (httpx.TransportError, httpx.HTTPStatusError) as exc:
            if attempt < RETRIES - 1:
                wait = BASE_DELAY * (2**attempt) + random.uniform(0, 1)
                logger.warning("Error on %s: %s — retrying in %.1fs (attempt %d/%d)",
                               url, exc, wait, attempt + 1, RETRIES)
                await asyncio.sleep(wait)
            else:
                raise RuntimeError(
                    f"Failed {url} after {RETRIES} attempts: {exc}"
                ) from exc
    raise RuntimeError(f"Failed {url}: retries exhausted")


def extract_branches(html: bytes) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    branches = {
        match.group(1)
        for a in soup.find_all("a", href=True)
        if (match := BRANCH_HREF_RE.search(a["href"]))
    }
    if not branches:
        raise RuntimeError(
            f"No FortiOS branch links found on {PRODUCT_URL} — "
            "docs page layout may have changed"
        )
    return sorted(branches, key=version_key, reverse=True)


def extract_doc_versions(html: bytes, branch: str) -> tuple[set[str], set[str]]:
    """Return (cli-reference versions, log-message-reference versions) for a branch page."""
    soup = BeautifulSoup(html, "lxml")
    cli: set[str] = set()
    lmr: set[str] = set()
    for a in soup.find_all("a", href=True):
        if (match := CLI_HREF_RE.search(a["href"])):
            cli.add(match.group(1))
        elif (match := LMR_HREF_RE.search(a["href"])):
            lmr.add(match.group(1))
    if not cli or not lmr:
        raise RuntimeError(
            f"Missing doc links for branch {branch} "
            f"(cli-reference: {len(cli)}, log-message-reference: {len(lmr)}) — "
            "docs page layout may have changed"
        )
    return cli, lmr


def load_configured_versions() -> list[str]:
    data = yaml.safe_load(VERSIONS_FILE.read_text())
    versions = [str(v) for patches in data.values() for v in patches]
    if not versions:
        raise RuntimeError(f"No versions found in {VERSIONS_FILE}")
    return versions


async def discover_versions(client: httpx.AsyncClient, min_major: str) -> list[str]:
    branches = [
        branch
        for branch in extract_branches((await _fetch(client, PRODUCT_URL)).content)
        if version_key(branch) >= version_key(min_major)
    ]
    logger.info("Tracking branches at or above %s: %s", min_major, ", ".join(branches))

    discovered: set[str] = set()
    for branch in branches:
        cli, lmr = extract_doc_versions(
            (await _fetch(client, BRANCH_URL.format(branch=branch))).content, branch
        )
        # Only versions both scrapers can fetch are safe to add.
        both = cli & lmr
        logger.info("[%s] cli-reference: %d, log-message-reference: %d, both: %d",
                    branch, len(cli), len(lmr), len(both))
        discovered |= both
    return sorted(discovered, key=version_key)


def find_insert_index(lines: list[str], version: str) -> tuple[int, list[str]]:
    """Return (position, lines) for inserting version into versions.yaml, keeping
    branch blocks in ascending order and patches grouped under their branch key."""
    branch = branch_of(version)
    keys: list[tuple[int, str]] = [
        (i, match.group(1))
        for i, line in enumerate(lines)
        if (match := BRANCH_KEY_RE.match(line))
    ]
    if not keys:
        raise RuntimeError(f"No branch blocks found in {VERSIONS_FILE}")

    def block_end(key_index: int) -> int:
        following = [i for i, _ in keys if i > key_index]
        return min(following) if following else len(lines)

    for key_index, key in keys:
        if key == branch:
            entries = [
                i for i in range(key_index + 1, block_end(key_index))
                if ENTRY_RE.match(lines[i])
            ]
            return (entries[-1] + 1 if entries else key_index + 1), [f"  - {version}\n"]

    lower = [(i, key) for i, key in keys if version_key(key) < version_key(branch)]
    if lower:
        after = max(lower, key=lambda pair: version_key(pair[1]))
        return block_end(after[0]), [f'"{branch}":\n', f"  - {version}\n"]
    return keys[0][0], [f'"{branch}":\n', f"  - {version}\n"]


def update_versions(new_versions: list[str]) -> None:
    # Ascending order so patches stack in sequence inside a new branch block.
    for version in sorted(new_versions, key=version_key):
        lines = VERSIONS_FILE.read_text().splitlines(keepends=True)
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        index, insert_lines = find_insert_index(lines, version)
        lines[index:index] = insert_lines
        VERSIONS_FILE.write_text("".join(lines))

    configured = load_configured_versions()
    missing = [v for v in new_versions if v not in configured]
    if missing:
        raise RuntimeError(f"Config update failed, versions missing after write: {missing}")
    logger.info("Added %d version(s) to %s", len(new_versions), VERSIONS_FILE)


def display_versions(versions: list[str]) -> str:
    if len(versions) <= 2:
        return " and ".join(versions)
    return ", ".join(versions[:-1]) + " and " + versions[-1]


def write_github_output(check: ReleaseCheck) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        raise RuntimeError("--github-output set but GITHUB_OUTPUT is not defined")
    with Path(output_path).open("a") as f:
        f.write(f"count={len(check.new_versions)}\n")
        f.write(f"new_versions={json.dumps(check.new_versions)}\n")
        f.write(f"display={display_versions(check.new_versions)}\n")


async def run(min_major: str, update: bool) -> ReleaseCheck:
    configured = load_configured_versions()

    async with httpx.AsyncClient(
        headers={"User-Agent": DEFAULT_UA},
        follow_redirects=True,
        timeout=httpx.Timeout(30.0),
        http2=True,
    ) as client:
        discovered = await discover_versions(client, min_major)

    known = set(configured)
    new_versions = sorted(
        (v for v in discovered if v not in known), key=version_key, reverse=True
    )
    check = ReleaseCheck(
        configured=configured,
        discovered=sorted(discovered, key=version_key, reverse=True),
        new_versions=new_versions,
    )

    logger.info("Configured versions: %d, discovered: %d, new: %d",
                len(check.configured), len(check.discovered), len(new_versions))
    if not new_versions:
        logger.info("No new FortiOS releases found")
        return check

    logger.info("New FortiOS releases: %s", ", ".join(new_versions))
    if update:
        update_versions(new_versions)
    else:
        logger.info("Dry run (no --update-config): versions.yaml not modified")
    return check


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check docs.fortinet.com for new FortiOS releases and "
        "optionally add them to versions.yaml."
    )
    parser.add_argument("--update-config", action="store_true",
                        help="Add discovered versions to versions.yaml")
    parser.add_argument("--github-output", action="store_true",
                        help="Write results to $GITHUB_OUTPUT for GitHub Actions")
    parser.add_argument("--min-major", default=MIN_TRACKED_MAJOR,
                        help=f"Lowest FortiOS branch to track (default: {MIN_TRACKED_MAJOR})")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )
    check = asyncio.run(run(args.min_major, args.update_config))
    if args.github_output:
        write_github_output(check)


if __name__ == "__main__":
    main()
