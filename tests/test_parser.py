from ytcue.core.parser import parse_lines, parse_lines_with_labels


def test_parse_lines_basic():
    lines = [
        "00:00 Robyn, Yaeji  - Beach2k20 - Yaeji Remix",
        "03:20 Creme Anglaise - Hysterics",
        "1:02:05 Tribute - Moodymann",
        "18.14 Can’t hold it back - Jovonn",
    ]
    parsed = parse_lines(lines)

    assert len(parsed) == 4
    assert parsed[0] == ("00:00", "Robyn, Yaeji  - Beach2k20 - Yaeji Remix")
    assert parsed[1] == ("03:20", "Creme Anglaise - Hysterics")
    assert parsed[2] == ("01:02:05", "Tribute - Moodymann")
    assert parsed[3] == ("18:14", "Can’t hold it back - Jovonn")


def test_parse_lines_with_brackets():
    lines = ["[00:00] Track 1", "[01:30:45] Track 2"]
    parsed = parse_lines(lines)
    assert len(parsed) == 2
    assert parsed[0] == ("00:00", "Track 1")
    assert parsed[1] == ("01:30:45", "Track 2")


def test_parse_lines_separators():
    """Test that various separators between timestamp and track text are handled."""
    lines = [
        "00:00 | ASC - Vapour Trail",
        "06:48 - Eusebeia - More Than Lucky",
        "1:00:14 – Pixl - Empath",
        "1:02:33 — Papa Shanti - Universal",
        "01:23:45 : Some Track",
    ]
    parsed = parse_lines(lines)

    assert len(parsed) == 5
    assert parsed[0] == ("00:00", "ASC - Vapour Trail")
    assert parsed[1] == ("06:48", "Eusebeia - More Than Lucky")
    assert parsed[2] == ("01:00:14", "Pixl - Empath")
    assert parsed[3] == ("01:02:33", "Papa Shanti - Universal")
    assert parsed[4] == ("01:23:45", "Some Track")


def test_parse_lines_with_labels_extraction():
    """Test that labels on the line following a track are extracted correctly."""
    lines = [
        "00:00 | ASC - Vapour Trail",
        "Over/Shadow",
        "",
        "06:48 | Eusebeia - More Than Lucky",
        "Modern Conveniences",
        "",
        "1:00:14 | Pixl - Empath",
        "",
        "1:02:33 | Papa Shanti - Universal",
        "Döner Beat Records",
    ]
    parsed = parse_lines_with_labels(lines)

    assert len(parsed) == 4
    assert parsed[0] == ("00:00", "ASC - Vapour Trail", "Over/Shadow")
    assert parsed[1] == ("06:48", "Eusebeia - More Than Lucky", "Modern Conveniences")
    assert parsed[2] == ("01:00:14", "Pixl - Empath", None)  # No label line
    assert parsed[3] == ("01:02:33", "Papa Shanti - Universal", "Döner Beat Records")
