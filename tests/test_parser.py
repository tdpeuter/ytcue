from ytdesc2cue.parser import parse_lines


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
