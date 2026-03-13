import re
from typing import Tuple, List


def extract_feat_artists(
    title: str, current_artist: str, extract_feat: bool = False
) -> Tuple[str, str]:
    """
    Extracts '(feat. XYZ)' or 'feat. XYZ' from the title OR artist string,
    and cleanly appends XYZ to the artist string.
    Returns (new_artist, new_title).
    """
    if not extract_feat:
        return current_artist, title

    feat_patterns = [
        r"\((?:feat\.?|ft\.?)\s+([^)]+)\)",
        r"(?:feat\.?|ft\.?)\s+([^-]+)$",
    ]

    new_title = title
    new_artist = current_artist
    extracted_artists = []

    # Check title
    for pattern in feat_patterns:
        matches = list(re.finditer(pattern, new_title, re.IGNORECASE))
        for match in matches:
            extracted_artists.append(match.group(1).strip())
            new_title = new_title.replace(match.group(0), "").strip()

    # Check artist string (sometimes the feat is natively in the artist half)
    for pattern in feat_patterns:
        matches = list(re.finditer(pattern, new_artist, re.IGNORECASE))
        for match in matches:
            artist_feat = match.group(1).strip()
            extracted_artists.append(artist_feat)
            new_artist = new_artist.replace(match.group(0), "").strip()

    # Clean up trailing non-alphanumeric if we ripped something off the end
    new_title = re.sub(r"[\s\-]+$", "", new_title)
    new_artist = re.sub(r"[\s\-]+$", "", new_artist)

    if extracted_artists:
        for ext_artist in extracted_artists:
            if ext_artist.lower() not in new_artist.lower():
                new_artist += f"; {ext_artist}"

    return new_artist, new_title


def split_track_string(
    raw_text: str, artist_title_format: str = "auto", extract_feat: bool = False
) -> Tuple[str, str]:
    """
    Given a raw track string (e.g. 'Robyn, Yaeji  - Beach2k20 - Yaeji Remix'),
    splits it into (artist, title).
    """
    parts = re.split(r"\s+-\s+", raw_text)
    artist, title = "", ""

    if len(parts) == 1:
        artist, title = "", raw_text
    elif artist_title_format == "title-artist":
        title = parts[0]
        artist = " - ".join(parts[1:])
    elif artist_title_format == "artist-title":
        artist = parts[0]
        title = " - ".join(parts[1:])
    else:
        part1 = parts[0]
        part2 = " - ".join(parts[1:])

        # Heuristic rules for part 1 being the title
        part1_lower = part1.lower()
        part1_is_title_prob = 0

        # 1. Keywords in part 1 highly indicate it is the title
        title_keywords = ["remix", "edit", "mix", "dub"]
        if any(kw in part1_lower for kw in title_keywords):
            part1_is_title_prob += 2

        # 2. Quotation marks indicate title
        if '"' in part1 or "'" in part1 or "’" in part1:
            part1_is_title_prob += 1

        # 3. Parenthesis often indicate title (e.g. Mix name, or feat)
        if "(" in part1 and ")" in part1:
            part1_is_title_prob += 1

        # Also check part 2 to counter-balance
        part2_lower = part2.lower()
        if any(kw in part2_lower for kw in title_keywords):
            part1_is_title_prob -= 2
        if "(" in part2 and ")" in part2:
            part1_is_title_prob -= 1

        if part1_is_title_prob > 0:
            artist, title = part2.strip(), part1.strip()
        else:
            artist, title = part1.strip(), part2.strip()

    return extract_feat_artists(title, artist, extract_feat)
