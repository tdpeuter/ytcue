"""Audio file metadata utilities."""

import sys
from pathlib import Path
from typing import Any

from tinytag import TinyTag

AUDIO_EXTENSIONS = {".flac", ".opus", ".mp3", ".m4a", ".wav", ".aac", ".ogg"}


GENERIC_ARTISTS = {"various artists", "va", "unknown"}


def get_audio_search_query(filepath: Path) -> str:
    """Extracts metadata to form a YouTube search query, falling back to filename.
    If a YouTube URL is embedded in the metadata (e.g., by yt-dlp), it returns the exact URL."""
    try:
        import re

        from mutagen import File

        audio = File(filepath)
        if audio and audio.tags:
            # Search all tag values for a youtube URL
            for key, val in audio.tags.items():
                text = str(val)
                # Look for youtube video URLs
                pattern = r"(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]+)"
                match = re.search(pattern, text)
                if match:
                    return match.group(1)
    except Exception:
        pass

    try:
        tag = TinyTag.get(filepath)
        artist = tag.artist or tag.albumartist
        title = tag.title

        # Filter out generic artist names
        if artist and artist.lower().strip() in GENERIC_ARTISTS:
            artist = None

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


def gather_audio_files(paths: list[Path], recursive: bool = False) -> list[Path]:
    """
    Gathers a unique list of audio files missing CUE sheets from a list of paths.
    Paths can be individual files or directories.
    """
    audio_files = set()
    for path in paths:
        if path.is_file():
            if path.suffix.lower() in AUDIO_EXTENSIONS:
                cue_path = path.with_suffix(".cue")
                if not cue_path.exists():
                    audio_files.add(path)
        elif path.is_dir():
            if recursive:
                found = get_missing_cue_files_recursive(path)
            else:
                found = get_missing_cue_files(path)
            audio_files.update(found)

    return sorted(list(audio_files))


def write_grouping_tag(filepath: Path, grouping: str) -> bool:
    """
    Writes the grouping tag to an audio file's metadata using mutagen.

    Supports FLAC, MP3 (ID3), M4A/MP4, and OGG/Opus.
    Returns True on success, False on failure.
    """
    import mutagen.id3
    from mutagen import File

    ext = filepath.suffix.lower()

    try:
        audio: Any = File(filepath)
        if audio is None:
            print(
                f"Warning: Could not read metadata for {filepath.name}.",
                file=sys.stderr,
            )
            return False

        if ext == ".flac":
            audio["GROUPING"] = grouping
            audio.save()
        elif ext == ".mp3":
            if audio.tags is None:
                audio.add_tags()
            tit1: Any = mutagen.id3.TIT1
            audio.tags.add(tit1(encoding=3, text=[grouping]))
            audio.save()
        elif ext in (".m4a", ".aac"):
            audio["\xa9grp"] = [grouping]
            audio.save()
        elif ext == ".opus":
            audio["GROUPING"] = grouping
            audio.save()
        elif ext == ".ogg":
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
