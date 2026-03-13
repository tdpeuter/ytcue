"""Shared YouTube fetching utilities using yt-dlp."""

import signal
import sys
from typing import Any, Optional

import yt_dlp

# Warnings that are noisy but not actionable by the user
_SUPPRESSED_WARNINGS = [
    "No supported JavaScript runtime could be found",
    "Incomplete data received",
]

# Default timeout for comment fetching (seconds)
COMMENT_FETCH_TIMEOUT = 30


class _CommentFetchTimeoutError(Exception):
    """Raised when comment fetching exceeds the timeout."""

    pass


def _filter_warnings(msg: str) -> None:
    """Suppress known benign yt-dlp warnings."""
    if any(suppressed in msg for suppressed in _SUPPRESSED_WARNINGS):
        return
    print(f"Warning: {msg}", file=sys.stderr)


class QuietLogger:
    """A logger that suppresses debug/info output and filters known warnings."""

    def debug(self, msg: str) -> None:
        pass

    def info(self, msg: str) -> None:
        pass

    def warning(self, msg: str) -> None:
        _filter_warnings(msg)

    def error(self, msg: str) -> None:
        print(msg, file=sys.stderr)


def _timeout_handler(signum: int, frame: Any) -> None:
    raise _CommentFetchTimeoutError()


def fetch_video_info(
    query_or_url: str,
    get_comments: bool = False,
    max_comments: int = 100,
    timeout: int = COMMENT_FETCH_TIMEOUT,
) -> Optional[dict[str, Any]]:
    """
    Fetches video info from YouTube. Supports both URLs and search queries.

    Returns a dict with keys: title, url, description, comments (if requested).
    Returns None on failure.

    When get_comments is True, fetches only top-sorted comments up to max_comments
    to avoid hanging on popular videos with thousands of comments.
    A timeout (default 30s) is applied to comment fetching to prevent indefinite hangs.
    """
    if not query_or_url.startswith("http"):
        query_or_url = f"ytsearch1:{query_or_url}"

    ydl_opts = {
        "quiet": True,
        "extract_flat": False,
        "nocheckcertificate": True,
        "logger": QuietLogger(),
    }

    if get_comments:
        ydl_opts["getcomments"] = True
        # Limit comment fetching to prevent hanging on popular videos.
        # Format: max_comments,max_parents,max_replies_per_thread
        ydl_opts["extractor_args"] = {
            "youtube": {
                "max_comments": [f"{max_comments},{max_comments},0,0"],
                "comment_sort": ["top"],
            }
        }

    # Set up a timeout for comment fetching (Unix-only via SIGALRM)
    use_timeout = get_comments and timeout > 0 and hasattr(signal, "SIGALRM")

    try:
        if use_timeout:
            old_handler = signal.signal(signal.SIGALRM, _timeout_handler)  # type: ignore
            signal.alarm(timeout)  # type: ignore

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query_or_url, download=False)

            if info is None:
                print("Warning: yt-dlp returned no data.", file=sys.stderr)
                return None

            if "entries" in info:
                entries = info.get("entries", [])
                if not entries:
                    print("Warning: No search results found.", file=sys.stderr)
                    return None
                info = entries[0]
                if info is None:
                    return None

            comments = []
            if get_comments:
                raw_comments = info.get("comments")
                if raw_comments and isinstance(raw_comments, list):
                    comments = raw_comments

            return {
                "title": info.get("title", "Unknown Title"),
                "url": info.get("webpage_url", query_or_url),
                "description": info.get("description", "") or "",
                "comments": comments,
            }
    except _CommentFetchTimeoutError:
        print(
            f"Warning: Comment fetching timed out after {timeout}s. Skipping comments.",
            file=sys.stderr,
        )
        return None
    except KeyboardInterrupt:
        print("\nAborted by user.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error fetching YouTube data: {e}", file=sys.stderr)
        return None
    finally:
        if use_timeout:
            signal.alarm(0)  # type: ignore
            signal.signal(signal.SIGALRM, old_handler)  # type: ignore
