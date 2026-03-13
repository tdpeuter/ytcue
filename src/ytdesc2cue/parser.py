import re
from typing import List, Tuple

# Matches HH:MM:SS, MM:SS, HH.MM.SS, MM.SS at the beginning of the line
TIMESTAMP_PATTERN = re.compile(r"^\[?(?:(\d{1,2})[:.])?(\d{1,2})[:.](\d{2})\]?\s+(.*)$")


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
