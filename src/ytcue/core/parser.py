import re
from typing import Optional

# Common separators between timestamp and track info
TIMESTAMP_SEPARATORS = r"[\-\–\—\―\:\|\s]+"

# Matches HH:MM:SS, MM:SS, HH.MM.SS, MM.SS at the beginning of the line
# Now also handles an optional track number prefix (e.g., "1. 00:00")
# to avoid mistaking track numbers for hours.
TIMESTAMP_PATTERN = re.compile(
    r"^"
    r"(?:\d+[\.\-\s]+)?"  # Optional track number prefix (e.g., "1. ", "01 - ")
    r"\[?"
    r"(?:(\d{1,2}):)?"  # HH: (Must be followed by :)
    r"\s*(\d{1,2})[:.]\s*(\d{2})"  # MM:SS or MM.SS
    r"\]?"
    r"(?:" + TIMESTAMP_SEPARATORS + ")?"  # Optional separator
    r"(.*)$"  # Remaining text
)


def parse_lines(lines: list[str]) -> list[tuple[str, str]]:
    """
    Parses a list of text lines, extracting the timestamp and the remaining text.
    Returns a list of tuples: (timestamp_string, remaining_raw_text).
    """
    parsed = []
    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = TIMESTAMP_PATTERN.search(line)
        if match:
            hours, minutes, seconds, raw_text = match.groups()

            # Reconstruct standardized timestamp format HH:MM:SS or MM:SS
            if hours:
                timestamp = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            else:
                timestamp = f"{int(minutes):02d}:{int(seconds):02d}"

            raw_text = raw_text.strip()
            parsed.append((timestamp, raw_text))

    return parsed


def parse_lines_with_labels(lines: list[str]) -> list[tuple[str, str, Optional[str]]]:
    """
    Parses a list of text lines, extracting timestamp, track text, and an optional
    label/publisher from the line immediately following a timestamped track.
    Returns a list of tuples: (timestamp_string, remaining_raw_text, label_or_none).
    """
    parsed = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1

        if not line:
            continue

        match = TIMESTAMP_PATTERN.search(line)
        if match:
            hours, minutes, seconds, raw_text = match.groups()

            if hours:
                timestamp = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            else:
                timestamp = f"{int(minutes):02d}:{int(seconds):02d}"

            raw_text = raw_text.strip()

            # Peek at the next non-empty line to see if it's a label (non-timestamped text)
            label = None
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                # If the next non-empty line is NOT a timestamp, it's a label
                if not TIMESTAMP_PATTERN.search(next_line):
                    label = next_line
                    i += 1
                break

            parsed.append((timestamp, raw_text, label))

    return parsed
