"""CLI entry point for ytaudio-query: prints a search query from audio file tags."""

import argparse
import sys
from pathlib import Path

from ytcue.core.metadata import get_audio_search_query


def main():
    parser = argparse.ArgumentParser(
        description="Extract a YouTube search query from audio file metadata tags."
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Path to the audio file.",
    )

    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    query = get_audio_search_query(args.file)
    print(query)


if __name__ == "__main__":
    main()
