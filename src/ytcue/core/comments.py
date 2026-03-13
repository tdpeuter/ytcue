"""Logic to find tracklists in YouTube video comments."""

import sys
from ytcue.core.parser import TIMESTAMP_PATTERN


def find_tracklist_comment(comments: list, max_comments: int = 100) -> str:
    """
    Scans a list of comment dicts and returns the text of the one
    that looks most like a tracklist (most timestamp matches).
    Returns empty string if no good candidate is found.
    """
    best_comment = ""
    max_matches = 0

    total = len(comments[:max_comments])
    if total > 0:
        sys.stderr.write(f"Scanning comments... 0/{total}")
        sys.stderr.flush()

    for i, comment in enumerate(comments[:max_comments], 1):
        sys.stderr.write(f"\rScanning comments... {i}/{total}")
        sys.stderr.flush()

        if not isinstance(comment, dict):
            continue
        text = comment.get("text") or ""
        if not text:
            continue
        lines = text.splitlines()

        match_count = sum(1 for line in lines if TIMESTAMP_PATTERN.search(line.strip()))

        if match_count > max_matches:
            max_matches = match_count
            best_comment = text

    sys.stderr.write("\n")

    if max_matches < 3:
        if best_comment:
            print(
                f"Warning: Best candidate has only {max_matches} timestamps.",
                file=sys.stderr,
            )
        return ""

    return best_comment
