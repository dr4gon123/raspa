from __future__ import annotations

import asyncio
import logging
import random

import httpx
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://docs.fortinet.com/document/fortigate"

# Slugs that signal the end of the CLI configuration commands section in the TOC.
_SECTION_TERMINATORS = {"cli-diagnose-commands", "cli-execute-commands"}

logger = logging.getLogger(__name__)


def toc_url(version: str) -> str:
    return f"{BASE_URL}/{version}/cli-reference/"


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


def _is_toc_anchor(classes: str | list[str] | None) -> bool:
    # Fortinet renamed the TOC anchor class from "toc" to "toc__link" (BEM style).
    # BS4 passes each class token individually (plus the joined value), or None
    # for anchors without a class attribute.
    if not classes:
        return False
    parts = classes if isinstance(classes, list) else classes.split()
    return any(c == "toc" or c.startswith("toc__") for c in parts)


def _is_toc_leaf(classes: str | list[str] | None) -> bool:
    if not classes:
        return False
    parts = classes if isinstance(classes, list) else classes.split()
    return "toc__leaf" in parts


def _is_leaf_anchor(a: Tag) -> bool:
    """True when the TOC anchor is a command page rather than an expandable node.

    In the current TOC markup every anchor sits in a <span class="toc__label">
    next to either a <span class="toc__leaf"> (command page) or a
    <button class="toc__toggle"> (expandable section node).
    """
    label = a.parent
    return label is not None and label.find(class_=_is_toc_leaf) is not None


def parse_toc_commands(html: bytes) -> list[tuple[str, str, str]]:
    """Parse TOC HTML into (section, slug, url) tuples for all config commands."""
    soup = BeautifulSoup(html, "lxml")
    links = soup.find_all("a", class_=_is_toc_anchor, href=True)

    in_config_section = False
    current_section: str | None = None
    seen_slugs: set[str] = set()
    results: list[tuple[str, str, str]] = []

    for a in links:
        href: str = a["href"]
        slug = href.rstrip("/").split("/")[-1]

        if slug == "cli-configuration-commands":
            in_config_section = True
            continue
        if not in_config_section:
            continue
        if slug in _SECTION_TERMINATORS:
            break

        url = href if href.startswith("http") else f"https://docs.fortinet.com{href}"

        if slug.startswith("config-"):
            if not _is_leaf_anchor(a):
                # FortiOS 8 TOCs name expandable section pages config-* (e.g.
                # config-alertemail); store the section without the prefix so
                # output paths match the 7.x layout (alertemail/).
                current_section = slug.removeprefix("config-")
            elif current_section is not None and slug not in seen_slugs:
                results.append((current_section, slug, url))
                seen_slugs.add(slug)
        else:
            current_section = slug

    return results


async def discover_commands(
    client: httpx.AsyncClient,
    version: str,
    cfg: dict,
) -> list[tuple[str, str, str]]:
    """
    Return list of (section, slug, url) for all config commands in a version.

    Fetches the CLI reference TOC page (with retries) and parses <a> TOC anchors.
    The TOC URL redirects to a numeric-ID landing page (e.g.
    /cli-reference/84566/fortios-cli-reference) whose TOC is fully
    server-rendered — no JavaScript execution required. The section is the most
    recent non-config- slug seen before each command.
    """
    response = await _fetch(client, toc_url(version), cfg)
    if response is None:
        raise RuntimeError(f"discover_commands: TOC page for {version!r} could not be fetched")

    results = parse_toc_commands(response.content)
    if not results:
        raise RuntimeError(
            f"discover_commands: no config commands found for {version!r}. "
            "Check the selector or TOC structure — Fortinet may have restructured the page."
        )

    return results
