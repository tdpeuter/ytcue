"""Standalone tool to find tracklists in YouTube video comments."""

import argparse
import sys

from ytcue.core.comments import find_tracklist_comment
from ytcue.core.youtube import fetch_video_info


def main() -> None:
    """CLI entry point for ytcomments: finds tracklists in YouTube comments."""
    parser = argparse.ArgumentParser(
        description="Search for tracklists in YouTube comments using timestamp heuristics."
    )
    parser.add_argument("url", help="YouTube video URL.")
    parser.add_argument(
        "--max",
        type=int,
        default=100,
        help="Maximum number of comments to scan. Default: 100.",
    )

    args = parser.parse_args()

    print(f"Fetching comments for {args.url}...", file=sys.stderr)
    info = fetch_video_info(args.url, get_comments=True)

    if not info:
        print("Error: Could not fetch video info.", file=sys.stderr)
        sys.exit(1)

    comments = info.get("comments", [])
    if not comments:
        print("No comments found.", file=sys.stderr)
        sys.exit(1)

    tracklist = find_tracklist_comment(comments, args.max)

    if tracklist:
        print(tracklist)
    else:
        print("Could not find a clear tracklist in the comments.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
