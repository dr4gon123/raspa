from scrape_log_ref import build_markdown, extract_categories, output_path


def test_output_path_structure():
    p = output_path("8.0.0")
    assert p.name == "fortiguard-web-filter-categories.md"
    assert p.parent.name == "8.0.0"
    assert p.parent.parent.name == "8.0"
    assert p.parent.parent.parent.name == "wfc"


def test_output_path_major_derived_from_version():
    p = output_path("7.4.3")
    assert p.parent.name == "7.4.3"
    assert p.parent.parent.name == "7.4"
    assert p.parent.parent.parent.name == "wfc"


def test_extract_categories_with_table():
    html = b"""
    <html><body>
    <h1>FortiGuard web filter categories</h1>
    <table>
      <thead><tr><th>Category ID</th><th>Category Name</th></tr></thead>
      <tbody><tr><td>1</td><td>Drug Abuse</td></tr></tbody>
    </table>
    </body></html>
    """
    title, table = extract_categories(html)
    assert title == "FortiGuard web filter categories"
    assert "Category ID" in table
    assert "Drug Abuse" in table


def test_extract_categories_no_table():
    html = b"<html><body><h1>FortiGuard web filter categories</h1></body></html>"
    title, table = extract_categories(html)
    assert title == "FortiGuard web filter categories"
    assert table == "_No category table found._"


def test_extract_categories_no_h1_fallback():
    html = b"<html><body><p>some content</p></body></html>"
    title, _ = extract_categories(html)
    assert title == "FortiGuard web filter categories"


def test_build_markdown():
    md = build_markdown("FortiGuard web filter categories", "TABLE_CONTENT")
    assert "# FortiGuard web filter categories" in md
    assert "TABLE_CONTENT" in md
