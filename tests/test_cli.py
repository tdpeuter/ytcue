from ytcue.cli.parser import process_input


def test_process_input_mixed_separator():
    """
    Test that process_input correctly delegates fallback splits when the
    primary separator 'by' is evaluated for a mixed tracklist containing mostly 'by'
    but some tracks formatted with '-' and lacking 'by'.
    """
    raw_lines = [
        "00:00 The Test by The Artist",
        "03:00 Second Track - Cool Guy",
        "05:30 Something in brackets (feat. Dude)",  # Should resolve to Title-Artist default if no hyphen/by
        "07:15 Another Track by Another Band",
    ]

    mix = process_input(raw_lines, format_guess="auto", extract_feat=True)

    assert len(mix.tracks) == 4

    # 1. Primary "by" track
    assert mix.tracks[0].artist == "The Artist"
    assert mix.tracks[0].title == "The Test"

    # 2. Track lacking "by" but having "-", falling back to hyphen logic
    # (probabilistic check places left-side "Second Track" as Artist because there are no Remix/Dub keywords on the right)
    assert mix.tracks[1].artist == "Second Track"
    assert mix.tracks[1].title == "Cool Guy"

    # 3. Track lacking any clear separator, falls back gracefully (Artist blank)
    assert mix.tracks[2].artist == "; Dude"  # Feat extracted
    assert mix.tracks[2].title == "Something in brackets"

    # 4. Another "by" track
    assert mix.tracks[3].artist == "Another Band"
    assert mix.tracks[3].title == "Another Track"


def test_process_input_hyphen_dominant():
    """
    Test that process_input does NOT falsely set primary_separator='by'
    if the ratio isn't met, falling back optimally to line-by-line checks.
    """
    raw_lines = [
        "00:00 Title by Artist",
        "03:00 Title A - Artist A",
        "05:30 Title B - Artist B",
        "07:15 Title C - Artist C",
    ]

    mix = process_input(raw_lines, format_guess="auto", extract_feat=False)

    # Track 0 does have "by" but it shouldn't dominate the whole list.
    # The smart logic should still extract it correctly on a line-by-line basis.
    assert mix.tracks[0].artist == "Artist"
    assert mix.tracks[0].title == "Title"

    # Track 1 uses hyphen (Probabilistic format defaults to Artist on left lacking keywords)
    assert mix.tracks[1].artist == "Title A"
    assert mix.tracks[1].title == "Artist A"


def test_dot_stripping_heuristic():
    """
    Test that trailing dots are stripped if most tracks have them.
    """
    raw_lines = [
        "00:00 Artist 1 - Title 1.",
        "03:00 Artist 2 - Title 2.",
        "06:00 Artist 3 - Title 3",  # No dot here
        "09:00 Artist 4 - Title 4.",
    ]
    # 3 out of 4 (75%) have dots. The threshold is 80%. Let's check 80%.
    # If I add another one:
    raw_lines.append("12:00 Artist 5 - Title 5.")
    # 4 out of 5 is 80%. 0.8 is the threshold. Let's make it 5 out of 6.
    raw_lines.append("15:00 Artist 6 - Title 6.")
    # 5 out of 6 is ~83%.

    mix = process_input(raw_lines, format_guess="artist-title", extract_feat=False)

    assert mix.tracks[0].title == "Title 1"
    assert mix.tracks[1].title == "Title 2"
    assert mix.tracks[2].title == "Title 3"
    assert mix.tracks[3].title == "Title 4"
    assert mix.tracks[4].title == "Title 5"
    assert mix.tracks[5].title == "Title 6"
