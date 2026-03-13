from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Track:
    start_time_str: str
    artist: str
    title: str
    label: Optional[str] = None


@dataclass
class Mix:
    tracks: list[Track]
    audio_file: Optional[Path] = None
    title: Optional[str] = None
