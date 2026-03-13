"""Master orchestrator: fetches description or comments and generates a CUE sheet."""

import argparse
import sys
from pathlib import Path

from ytcue.core.youtube import fetch_video_info
from ytcue.core.metadata import get_audio_search_query, get_audio_title, write_grouping_tag
from ytcue.core.parser import parse_lines
from ytcue.core.comments import find_tracklist_comment
from ytcue.cli.parser import process_input
from ytcue.core.cue import generate_cue_sheet


def main():
    parser = argparse.ArgumentParser(
        description="All-in-one tool: fetch a YouTube tracklist (description or comments) and generate a CUE sheet.",
        epilog="Wraps ytdesc, ytcomments, and ytcue into a single command.",
    )
    parser.add_argument(
        "source",
        help="YouTube URL, search query, or path to an audio file (will auto-search YouTube).",
    )
    parser.add_argument(
        "-a",
        "--audio",
        type=str,
        help="Name of the audio file to reference in the CUE sheet.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output CUE file path. Auto-derived from audio file if not specified.",
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
        "-y", "--yes", action="store_true", help="Overwrite output file without asking."
    )
    parser.add_argument(
        "--max-comments",
        type=int,
        default=100,
        help="Max comments to scan when falling back to comments. Default: 100.",
    )

    args = parser.parse_args()

    # Step 1: Determine the YouTube URL/query and output path
    source = args.source
    audio_name = args.audio
    output_path = args.output
    source_path = Path(source)
    video_title = None

    if source_path.exists() and source_path.is_file():
        # It's a local audio file — derive a search query from its tags
        print(f"Reading metadata from {source_path.name}...", file=sys.stderr)
        query = get_audio_search_query(source_path)
        print(f'Searching YouTube for: "{query}"...', file=sys.stderr)
        source = query
        if not audio_name:
            audio_name = source_path.name
        # Auto-derive output path from the audio file
        if not output_path:
            output_path = source_path.with_suffix(".cue")
        # Get audio title as fallback for mix title
        video_title = get_audio_title(source_path)

    # Step 2: Fetch description
    print("Fetching video info...", file=sys.stderr)
    info = fetch_video_info(source)
    lines = []

    if info:
        print(f"Video: {info['title']}", file=sys.stderr)
        if not video_title:
            video_title = info.get("title")
        desc = info.get("description", "")
        if desc:
            desc_lines = desc.splitlines()
            parsed = parse_lines(desc_lines)
            if parsed:
                lines = desc_lines
                print(
                    f"Found {len(parsed)} timestamps in description.", file=sys.stderr
                )

    # Step 3: Fallback to comments
    if not lines:
        print("No timestamps in description. Trying comments...", file=sys.stderr)
        url = info["url"] if info else source
        try:
            comment_info = fetch_video_info(url, get_comments=True)
            if comment_info:
                comments = comment_info.get("comments") or []
                if comments:
                    tracklist = find_tracklist_comment(comments, args.max_comments)
                    if tracklist:
                        lines = tracklist.splitlines()
                        print("Found tracklist in comments!", file=sys.stderr)
                    else:
                        print("No tracklist found in comments.", file=sys.stderr)
                else:
                    print("No comments were returned.", file=sys.stderr)
            else:
                print("Could not fetch comments.", file=sys.stderr)
        except Exception as e:
            print(f"Error during comment fetching: {e}", file=sys.stderr)

    if not lines:
        print(
            "Error: Could not find a tracklist in description or comments.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Step 4: Process and generate CUE
    mix = process_input(lines, args.format, args.extract_feat)

    if audio_name:
        mix.audio_file = Path(audio_name)

    # Use the video/audio title as the mix title if available
    if video_title:
        mix.title = video_title

    cue_content = generate_cue_sheet(
        mix, args.separator, include_labels=args.include_labels
    )

    # Step 5: Output
    if output_path:
        if output_path.exists() and not args.yes:
            answer = input(f"File {output_path} already exists. Overwrite? [y/N]: ")
            if answer.lower() not in ["y", "yes"]:
                print("Aborted.", file=sys.stderr)
                sys.exit(0)

        output_path.write_text(cue_content, encoding="utf-8-sig")
        print(f"Successfully wrote CUE sheet to {output_path}", file=sys.stderr)

        # Write grouping tag to the audio file metadata
        if source_path.exists() and source_path.is_file():
            if write_grouping_tag(source_path, mix.title or "YouTube Mix"):
                print(
                    f"Wrote grouping tag to {source_path.name}", file=sys.stderr
                )
    else:
        sys.stdout.write(cue_content)


if __name__ == "__main__":
    main()
