from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


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
