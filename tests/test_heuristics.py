from ytcue.core.heuristics import split_track_string, extract_feat_artists


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

    # Mixed suffix cleanup
    assert split_track_string("Franky Nuts (Mixed) - Waves", "artist-title") == (
        "Franky Nuts",
        "Waves (Mixed)",
    )
    assert split_track_string(
        "Gucci Mane [Mixed] - Both (feat. Drake) [Remix]", "artist-title"
    ) == (
        "Gucci Mane",
        "Both (feat. Drake) [Remix] [Mixed]",
    )
    assert split_track_string(
        "Waves by Franky Nuts (mixed)", primary_separator="by"
    ) == (
        "Franky Nuts",
        "Waves (mixed)",
    )

    # Remix suffix cleanup in artist
    assert split_track_string("M-Beat (Remix) - Incredible", "artist-title") == (
        "M-Beat",
        "Incredible (Remix)",
    )
    assert split_track_string(
        "Aaliyah [Remix] - Are You That Somebody", "artist-title"
    ) == (
        "Aaliyah",
        "Are You That Somebody [Remix]",
    )
    assert split_track_string("Laura Les Remix - Haunted", "artist-title") == (
        "Laura Les",
        "Haunted Remix",
    )

    # By split logic checks (smart heuristic fallback)
    assert split_track_string("Super Song by Cool Band") == (
        "Cool Band",
        "Super Song",
    )

    # Capitalized article is valid
    assert split_track_string("Hey Jude by The Beatles") == (
        "The Beatles",
        "Hey Jude",
    )

    # Pronoun avoidance
    assert split_track_string("Stand by Me") == ("", "Stand by Me")

    # Article avoidance (lowercase right side)
    assert split_track_string("Down by the river") == ("", "Down by the river")

    # Verb avoidance
    assert split_track_string("I went by the store") == ("", "I went by the store")

    # Enclosed in brackets
    assert split_track_string("Some Track (Remixed by DJ Foo)") == (
        "",
        "Some Track (Remixed by DJ Foo)",
    )

    # Primary separator forced to 'by'
    assert split_track_string(
        "Just a Track by Some Artist", primary_separator="by"
    ) == (
        "Some Artist",
        "Just a Track",
    )

    # Primary separator forced to 'by', ignoring smart heuristics
    assert split_track_string("Stand by Me", primary_separator="by") == (
        "Me",
        "Stand",
    )

    # Primary separator forced to 'by', but no "by" in track -> fallback to "-"
    assert split_track_string("Artist - Title", primary_separator="by") == (
        "Artist",
        "Title",
    )

    # Fallback checking format probabilities (keywords determining title)
    assert split_track_string("Title Remix - Artist", primary_separator="by") == (
        "Artist",
        "Title Remix",
    )

    # Long dash support
    assert split_track_string("Artist – Title", "artist-title") == ("Artist", "Title")
    assert split_track_string("Artist — Title", "artist-title") == ("Artist", "Title")


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

    # New patterns: featuring, with, w/, prod., bracket variants
    assert extract_feat_artists(
        "Track (featuring Guest)", "Artist", extract_feat=True
    ) == ("Artist; Guest", "Track")
    assert extract_feat_artists("Track [feat. Guest]", "Artist", extract_feat=True) == (
        "Artist; Guest",
        "Track",
    )
    assert extract_feat_artists("Track [ft Guest]", "Artist", extract_feat=True) == (
        "Artist; Guest",
        "Track",
    )
    assert extract_feat_artists(
        "Track (with Vocalist)", "Artist", extract_feat=True
    ) == ("Artist; Vocalist", "Track")
    assert extract_feat_artists("Track (w/ DJ Foo)", "Artist", extract_feat=True) == (
        "Artist; DJ Foo",
        "Track",
    )
    assert extract_feat_artists(
        "Track (prod. Producer)", "Artist", extract_feat=True
    ) == ("Artist; Producer", "Track")
