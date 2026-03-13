import argparse
import sys
from pathlib import Path

from ytdesc2cue.models import Mix, Track
from ytdesc2cue.parser import parse_lines
from ytdesc2cue.heuristics import split_track_string
from ytdesc2cue.cue import generate_cue_sheet


def process_input(lines: list, format_guess: str, extract_feat: bool) -> Mix:
    parsed = parse_lines(lines)
    tracks = []

    # Tracklist-level heuristic: evaluate whether to enforce a "by" split
    by_count = 0
    dash_count = 0
    for _, raw_text in parsed:
        if " by " in raw_text.lower():
            by_count += 1
        if " - " in raw_text:
            dash_count += 1

    primary_separator = None
    if parsed and by_count > len(parsed) * 0.6 and dash_count < len(parsed) * 0.4:
        primary_separator = "by"

    for timestamp, raw_text in parsed:
        artist, title = split_track_string(raw_text, format_guess, extract_feat, primary_separator)
        tracks.append(Track(start_time_str=timestamp, artist=artist, title=title))

    return Mix(tracks=tracks)


def main():
    parser = argparse.ArgumentParser(
        description="Convert YouTube descriptions with timestamps into MusicBee-compatible CUE sheets.",
        epilog="Use DOTADIW workflow: yt-dlp to download the audio and description, then pipe the description into ytdesc2cue.",
    )

    parser.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType("r", encoding="utf-8"),
        default=sys.stdin,
        help="Input text file containing the YouTube description. If omitted, reads from stdin.",
    )

    parser.add_argument(
        "-a",
        "--audio",
        type=str,
        help="Name of the audio file to reference in the CUE sheet (e.g. 'mix.flac').",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output CUE file path. Prints to stdout if omitted.",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["auto", "artist-title", "title-artist"],
        default="auto",
        help="Heuristic format for the tracklist. Default is 'auto'. Use 'artist-title' or 'title-artist' to force.",
    )

    parser.add_argument(
        "-s",
        "--separator",
        type=str,
        default="; ",
        help="Artist separator string for the CUE PERFORMER field. Default is '; ' which works well for MusicBee.",
    )

    parser.add_argument(
        "--extract-feat",
        action="store_true",
        help="Enable attempting to extract (feat.) artists into the performer field.",
    )

    parser.add_argument(
        "-y", "--yes", action="store_true", help="Overwrite output file without asking."
    )

    args = parser.parse_args()

    # Read lines
    if args.input.isatty():
        # Running interactively without piping
        parser.print_help()
        sys.exit(1)

    try:
        lines = args.input.readlines()
    except UnicodeDecodeError:
        print(
            "Error: Could not decode input. Ensure the file is UTF-8 encoded.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not lines:
        print("No input provided.", file=sys.stderr)
        sys.exit(1)

    # Process models
    mix = process_input(lines, args.format, args.extract_feat)

    if args.audio:
        mix.audio_file = Path(args.audio)

    # Generate CUE
    cue_content = generate_cue_sheet(mix, args.separator)

    # Output handling
    if args.output:
        if args.output.exists() and not args.yes:
            answer = input(f"File {args.output} already exists. Overwrite? [y/N]: ")
            if answer.lower() not in ["y", "yes"]:
                print("Aborted.", file=sys.stderr)
                sys.exit(0)

        args.output.write_text(cue_content, encoding="utf-8")
        print(f"Successfully wrote CUE sheet to {args.output}", file=sys.stderr)
    else:
        # Print to stdout
        sys.stdout.write(cue_content)


if __name__ == "__main__":
    main()
