from pathlib import Path
from ytdesc2cue.models import Mix


# Map audio file extensions to CUE FILE types.
# MusicBee treats WAVE as a generic lossless container type.
# MP3 is explicitly required for .mp3 files.
_CUE_FILE_TYPES = {
    ".wav": "WAVE",
    ".flac": "WAVE",
    ".aiff": "WAVE",
    ".aif": "WAVE",
    ".mp3": "MP3",
    # Formats without a formal CUE type — WAVE is the safest fallback for MusicBee.
    ".ogg": "WAVE",
    ".opus": "WAVE",
    ".m4a": "WAVE",
    ".aac": "WAVE",
    ".wma": "WAVE",
}


def _get_cue_file_type(audio_path: Path | None) -> str:
    """Returns the CUE FILE type keyword for the given audio file extension."""
    if audio_path is None:
        return "WAVE"
    return _CUE_FILE_TYPES.get(audio_path.suffix.lower(), "WAVE")


def _escape_cue_string(value: str) -> str:
    """Escapes double quotes inside CUE string values."""
    return value.replace('"', "'")


def generate_cue_sheet(
    mix: Mix, artist_separator: str = "; ", include_labels: bool = False
) -> str:
    """
    Generates a MusicBee-compatible CUE sheet from a Mix object.

    Format follows the CDRWIN CUE sheet specification:
    - Disc-level: PERFORMER, TITLE, FILE (in that order)
    - Track-level: TRACK, TITLE, PERFORMER, INDEX 01
    - Encoding: caller writes with UTF-8 BOM for MusicBee Unicode support.
    """
    mix_title = _escape_cue_string(mix.title or "YouTube Mix")
    lines = [
        'REM GENRE "Mix"',
        'PERFORMER "Various Artists"',
        f'TITLE "{mix_title}"',
    ]

    # Audio file declaration
    if mix.audio_file:
        file_name = mix.audio_file.name
        file_type = _get_cue_file_type(mix.audio_file)
    else:
        file_name = "audio.flac"
        file_type = "WAVE"

    lines.append(f'FILE "{file_name}" {file_type}')

    # Tracks
    for index, track in enumerate(mix.tracks, 1):
        lines.append(f"  TRACK {index:02d} AUDIO")

        # TITLE (required)
        title = _escape_cue_string(track.title)
        lines.append(f'    TITLE "{title}"')

        # PERFORMER (optional — omitting it inherits disc-level performer)
        if track.artist:
            performer = _escape_cue_string(track.artist.replace(",", artist_separator))
            lines.append(f'    PERFORMER "{performer}"')

        # Optional label/publisher as a REM comment
        if include_labels and track.label:
            label = _escape_cue_string(track.label)
            lines.append(f'    REM LABEL "{label}"')

        # INDEX 01 MM:SS:FF (must be last in the track block)
        # MM can exceed 99 for long mixes — MusicBee handles this correctly.
        parts = track.start_time_str.split(":")
        if len(parts) == 3:
            h, m, s = [int(p) for p in parts]
            total_minutes = (h * 60) + m
            cue_time = f"{total_minutes:02d}:{s:02d}:00"
        else:
            m, s = [int(p) for p in parts]
            cue_time = f"{m:02d}:{s:02d}:00"

        lines.append(f"    INDEX 01 {cue_time}")

    return "\n".join(lines) + "\n"
