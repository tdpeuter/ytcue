"""Comprehensive tests for the comments and youtube modules, including negative edge cases."""

from unittest.mock import patch
from ytcue.core.comments import find_tracklist_comment
from ytcue.core.youtube import fetch_video_info, _filter_warnings


# ── find_tracklist_comment tests ──────────────────────────────────────


def test_find_tracklist_comment_selection():
    """Pick the comment with the most timestamps."""
    mock_comments = [
        {"text": "Great mix!"},
        {"text": "Tracklist:\n00:00 Song A\n03:20 Song B\n06:40 Song C"},
        {"text": "00:00 Intro\n05:00 Outro"},
    ]

    result = find_tracklist_comment(mock_comments)
    assert "Song A" in result
    assert "Song B" in result
    assert "Song C" in result
    assert "Intro" not in result


def test_find_tracklist_comment_not_found():
    """Not enough timestamps to be confident."""
    mock_comments = [
        {"text": "00:00 Intro"},
    ]
    result = find_tracklist_comment(mock_comments)
    assert result == ""


def test_find_tracklist_comment_empty():
    """No comments at all."""
    result = find_tracklist_comment([])
    assert result == ""


def test_find_tracklist_comment_none_text():
    """Comment with missing 'text' key."""
    mock_comments = [
        {},
        {"text": None},
        {"text": ""},
        {"text": "00:00 A\n03:00 B\n06:00 C"},
    ]
    result = find_tracklist_comment(mock_comments)
    assert "A" in result


def test_find_tracklist_comment_max_limits():
    """Only scans up to max_comments."""
    # First comment has a tracklist, but max_comments=0 means we skip it
    mock_comments = [
        {"text": "00:00 A\n03:00 B\n06:00 C"},
    ]
    result = find_tracklist_comment(mock_comments, max_comments=0)
    assert result == ""


def test_find_tracklist_comment_non_dict():
    """Gracefully handle malformed comment entries."""
    mock_comments = [
        None,
        "just a string",
        42,
        {"text": "00:00 A\n01:00 B\n02:00 C"},
    ]
    # None and non-dict entries should not crash
    result = find_tracklist_comment(mock_comments)
    assert "A" in result


# ── _filter_warnings tests ───────────────────────────────────────────


def test_filter_warnings_suppresses_js_runtime(capsys):
    """JS runtime warning should be suppressed."""
    _filter_warnings("No supported JavaScript runtime could be found blah blah")
    captured = capsys.readouterr()
    assert captured.err == ""


def test_filter_warnings_suppresses_incomplete_data(capsys):
    """Incomplete data warning should be suppressed."""
    _filter_warnings("[youtube] Incomplete data received. Retrying (1/3)...")
    captured = capsys.readouterr()
    assert captured.err == ""


def test_filter_warnings_passes_unknown(capsys):
    """Unknown warnings should be printed."""
    _filter_warnings("Something unexpected happened")
    captured = capsys.readouterr()
    assert "Something unexpected" in captured.err


# ── fetch_video_info tests (mocked) ─────────────────────────────────


def test_fetch_video_info_returns_none_on_exception():
    """yt-dlp throwing should return None, not crash."""
    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.side_effect = (
            Exception("network error")
        )
        result = fetch_video_info("http://example.com")
        assert result is None


def test_fetch_video_info_returns_none_on_no_info():
    """yt-dlp returning None info should be handled."""
    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = None
        result = fetch_video_info("http://example.com")
        assert result is None


def test_fetch_video_info_empty_search_results():
    """Search with no results returns None."""
    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = {
            "entries": []
        }
        result = fetch_video_info("some search query")
        assert result is None


def test_fetch_video_info_comments_none_value():
    """Video exists but comments field is None."""
    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = {
            "title": "Test",
            "webpage_url": "http://example.com",
            "description": "Hello",
            "comments": None,
        }
        result = fetch_video_info("http://example.com", get_comments=True)
        assert result is not None
        assert result["comments"] == []


def test_fetch_video_info_no_description():
    """Video with no description returns empty string, not None."""
    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = {
            "title": "Test",
            "webpage_url": "http://example.com",
            "description": None,
        }
        result = fetch_video_info("http://example.com")
        assert result is not None
        assert result["description"] == ""


def test_fetch_video_info_keyboard_interrupt():
    """Ctrl+C during fetch returns None gracefully."""
    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.side_effect = (
            KeyboardInterrupt()
        )
        result = fetch_video_info("http://example.com")
        assert result is None
