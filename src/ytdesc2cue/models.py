from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class Track:
    start_time_str: str
    artist: str
    title: str
    label: Optional[str] = None


@dataclass
class Mix:
    tracks: List[Track]
    audio_file: Optional[Path] = None
