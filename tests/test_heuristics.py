from ytdesc2cue.heuristics import split_track_string, extract_feat_artists


def test_split_artist_title():
    # Standard format
    assert split_track_string("Creme Anglaise - Hysterics", "artist-title") == (
        "Creme Anglaise",
        "Hysterics",
    )

    # Auto fallback (assumes artist - title default)
    assert split_track_string("Robyn, Yaeji  - Beach2k20 - Yaeji Remix", "auto") == (
        "Robyn, Yaeji",
        "Beach2k20 - Yaeji Remix",
    )

    # Auto heuristic (detects single quote as title)
    assert split_track_string("Can’t hold it back - Jovonn", "auto") == (
        "Jovonn",
        "Can’t hold it back",
    )

    # Auto heuristic (remix in part 1)
    # E.g. "Some Remix - Producer"
    assert split_track_string("Cool Edit - DJ Test", "auto") == ("DJ Test", "Cool Edit")

    # Default without dashes
    assert split_track_string("Just A Song") == ("", "Just A Song")


def test_extract_feat_artists():
    assert extract_feat_artists(
        "My Song (feat. Jane Doe)", "John Doe", extract_feat=True
    ) == ("John Doe; Jane Doe", "My Song")
    assert extract_feat_artists("Track (ft. Singer)", "Artist", extract_feat=True) == (
        "Artist; Singer",
        "Track",
    )
    assert extract_feat_artists("Title ft Rapper", "DJ", extract_feat=True) == (
        "DJ; Rapper",
        "Title",
    )
    assert extract_feat_artists(
        "Already here (feat. Name)", "Artist; Name", extract_feat=True
    ) == ("Artist; Name", "Already here")  # deduplication check
    assert extract_feat_artists("Just a song", "Singer", extract_feat=True) == (
        "Singer",
        "Just a song",
    )
