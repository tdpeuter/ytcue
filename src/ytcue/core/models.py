from dataclasses import dataclass
from pathlib import Path


@dataclass
class Track:
    start_time_str: str
    artist: str
    title: str
    label: str | None = None


@dataclass
class Mix:
    tracks: list[Track]
    audio_file: Path | None = None
    title: str | None = None
