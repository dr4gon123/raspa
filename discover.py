from __future__ import annotations

import logging

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://docs.fortinet.com/document/fortigate"

# Slugs that signal the end of the CLI configuration commands section in the TOC.
_SECTION_TERMINATORS = {"cli-diagnose-commands", "cli-execute-commands"}

logger = logging.getLogger(__name__)


async def discover_commands(client: httpx.AsyncClient, version: str) -> list[tuple[str, str, str]]:
    """
    Return list of (section, slug, url) for all config commands in a version.

    Fetches the CLI reference TOC page and parses <a class="toc"> links.
    The TOC HTML contains numeric-ID URLs (e.g. /cli-reference/239356323/config-alertemail-setting)
    which are fully server-rendered — no JavaScript execution required.
    The section is the most recent non-config- slug seen before each command.
    """
    toc_url = f"{BASE_URL}/{version}/cli-reference/"
    r = await client.get(toc_url)
    r.raise_for_status()

    soup = BeautifulSoup(r.content, "lxml")
    links = soup.find_all("a", class_="toc", href=True)

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
            if current_section is not None and slug not in seen_slugs:
                results.append((current_section, slug, url))
                seen_slugs.add(slug)
        else:
            current_section = slug

    if not results:
        raise RuntimeError(
            f"discover_commands: no config commands found for {version!r}. "
            "Check the selector or TOC structure — Fortinet may have restructured the page."
        )

    return results
