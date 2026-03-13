"""Fully autonomous mode: recursively processes directories, generating CUE sheets without user interaction."""

import argparse
import sys
from pathlib import Path

from ytcue.core.youtube import fetch_video_info
from ytcue.core.metadata import (
    get_audio_search_query,
    get_audio_title,
    get_missing_cue_files_recursive,
    write_grouping_tag,
)
from ytcue.core.parser import parse_lines
from ytcue.core.comments import find_tracklist_comment
from ytcue.cli.parser import process_input
from ytcue.core.cue import generate_cue_sheet


def process_single_file(
    audio_file: Path,
    format_guess: str = "auto",
    extract_feat: bool = False,
    separator: str = "; ",
    include_labels: bool = False,
    max_comments: int = 100,
    overwrite: bool = False,
) -> bool:
    """
    Autonomously processes a single audio file: search YouTube, fetch tracklist, generate CUE.
    Returns True on success, False on failure.
    """
    cue_path = audio_file.with_suffix(".cue")

    if cue_path.exists() and not overwrite:
        print(f"  Skipping (CUE exists): {audio_file.name}", file=sys.stderr)
        return False

    print(f"  Processing: {audio_file.name}", file=sys.stderr)

    # Step 1: Search YouTube
    query = get_audio_search_query(audio_file)
    print(f'    Searching: "{query}"...', file=sys.stderr)
    info = fetch_video_info(query)

    if not info:
        print("    ✗ Could not find video.", file=sys.stderr)
        return False

    print(f"    Found: {info['title']}", file=sys.stderr)

    # Step 2: Try description
    lines = []
    desc = info.get("description", "")
    if desc:
        desc_lines = desc.splitlines()
        parsed = parse_lines(desc_lines)
        if parsed:
            lines = desc_lines
            print(f"    ✓ {len(parsed)} timestamps in description.", file=sys.stderr)

    # Step 3: Try comments
    if not lines:
        print("    No timestamps in description. Trying comments...", file=sys.stderr)
        try:
            comment_info = fetch_video_info(info["url"], get_comments=True)
            if comment_info:
                comments = comment_info.get("comments") or []
                if comments:
                    tracklist = find_tracklist_comment(comments, max_comments)
                    if tracklist:
                        lines = tracklist.splitlines()
                        print("    ✓ Found tracklist in comments.", file=sys.stderr)
        except Exception:
            pass

    if not lines:
        print("    ✗ No tracklist found.", file=sys.stderr)
        return False

    # Step 4: Generate CUE
    try:
        mix = process_input(lines, format_guess, extract_feat)
        mix.audio_file = audio_file
        mix.title = get_audio_title(audio_file) or info.get("title")

        cue_content = generate_cue_sheet(mix, separator, include_labels=include_labels)
        cue_path.write_text(cue_content, encoding="utf-8-sig")
        write_grouping_tag(audio_file, mix.title or "YouTube Mix")
        print(f"    ✓ Created {cue_path.name}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"    ✗ Error generating CUE: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Fully autonomous: recursively scan a directory and generate CUE sheets for all audio files.",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Directory to scan recursively for audio files.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["auto", "artist-title", "title-artist"],
        default="auto",
        help="Heuristic format for the tracklist. Default is 'auto'.",
    )
    parser.add_argument(
        "-s",
        "--separator",
        type=str,
        default="; ",
        help="Artist separator for the CUE PERFORMER field. Default: '; '.",
    )
    parser.add_argument(
        "--extract-feat",
        action="store_true",
        help="Extract (feat.) artists into the performer field.",
    )
    parser.add_argument(
        "--include-labels",
        action="store_true",
        help="Include record label info as REM LABEL comments.",
    )
    parser.add_argument(
        "--max-comments",
        type=int,
        default=100,
        help="Max comments to scan per video. Default: 100.",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Overwrite existing CUE files.",
    )

    args = parser.parse_args()

    if not args.path.is_dir():
        print(f"Error: {args.path} is not a directory.", file=sys.stderr)
        sys.exit(1)

    audio_files = get_missing_cue_files_recursive(args.path)

    if not audio_files:
        print(f"No audio files missing CUE sheets found in {args.path}.")
        sys.exit(0)

    print(f"Found {len(audio_files)} audio file(s) missing CUE sheets.\n")

    success = 0
    fail = 0

    for audio_file in audio_files:
        result = process_single_file(
            audio_file,
            format_guess=args.format,
            extract_feat=args.extract_feat,
            separator=args.separator,
            include_labels=args.include_labels,
            max_comments=args.max_comments,
            overwrite=args.yes,
        )
        if result:
            success += 1
        else:
            fail += 1

    print(f"\nDone. {success} succeeded, {fail} failed/skipped.")


if __name__ == "__main__":
    main()
