import re
from typing import List, Tuple, Optional

# Common separators between timestamp and track info
TIMESTAMP_SEPARATORS = r"[\-\–\—\―\:\|\s]+"

# Matches HH:MM:SS, MM:SS, HH.MM.SS, MM.SS at the beginning of the line
# Followed by optional separators and then the track text
TIMESTAMP_PATTERN = re.compile(
    r"^\[?(?:(\d{1,2})[:.])?\s*(\d{1,2})[:.]\s*(\d{2})\]?"  # Timestamp
    rf"(?:{TIMESTAMP_SEPARATORS})?"                        # Optional separator
    r"(.*)$"                                                # Remaining text
)


def parse_lines(lines: List[str]) -> List[Tuple[str, str]]:
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


def parse_lines_with_labels(lines: List[str]) -> List[Tuple[str, str, Optional[str]]]:
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
