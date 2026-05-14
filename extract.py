from __future__ import annotations

import logging
from pathlib import Path

import pypandoc
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def slug_to_filename(slug: str) -> str:
    return slug.replace("-", "_") + ".md"


def output_path(repo_root: Path, version: str, section: str, slug: str, output_dir: str = "config") -> Path:
    major = ".".join(version.split(".")[:2])
    return repo_root / output_dir / major / version / section / slug_to_filename(slug)


def table_to_pandoc(table_html: str) -> str:
    # Disable simple/multiline/pipe table extensions to force grid table output.
    # Grid tables are required because parameter cells contain nested option sub-tables.
    return pypandoc.convert_text(
        table_html,
        "markdown-simple_tables-multiline_tables-pipe_tables",
        format="html",
    )


def build_markdown(command_name: str, description: str, syntax: str | None, pandoc_table: str | None) -> str:
    if syntax is None:
        logger.warning("no syntax block found for %r — using fallback", command_name)
    fallback = f"{command_name}\n    set <parameter> <value>\nend"
    parts = [
        f"# {command_name}",
        "",
        description,
        "",
        "## Syntax",
        "",
        "```",
        syntax or fallback,
        "```",
        "",
        "## Parameters",
        "",
        pandoc_table if pandoc_table else "_No parameter table found._",
    ]
    return "\n".join(parts) + "\n"


def extract_page(html: bytes) -> tuple[str, str, str | None, str | None]:
    """
    Extract (command_name, description, syntax | None, table_html | None) from raw HTML.

    Expects the fully server-rendered numeric-ID URL page. The slug-based URL
    serves an SPA shell with no content; the numeric-ID URL is SSR.
    """
    soup = BeautifulSoup(html, "lxml")

    # The page has multiple <h1> elements (navigation duplicates).
    # The content h1 is the one immediately followed by a <pre> syntax block.
    h1 = next(
        (h for h in soup.find_all("h1") if h.find_next_sibling("pre")),
        soup.find("h1"),
    )
    command_name = h1.get_text(strip=True) if h1 else ""

    # First <p> sibling after the content h1 is the description sentence
    sibling_p = h1.find_next_sibling("p") if h1 else None
    description = sibling_p.get_text(strip=True) if sibling_p else ""

    # First <pre> whose text starts with "config".
    # SSR HTML uses \r\n line endings inside <pre>; normalize to \n.
    syntax: str | None = None
    for pre in soup.find_all("pre"):
        text = pre.get_text(strip=True).replace("\r\n", "\n").replace("\r", "\n")
        if text.startswith("config"):
            syntax = text
            break

    # First <table> in the page body
    table = soup.find("table")
    table_html: str | None = str(table) if table else None

    return command_name, description, syntax, table_html
