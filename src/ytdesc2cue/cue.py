from ytdesc2cue.models import Mix


def generate_cue_sheet(mix: Mix, artist_separator: str = "; ", include_labels: bool = False) -> str:
    """
    Generates a MusicBee-compatible CUE sheet from a Mix object.
    MusicBee supports standard CUE sheet formatting.
    We format the PERFORMER separating multiple artists (e.g. using ';' which MusicBee handles well).
    """
    # Default header
    lines = [
        "REM GENRE Mix",
        "REM DATE 2024",  # generic fallback, can be improved later
        'PERFORMER "Various Artists"',
        'TITLE "YouTube Mix"',
    ]

    # Audio file declaration
    if mix.audio_file:
        file_name = mix.audio_file.name
        # Use wave to denote standard compatible playback, even if flac/opus (common cue trick, though many players accept FLAC)
        # However, it's safer to use the actual file name and generic WAVE or MP3 depending on player.
        # MusicBee handles exact filenames very well.
        lines.append(f'FILE "{file_name}" WAVE')
    else:
        lines.append('FILE "audio.flac" WAVE')

    # Tracks
    for index, track in enumerate(mix.tracks, 1):
        lines.append(f"  TRACK {index:02d} AUDIO")

        # Format the title
        lines.append(f'    TITLE "{track.title}"')

        # Format the performer(s). Sometimes multiple artists are separated by commas.
        # Replace commas with the chosen separator (like ';') if requested.
        # MusicBee recognizes ';' for multiple artists.
        if track.artist:
            performer = track.artist.replace(",", artist_separator)
            lines.append(f'    PERFORMER "{performer}"')

        # Optional label/publisher as a REM comment
        if include_labels and track.label:
            lines.append(f'    REM LABEL "{track.label}"')

        # Format index/timestamp (CUE requires MM:SS:FF where FF is frames 0-74)
        # Our parsed timestamps are HH:MM:SS or MM:SS
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
