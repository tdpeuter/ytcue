"""Standalone tool to fetch a YouTube video description."""

import argparse
import sys

from ytcue.core.youtube import fetch_video_info


def main() -> None:
    """CLI entry point for ytdesc: fetches and prints a YouTube description to stdout."""
    parser = argparse.ArgumentParser(
        description="Fetch the description of a YouTube video and print it to stdout."
    )
    parser.add_argument("url", help="YouTube video URL or search query.")

    args = parser.parse_args()

    info = fetch_video_info(args.url)

    if not info:
        print("Error: Could not fetch video info.", file=sys.stderr)
        sys.exit(1)

    description = info.get("description", "")
    if not description:
        print(
            f"Warning: No description found for '{info.get('title', 'Unknown')}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Print title to stderr for context, description to stdout for piping
    print(f"Video: {info['title']}", file=sys.stderr)
    print(description)


if __name__ == "__main__":
    main()
