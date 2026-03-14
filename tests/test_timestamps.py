from ytcue.core.parser import parse_lines


def test_timestamp_parsing_with_track_numbers():
    """
    Test that the parser correctly handles track numbers at the beginning of lines
    and doesn't mistake them for hours.
    """
    raw_lines = [
        "1. 00:00 Track 1",
        "2. 03:00 Track 2",
        "65. 05:00 Track 65",
        "01 - 10:00 Track with dash prefix",
    ]

    parsed = parse_lines(raw_lines)

    assert len(parsed) == 4

    # Check that hours were NOT extracted from the track numbers
    assert parsed[0][0] == "00:00"
    assert parsed[1][0] == "03:00"
    assert parsed[2][0] == "05:00"
    assert parsed[3][0] == "10:00"

    assert parsed[0][1] == "Track 1"
    assert parsed[1][1] == "Track 2"
    assert parsed[2][1] == "Track 65"
    assert parsed[3][1] == "Track with dash prefix"


def test_timestamp_parsing_with_real_hours():
    """
    Test that the parser still correctly identifies real hours.
    """
    raw_lines = [
        "00:00:01 Early Track",
        "01:02:03 Middle Track",
        "12:34:56 Late Track",
    ]

    parsed = parse_lines(raw_lines)

    assert len(parsed) == 3
    assert parsed[0][0] == "00:00:01"
    assert parsed[1][0] == "01:02:03"
    assert parsed[2][0] == "12:34:56"


def test_timestamp_parsing_mixed_formats():
    """
    Test a mix of prefixed and non-prefixed timestamps.
    """
    raw_lines = [
        "00:00 Simple",
        "1. 02:00 Prefixed",
        "01:00:00 Hour-long",
    ]

    parsed = parse_lines(raw_lines)

    assert len(parsed) == 3
    assert parsed[0][0] == "00:00"
    assert parsed[1][0] == "02:00"
    assert parsed[2][0] == "01:00:00"
