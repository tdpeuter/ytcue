from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from ytcue.core.models import Track


class Severity(Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class Diagnostic:
    severity: Severity
    message: str
    track_index: Optional[int] = None

    def __str__(self) -> str:
        prefix = f"[{self.severity.value}]"
        if self.track_index is not None:
            prefix += f" Track {self.track_index}:"
        return f"{prefix} {self.message}"


@dataclass
class ProcessingResult:
    file_path: Path
    success: bool = False
    cue_written: bool = False
    diagnostics: list[Diagnostic] = field(default_factory=list)

    def add_warning(self, message: str, track_index: Optional[int] = None) -> None:
        self.diagnostics.append(Diagnostic(Severity.WARNING, message, track_index))

    def add_error(self, message: str, track_index: Optional[int] = None) -> None:
        self.diagnostics.append(Diagnostic(Severity.ERROR, message, track_index))
        self.success = False

    @property
    def has_errors(self) -> bool:
        return any(d.severity == Severity.ERROR for d in self.diagnostics)

    @property
    def has_warnings(self) -> bool:
        return any(d.severity == Severity.WARNING for d in self.diagnostics)


def format_summary(results: list[ProcessingResult]) -> str:
    """
    Formats a summary report of all diagnostics across multiple files.
    Files with no diagnostics are excluded from the detailed output.
    """
    if not results:
        return "No files processed."

    total = len(results)
    succeeded = sum(1 for r in results if r.success)
    failed = total - succeeded
    written = sum(1 for r in results if r.cue_written)

    lines = []
    lines.append("=" * 50)
    lines.append(" PROCESSING SUMMARY ")
    lines.append("=" * 50)
    lines.append(f"Total files: {total}")
    lines.append(f"Succeeded:   {succeeded}")
    lines.append(f"Failed:      {failed}")
    lines.append(f"CUE written: {written}")
    lines.append("")

    # Only show files that had diagnostics (warnings or errors)
    files_with_issues = [r for r in results if r.diagnostics]

    if files_with_issues:
        lines.append("--- Details ---")
        for res in files_with_issues:
            status = "PASS" if res.success else "FAIL"
            lines.append(f"\n{res.file_path.name} [{status}]")
            for diag in res.diagnostics:
                lines.append(f"  {diag}")

    return "\n".join(lines)


def _parse_timestamp_to_seconds(timestamp: str) -> float:
    """Converts HH:MM:SS or MM:SS to total seconds."""
    parts = timestamp.split(":")
    if len(parts) == 3:
        h, m, s = map(int, parts)
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:
        m, s = map(int, parts)
        return m * 60 + s
    return 0.0


def validate_timestamps(tracks: list[Track], duration_seconds: float) -> list[Diagnostic]:
    """
    Checks if any track's timestamp exceeds the audio file's duration.
    Returns a list of Diagnostics for any that do.
    """
    diagnostics = []
    # Add a 5 second grace period for rounding differences
    threshold = duration_seconds + 5.0

    for i, track in enumerate(tracks, 1):
        track_seconds = _parse_timestamp_to_seconds(track.start_time_str)
        if track_seconds > threshold:
            # Format audio duration for the message
            m, s = divmod(int(duration_seconds), 60)
            h, m = divmod(m, 60)
            if h > 0:
                dur_str = f"{h:02d}:{m:02d}:{s:02d}"
            else:
                dur_str = f"{m:02d}:{s:02d}"

            msg = f"Timestamp ({track.start_time_str}) exceeds audio duration ({dur_str})"
            diagnostics.append(Diagnostic(Severity.WARNING, msg, track_index=i))

    return diagnostics
