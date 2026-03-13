"""Audio file metadata utilities."""

import argparse
import sys
from pathlib import Path

from tinytag import TinyTag

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


def get_audio_title(filepath: Path) -> str:
    """Extracts the title from audio file metadata, falling back to filename."""
    try:
        tag = TinyTag.get(filepath)
        if tag.title:
            return tag.title
    except Exception:
        pass
    return filepath.stem


def get_missing_cue_files(directory: Path) -> list[Path]:
    """Returns a list of audio files in the directory that don't have a corresponding .cue file."""
    audio_files = []
    for f in directory.iterdir():
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS:
            cue_path = f.with_suffix(".cue")
            if not cue_path.exists():
                audio_files.append(f)
    return sorted(audio_files)


def get_missing_cue_files_recursive(directory: Path) -> list[Path]:
    """Recursively returns audio files missing corresponding .cue files."""
    audio_files = []
    for f in directory.rglob("*"):
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS:
            cue_path = f.with_suffix(".cue")
            if not cue_path.exists():
                audio_files.append(f)
    return sorted(audio_files)


def write_grouping_tag(filepath: Path, grouping: str) -> bool:
    """
    Writes the grouping tag to an audio file's metadata using mutagen.

    Supports FLAC, MP3 (ID3), M4A/MP4, and OGG/Opus.
    Returns True on success, False on failure.
    """
    import mutagen
    from mutagen.flac import FLAC
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4
    from mutagen.oggopus import OggOpus
    from mutagen.oggvorbis import OggVorbis
    from mutagen.id3 import TIT1

    ext = filepath.suffix.lower()

    try:
        if ext == ".flac":
            audio = FLAC(filepath)
            audio["GROUPING"] = grouping
            audio.save()
        elif ext == ".mp3":
            audio = MP3(filepath)
            if audio.tags is None:
                audio.add_tags()
            audio.tags.add(TIT1(encoding=3, text=[grouping]))
            audio.save()
        elif ext in (".m4a", ".aac"):
            audio = MP4(filepath)
            audio["\xa9grp"] = [grouping]
            audio.save()
        elif ext == ".opus":
            audio = OggOpus(filepath)
            audio["GROUPING"] = grouping
            audio.save()
        elif ext == ".ogg":
            audio = OggVorbis(filepath)
            audio["GROUPING"] = grouping
            audio.save()
        else:
            print(
                f"Warning: Cannot write grouping tag to {ext} files.",
                file=sys.stderr,
            )
            return False

        return True
    except Exception as e:
        print(f"Warning: Could not write grouping tag: {e}", file=sys.stderr)
        return False


def main():
    """CLI entry point for ytaudio-query: prints a search query from audio file tags."""
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
