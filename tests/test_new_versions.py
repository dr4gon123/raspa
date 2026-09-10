from pathlib import Path

import yaml

import check_new_versions as cnv
from check_new_versions import (
    branch_of,
    display_versions,
    extract_doc_versions,
    find_insert_index,
    update_versions,
    version_key,
)

VERSIONS_YAML = """\
# Manually maintained list of FortiOS versions to scrape.
# Add new patch releases as Fortinet publishes them.
"7.4":
  - 7.4.0
  - 7.4.11
"7.6":
  - 7.6.0
  - 7.6.6
"8.0":
  - 8.0.0
"""


def test_version_key_numeric_ordering():
    assert version_key("7.4.9") < version_key("7.4.10")
    assert version_key("7.9.0") < version_key("8.0.0")


def test_branch_of():
    assert branch_of("7.6.7") == "7.6"


def test_display_versions():
    assert display_versions(["7.6.7"]) == "7.6.7"
    assert display_versions(["7.4.12", "7.6.7"]) == "7.4.12 and 7.6.7"
    assert display_versions(["7.4.12", "7.6.7", "8.0.1"]) == "7.4.12, 7.6.7 and 8.0.1"


def test_find_insert_index_existing_branch_appends():
    lines = VERSIONS_YAML.splitlines(keepends=True)
    index, insert_lines = find_insert_index(lines, "7.6.7")
    assert lines[index - 1] == '  - 7.6.6\n'
    assert insert_lines == ["  - 7.6.7\n"]


def test_find_insert_index_new_branch_in_middle():
    lines = VERSIONS_YAML.splitlines(keepends=True)
    index, insert_lines = find_insert_index(lines, "7.8.0")
    assert lines[index] == '"8.0":\n'
    assert insert_lines == ['"7.8":\n', "  - 7.8.0\n"]


def test_find_insert_index_new_top_branch_at_end():
    lines = VERSIONS_YAML.splitlines(keepends=True)
    index, insert_lines = find_insert_index(lines, "8.1.0")
    assert index == len(lines)
    assert insert_lines == ['"8.1":\n', "  - 8.1.0\n"]


def test_find_insert_index_branch_below_all():
    lines = VERSIONS_YAML.splitlines(keepends=True)
    index, insert_lines = find_insert_index(lines, "7.2.0")
    assert lines[index] == '"7.4":\n'
    assert insert_lines == ['"7.2":\n', "  - 7.2.0\n"]


def test_update_versions_preserves_comments_and_settings(tmp_path, monkeypatch):
    versions_file = tmp_path / "versions.yaml"
    versions_file.write_text(VERSIONS_YAML)
    monkeypatch.setattr(cnv, "VERSIONS_FILE", versions_file)

    update_versions(["7.6.7", "7.4.12", "7.8.0"])

    text = versions_file.read_text()
    assert text.startswith("# Manually maintained list")
    data = yaml.safe_load(text)
    assert data["7.6"] == ["7.6.0", "7.6.6", "7.6.7"]
    assert data["7.4"] == ["7.4.0", "7.4.11", "7.4.12"]
    assert data["7.8"] == ["7.8.0"]
    assert data["8.0"] == ["8.0.0"]
    assert list(data) == ["7.4", "7.6", "7.8", "8.0"]


def test_extract_doc_versions_from_branch_page():
    html = b"""
    <html><body>
      <a href="/product/fortigate/7.6">FortiOS 7.6</a>
      <a href="/document/fortigate/7.6.6/cli-reference">CLI 7.6.6</a>
      <a href="/document/fortigate/7.6.7/cli-reference">CLI 7.6.7</a>
      <a href="/document/fortigate/7.6.7/fortios-log-message-reference">LMR 7.6.7</a>
      <a href="/document/fortigate/7.6.6/fortios-log-message-reference">LMR 7.6.6</a>
      <a href="/document/fortigate/7.6.0/administration-guide">not tracked</a>
    </body></html>
    """
    cli, lmr = extract_doc_versions(html, "7.6")
    assert cli == {"7.6.6", "7.6.7"}
    assert lmr == {"7.6.6", "7.6.7"}


def test_extract_doc_versions_fails_loudly_on_missing_docs():
    html = b"<html><body><p>layout changed</p></body></html>"
    try:
        extract_doc_versions(html, "7.6")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "7.6" in str(exc)
