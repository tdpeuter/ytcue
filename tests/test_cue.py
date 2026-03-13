"""Tests for CUE sheet generation."""

from pathlib import Path
from ytcue.core.models import Mix, Track
from ytcue.core.cue import generate_cue_sheet, _get_cue_file_type, _escape_cue_string


def test_cue_file_type_mapping():
    """Correct FILE type for various audio formats."""
    assert _get_cue_file_type(Path("mix.flac")) == "WAVE"
    assert _get_cue_file_type(Path("mix.wav")) == "WAVE"
    assert _get_cue_file_type(Path("mix.aiff")) == "WAVE"
    assert _get_cue_file_type(Path("mix.mp3")) == "MP3"
    assert _get_cue_file_type(Path("mix.opus")) == "WAVE"
    assert _get_cue_file_type(Path("mix.m4a")) == "WAVE"
    assert _get_cue_file_type(None) == "WAVE"


def test_escape_cue_string():
    """Double quotes in metadata are replaced with single quotes."""
    assert _escape_cue_string('Track "Remix"') == "Track 'Remix'"
    assert _escape_cue_string("No quotes") == "No quotes"


def test_generate_cue_basic():
    """Basic CUE sheet generation with correct structure."""
    mix = Mix(
        tracks=[
            Track(start_time_str="0:00", artist="Artist A", title="Track One"),
            Track(start_time_str="3:30", artist="Artist B", title="Track Two"),
        ],
        audio_file=Path("mix.flac"),
        title="My Mix",
    )

    cue = generate_cue_sheet(mix)

    # Disc-level headers
    assert 'TITLE "My Mix"' in cue
    assert 'PERFORMER "Various Artists"' in cue
    assert 'FILE "mix.flac" WAVE' in cue

    # No hardcoded DATE
    assert "REM DATE 2024" not in cue

    # Track structure
    assert "TRACK 01 AUDIO" in cue
    assert '    TITLE "Track One"' in cue
    assert '    PERFORMER "Artist A"' in cue
    assert "    INDEX 01 00:00:00" in cue

    assert "TRACK 02 AUDIO" in cue
    assert '    TITLE "Track Two"' in cue
    assert "    INDEX 01 03:30:00" in cue


def test_generate_cue_mp3():
    """MP3 files get FILE type MP3."""
    mix = Mix(
        tracks=[Track(start_time_str="0:00", artist="A", title="B")],
        audio_file=Path("mix.mp3"),
    )
    cue = generate_cue_sheet(mix)
    assert 'FILE "mix.mp3" MP3' in cue


def test_generate_cue_quotes_escaped():
    """Quotes in titles and performers are escaped."""
    mix = Mix(
        tracks=[
            Track(start_time_str="0:00", artist='DJ "Fresh"', title='Track "One"'),
        ],
        audio_file=Path("mix.flac"),
    )
    cue = generate_cue_sheet(mix)
    assert "TITLE \"Track 'One'\"" in cue
    assert "PERFORMER \"DJ 'Fresh'\"" in cue


def test_generate_cue_long_timestamp():
    """Timestamps exceeding 60 minutes are correctly converted."""
    mix = Mix(
        tracks=[Track(start_time_str="1:05:30", artist="A", title="B")],
        audio_file=Path("mix.flac"),
    )
    cue = generate_cue_sheet(mix)
    assert "INDEX 01 65:30:00" in cue


def test_generate_cue_no_performer():
    """Tracks without an artist omit the PERFORMER line (inherits disc-level)."""
    mix = Mix(
        tracks=[Track(start_time_str="0:00", artist="", title="Intro")],
        audio_file=Path("mix.flac"),
    )
    cue = generate_cue_sheet(mix)
    lines = cue.splitlines()
    track_lines = [
        line
        for line in lines
        if line.strip().startswith("PERFORMER") and "Various" not in line
    ]
    assert len(track_lines) == 0
