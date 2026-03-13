import argparse
import sys
from pathlib import Path
import yt_dlp
from tinytag import TinyTag

from ytdesc2cue.cli import process_input
from ytdesc2cue.cue import generate_cue_sheet
from ytdesc2cue.parser import parse_lines

AUDIO_EXTENSIONS = {".flac", ".opus", ".mp3", ".m4a", ".wav", ".aac", ".ogg"}


def get_audio_search_query(filepath: Path) -> str:
    """Extracts metadata to form a YouTube search query, falling back to filename."""
    try:
        tag = TinyTag.get(filepath)
        artist = tag.artist or tag.albumartist
        title = tag.title
        if artist and title:
            return f"{artist} - {title}"
        elif title:
            return title
    except Exception:
        pass

    # Fallback to filename without extension
    return filepath.stem


def _filter_warnings(msg):
    if "No supported JavaScript runtime could be found" in msg:
        return
    print(f"Warning: {msg}", file=sys.stderr)


class MyLogger:
    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        _filter_warnings(msg)

    def error(self, msg):
        print(msg, file=sys.stderr)


def fetch_youtube_data(query_or_url: str) -> dict:
    """Uses yt-dlp to fetch the description of a YouTube video or search result."""

    # If it doesn't look like a URL, treat it as a search
    if not query_or_url.startswith("http"):
        query_or_url = f"ytsearch1:{query_or_url}"

    ydl_opts = {
        "quiet": True,
        "extract_flat": False,  # We need the full info, not just playlist links
        "nocheckcertificate": True,
        "logger": MyLogger(),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query_or_url, download=False)

            if "entries" in info:
                # It was a search, get the first entry
                entries = info.get("entries", [])
                if not entries:
                    print("Warning: No search results found.", file=sys.stderr)
                    return None
                info = entries[0]

            if "description" in info and info["description"]:
                return {
                    "title": info.get("title", "Unknown Title"),
                    "url": info.get("webpage_url", query_or_url),
                    "description": info["description"],
                }
            else:
                print(
                    f"Warning: No description found for video '{info.get('title', 'Unknown')}'.",
                    file=sys.stderr,
                )
                return None
    except Exception as e:
        print(f"Error fetching YouTube data: {e}", file=sys.stderr)
        return None


def get_missing_cue_files(directory: Path) -> list[Path]:
    """Returns a list of audio files in the directory that don't have a corresponding .cue file."""
    audio_files = []
    for f in directory.iterdir():
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS:
            cue_path = f.with_suffix(".cue")
            if not cue_path.exists():
                audio_files.append(f)
    return sorted(audio_files)


def main():
    parser = argparse.ArgumentParser(
        description="Interactive batch wrapper to fetch YouTube descriptions for audio files missing CUE sheets."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Directory containing audio files, or a single audio file.",
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

    args = parser.parse_args()

    audio_files = []
    if args.path.is_file():
        audio_files = [args.path]
    elif args.path.is_dir():
        audio_files = get_missing_cue_files(args.path)
    else:
        print(f"Error: {args.path} is not a valid file or directory.", file=sys.stderr)
        sys.exit(1)

    if not audio_files:
        print(f"No audio files missing CUE sheets found in {args.path}.")
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
                # Auto-search triggered
                print(f'Searching YouTube for: "{search_query}"...')
                yt_data = fetch_youtube_data(search_query)
            else:
                print("Fetching URL data...")
                yt_data = fetch_youtube_data(url_or_query)

            if not yt_data:
                continue  # Try again

            print(f"\n--- Found Video: {yt_data['title']} ---")
            lines = yt_data["description"].splitlines()

            # Test parse to show what we found
            parsed = parse_lines(lines)
            if not parsed:
                print("\nWarning: No valid timestamps found in the video description.")
                print(
                    "Tip: A tracklist might be in the pinned comments! Check the video here:"
                )
                print(f" -> {yt_data['url']}")

                print(
                    "\nIf you found a tracklist, paste it below (press Enter twice when done)."
                )
                print(
                    "Or just press Enter immediately to retry a different search/URL."
                )

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
                    continue  # User pressed enter immediately to skip/retry

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
                    # Build string for artist and title, taking care of empty artist
                    track_repr = f"[{track.start_time_str}] "
                    if track.artist:
                        track_repr += f"{track.artist} - "
                    track_repr += track.title
                    print(f"  {track_repr}")
                if len(tracks) > 3:
                    print("  ...")

            confirm = (
                input(
                    "\nDoes this look correct? [Y to generate / n to retry / s to skip]: "
                )
                .strip()
                .lower()
            )
            if confirm == "s":
                print("Skipping...")
                break
            elif confirm == "n":
                continue  # Loop back to prompt

            # Generate CUE
            try:
                mix.audio_file = audio_file  # Associate with the actual audio file name
                cue_content = generate_cue_sheet(mix, args.separator)

                cue_path = audio_file.with_suffix(".cue")
                cue_path.write_text(cue_content, encoding="utf-8")
                print(f"Successfully created {cue_path.name}")
                break  # Done with this file, move to next
            except Exception as e:
                print(f"Error generating CUE sheet: {e}")
                break


if __name__ == "__main__":
    main()
