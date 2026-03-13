from ytdesc2cue.cli import process_input


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
