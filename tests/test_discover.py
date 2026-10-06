from discover import parse_toc_commands

# Mirrors the live TOC DOM: each anchor sits in a <span class="toc__label"> next
# to either a <span class="toc__leaf"> (command page) or a
# <button class="toc__toggle"> (expandable section node).
TOC_HTML = b"""
<html><body>
  <span class="toc__label"><span class="toc__leaf"></span><a class="toc__link" href="/document/fortigate/7.4.0/cli-reference/84566/fortios-cli-reference">Fortios CLI</a></span>
  <span class="toc__label"><span class="toc__leaf"></span><a class="toc__link" href="/document/fortigate/7.4.0/cli-reference/708841/cli-configuration-commands">Configuration</a></span>
  <span class="toc__label"><button class="toc__toggle"></button><a class="toc__link" href="/document/fortigate/7.4.0/cli-reference/848/alertemail">alertemail</a></span>
  <span class="toc__label"><span class="toc__leaf"></span><a class="toc__link" href="/document/fortigate/7.4.0/cli-reference/510620/config-alertemail-setting">config alertemail setting</a></span>
  <span class="toc__label"><span class="toc__leaf"></span><a class="toc" href="/document/fortigate/7.4.0/cli-reference/489620/config-antivirus-exempt-list">old-style anchor class</a></span>
  <span class="toc__label"><span class="toc__leaf"></span><a class="toc__link" href="/document/fortigate/7.4.0/cli-reference/489620/config-antivirus-exempt-list">duplicate slug</a></span>
  <span class="toc__label"><button class="toc__toggle"></button><a class="toc__link" href="/document/fortigate/8.0.0/cli-reference/168275279/config-system">8.0-style section</a></span>
  <span class="toc__label"><span class="toc__leaf"></span><a class="toc__link" href="/document/fortigate/8.0.0/cli-reference/999/config-system-global">config system global</a></span>
  <span class="toc__label"><span class="toc__leaf"></span><a class="toc__link" href="/document/fortigate/7.4.0/cli-reference/101/cli-diagnose-commands">Diagnose</a></span>
  <span class="toc__label"><span class="toc__leaf"></span><a class="toc__link" href="/document/fortigate/7.4.0/cli-reference/555/config-log-remote-syslog">must not appear</a></span>
  <span class="toc__label"><span class="toc__leaf"></span><a class="protocol" href="/document/fortigate/7.4.0/cli-reference/777/config-should-not-match">substring trap</a></span>
  <a href="/document/fortigate/7.4.0/cli-reference/888/config-no-class-attr">classless anchor</a>
</body></html>
"""


def test_parse_toc_commands_collects_leaf_commands():
    commands = parse_toc_commands(TOC_HTML)
    slugs = [slug for _, slug, _ in commands]
    assert slugs == [
        "config-alertemail-setting",
        "config-antivirus-exempt-list",
        "config-system-global",
    ]


def test_parse_toc_commands_sections():
    commands = parse_toc_commands(TOC_HTML)
    assert commands[0] == (
        "alertemail",
        "config-alertemail-setting",
        "https://docs.fortinet.com/document/fortigate/7.4.0/cli-reference/510620/config-alertemail-setting",
    )
    assert commands[1][0] == "alertemail"
    # 8.0-style expandable sections are named config-*; the prefix is stripped
    # so output paths match the 7.x layout.
    assert commands[2][0] == "system"


def test_parse_toc_commands_stops_at_terminator():
    assert all(slug != "config-log-remote-syslog" for _, slug, _ in parse_toc_commands(TOC_HTML))


def test_parse_toc_commands_ignores_pre_config_section():
    assert all(slug != "fortios-cli-reference" for _, slug, _ in parse_toc_commands(TOC_HTML))


def test_parse_toc_commands_ignores_non_toc_anchors():
    # "protocol" contains the substring "toc" but is not a TOC class, and
    # anchors without a class attribute are not TOC links either.
    assert all(slug != "config-should-not-match" for _, slug, _ in parse_toc_commands(TOC_HTML))
    assert all(slug != "config-no-class-attr" for _, slug, _ in parse_toc_commands(TOC_HTML))


def test_parse_toc_commands_empty_on_restructure():
    assert parse_toc_commands(b"<html><body><p>layout changed</p></body></html>") == []
