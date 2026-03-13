import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from ytcue.core.metadata import get_audio_search_query

@pytest.fixture
def mock_tag():
    with patch("ytcue.core.metadata.TinyTag.get") as mock:
        tag = MagicMock()
        mock.return_value = tag
        yield tag

def test_get_audio_search_query_with_artist_title(mock_tag):
    mock_tag.artist = "Artist Name"
    mock_tag.albumartist = None
    mock_tag.title = "Song Title"
    
    query = get_audio_search_query(Path("test.m4a"))
    assert query == "Artist Name - Song Title"

def test_get_audio_search_query_with_albumartist_title(mock_tag):
    mock_tag.artist = None
    mock_tag.albumartist = "Album Artist"
    mock_tag.title = "Song Title"
    
    query = get_audio_search_query(Path("test.m4a"))
    assert query == "Album Artist - Song Title"

def test_get_audio_search_query_with_various_artists(mock_tag):
    mock_tag.artist = "Various Artists"
    mock_tag.title = "Mix Title"
    
    query = get_audio_search_query(Path("test.m4a"))
    assert query == "Mix Title"

def test_get_audio_search_query_with_va(mock_tag):
    mock_tag.artist = "VA"
    mock_tag.title = "Mix Title"
    
    query = get_audio_search_query(Path("test.m4a"))
    assert query == "Mix Title"

def test_get_audio_search_query_with_title_only(mock_tag):
    mock_tag.artist = None
    mock_tag.albumartist = None
    mock_tag.title = "Song Title"
    
    query = get_audio_search_query(Path("test.m4a"))
    assert query == "Song Title"

def test_get_audio_search_query_fallback_to_filename():
    with patch("ytcue.core.metadata.TinyTag.get", side_effect=Exception("Failed to read")):
        query = get_audio_search_query(Path("path/to/my_cool_mix.m4a"))
        assert query == "my_cool_mix"

def test_get_audio_search_query_no_tags(mock_tag):
    mock_tag.artist = None
    mock_tag.albumartist = None
    mock_tag.title = None
    
    query = get_audio_search_query(Path("path/to/another_mix.mp3"))
    assert query == "another_mix"
