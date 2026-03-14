"""Interactive batch wrapper for processing directories of audio files missing CUE sheets."""

import argparse
import sys
from pathlib import Path

from ytcue.cli.parser import process_input
from ytcue.core.comments import find_tracklist_comment
from ytcue.core.cue import generate_cue_sheet
from ytcue.core.metadata import (
    gather_audio_files,
    get_audio_search_query,
    write_grouping_tag,
)
from ytcue.core.parser import parse_lines
from ytcue.core.youtube import fetch_video_info


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Interactive batch wrapper to fetch YouTube descriptions for audio files "
            "missing CUE sheets."
        )
    )
    parser.add_argument(
        "paths",
        type=Path,
        nargs="+",
        help="Paths to audio files or directories containing audio files.",
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
        help="Artist separator string for the CUE PERFORMER field. Default is '; '",
    )
    parser.add_argument(
        "--extract-feat",
        action="store_true",
        help="Enable attempting to extract (feat.) artists into the performer field.",
    )
    parser.add_argument(
        "--include-labels",
        action="store_true",
        help="Include record label/publisher info as REM LABEL comments in the CUE sheet.",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Overwrite existing CUE files without asking.",
    )

    args = parser.parse_args()
    audio_files = gather_audio_files(args.paths, recursive=False)

    if not audio_files:
        print("No audio files missing CUE sheets found in the provided paths.")
        sys.exit(0)

    print(f"Found {len(audio_files)} audio file(s) missing CUE sheets.")

    for audio_file in audio_files:
        print(f"\n{'=' * 50}")
        print(f"Processing: {audio_file.name}")
        search_query = get_audio_search_query(audio_file)

        while True:
            url_or_query = input(
                f"Provide YouTube URL (Enter to auto-search: \"{search_query}\", or 's' to skip): "
            ).strip()

            if url_or_query.lower() == "s":
                print("Skipping...")
                break

            if not url_or_query:
                print(f'Searching YouTube for: "{search_query}"...')
                yt_data = fetch_video_info(search_query)
            else:
                print("Fetching URL data...")
                yt_data = fetch_video_info(url_or_query)

            if not yt_data:
                continue

            print(f"\n--- Found Video: {yt_data['title']} ---")
            lines = yt_data["description"].splitlines()

            # Test parse to show what we found
            parsed = parse_lines(lines)
            if not parsed:
                print("\nNo timestamps found in the video description.")

                # Interactive comment fallback
                try_comments = (
                    input("Try fetching tracklist from comments? [y/N/s(kip)]: ").strip().lower()
                )

                if try_comments == "s":
                    print("Skipping...")
                    break
                elif try_comments in ["y", "yes"]:
                    url = yt_data["url"]
                    print(f"Fetching comments for {url}...")
                    try:
                        comment_info = fetch_video_info(url, get_comments=True)
                        if comment_info:
                            comments = comment_info.get("comments") or []
                            if comments:
                                tracklist = find_tracklist_comment(comments)
                                if tracklist:
                                    lines = tracklist.splitlines()
                                    parsed = parse_lines(lines)
                                    print("Found tracklist in comments!")
                                else:
                                    print("No tracklist found in comments.")
                            else:
                                print("No comments were returned.")
                        else:
                            print("Could not fetch comments (timeout or error).")
                    except Exception as e:
                        print(f"Error fetching comments: {e}")

                if not parsed:
                    print("\nYou can also paste a tracklist below (press Enter twice when done).")
                    print("Or just press Enter immediately to retry a different search/URL.")

                    user_pasted_lines = []
                    while True:
                        line = input()
                        if not line:
                            break
                        user_pasted_lines.append(line)

                    if user_pasted_lines:
                        parsed = parse_lines(user_pasted_lines)
                        if parsed:
                            lines = user_pasted_lines
                        else:
                            print(
                                "Still no valid timestamps found in the pasted text. Please retry."
                            )
                            continue
                    else:
                        continue

            # Generate the Mix object early to preview parsing heuristics
            try:
                mix = process_input(lines, args.format, args.extract_feat)
                tracks = mix.tracks
            except Exception as e:
                print(f"Error parsing tracklist: {e}")
                continue

            print(f"\nFound {len(tracks)} tracks.")
            if len(tracks) > 0:
                print("First 3 tracks parsed preview:")
                for track in tracks[:3]:
                    track_repr = f"[{track.start_time_str}] "
                    if track.artist:
                        track_repr += f"{track.artist} - "
                    track_repr += track.title
                    print(f"  {track_repr}")
                if len(tracks) > 3:
                    print("  ...")

            confirm = (
                input("\nDoes this look correct? [Y to generate / n to retry / s to skip]: ")
                .strip()
                .lower()
            )
            if confirm == "s":
                print("Skipping...")
                break
            elif confirm == "n":
                continue

            # Generate CUE
            try:
                mix.audio_file = audio_file
                cue_content = generate_cue_sheet(
                    mix, args.separator, include_labels=args.include_labels
                )

                cue_path = audio_file.with_suffix(".cue")
                if cue_path.exists() and not args.yes:
                    overwrite = (
                        input(f"Warning: {cue_path.name} already exists. Overwrite? [y/N]: ")
                        .strip()
                        .lower()
                    )
                    if overwrite not in ["y", "yes"]:
                        print("Skipping write...")
                        break

                cue_path.write_text(cue_content, encoding="utf-8-sig")
                print(f"Successfully created {cue_path.name}")
                write_grouping_tag(audio_file, mix.title or "YouTube Mix")
                break
            except Exception as e:
                print(f"Error generating CUE sheet: {e}")
                break


if __name__ == "__main__":
    main()
