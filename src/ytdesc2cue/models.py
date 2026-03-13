from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class Track:
    start_time_str: str
    artist: str
    title: str


@dataclass
class Mix:
    tracks: List[Track]
    audio_file: Optional[Path] = None
