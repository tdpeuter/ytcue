import re
from typing import Tuple

# Standard separators for splitting track into Artist - Title
DASH_PATTERN = r"\s+[\-\–\—\―]\s+"


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
        # (feat. XYZ), (ft. XYZ), [feat. XYZ], [ft. XYZ]
        r"[\(\[](?:feat\.?|ft\.?|featuring)\s+([^)\]]+)[\)\]]",
        # feat. XYZ at end of string
        r"(?:feat\.?|ft\.?|featuring)\s+([^-]+)$",
        # (with XYZ), [with XYZ]
        r"[\(\[](?:with|w/)\s+([^)\]]+)[\)\]]",
        # (prod. XYZ) — producer credits sometimes in feat position
        r"[\(\[]prod\.?\s+([^)\]]+)[\)\]]",
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


def _is_inside_brackets_or_quotes(text: str, index: int) -> bool:
    """
    Given a text and an index, determines heuristically if that index
    is inside a pair of brackets (), [], or quotes "", ''.
    """
    left_part = text[:index]
    right_part = text[index:]

    if left_part.count("(") > left_part.count(")") and ")" in right_part:
        return True
    if left_part.count("[") > left_part.count("]") and "]" in right_part:
        return True
    if left_part.count('"') % 2 != 0 and '"' in right_part:
        return True
    if left_part.count("'") % 2 != 0 and "'" in right_part:
        return True

    return False


def _find_by_split(raw_text: str) -> Tuple[str, str]:
    """
    Heuristically attempts to split "Title by Artist" backwards.
    Returns (artist, title) if a valid split is found, else ("", raw_text).
    """
    by_matches = list(re.finditer(r"\s+by\s+", raw_text, re.IGNORECASE))

    # Iterate backwards, assuming the last valid "by" is the separator
    for match in reversed(by_matches):
        start = match.start()
        end = match.end()

        if _is_inside_brackets_or_quotes(raw_text, start):
            continue

        left_part = raw_text[:start].strip()
        right_part = raw_text[end:].strip()

        # Heuristic rules to avoid false positives:
        right_lower = right_part.lower()
        left_lower = left_part.lower()

        # 1. Right side is a pronoun
        if right_lower in ("me", "you", "him", "her", "it", "us", "them"):
            continue

        # 2. Right side starts with an article and doesn't seem like a capitalized band name
        # E.g., "Down by the river" vs "Song by The Beatles"
        if right_lower.startswith(("the ", "a ", "an ")):
            # If the rest of the right part is not capitalized, it's probably a sentence
            words = right_part.split()
            if len(words) > 1 and words[1].islower():
                continue

        # 3. Left side ends with common directional/positional verbs
        if left_lower.endswith(
            (
                "stand",
                "down",
                "close",
                "surrounded",
                "passed",
                "pass",
                "fly",
                "go",
                "went",
            )
        ):
            continue

        return right_part, left_part

    return "", raw_text


def split_track_string(
    raw_text: str,
    artist_title_format: str = "auto",
    extract_feat: bool = False,
    primary_separator: str = None,
) -> Tuple[str, str]:
    """
    Given a raw track string (e.g. 'Robyn, Yaeji  - Beach2k20 - Yaeji Remix'),
    splits it into (artist, title).
    """
    # Clean up YouTube's artifact (Mixed) or [Mixed] globally before any heuristic processing
    # but save them to be injected into the Title string later
    global_tags = []

    def extract_mixed(m):
        global_tags.append(m.group(1).strip())
        return ""

    raw_text = re.sub(
        r"\s*([\(\[]mixed[\)\]])", extract_mixed, raw_text, flags=re.IGNORECASE
    )

    used_separator = primary_separator

    if primary_separator == "by":
        parts = re.split(r"\s+by\s+", raw_text, flags=re.IGNORECASE)
        # Fallback to hyphen if no 'by' was found in this specific line
        if len(parts) == 1:
            used_separator = "-"
            parts = re.split(DASH_PATTERN, raw_text)
    else:
        used_separator = "-"
        parts = re.split(DASH_PATTERN, raw_text)

    artist, title = "", ""

    if len(parts) == 1:
        # If no separator worked, try smart fallback if it wasn't a forced 'by'
        if used_separator != "by" and " by " in raw_text.lower():
            artist, title = _find_by_split(raw_text)
        else:
            artist, title = "", raw_text
    elif used_separator == "by" or artist_title_format == "title-artist":
        title = parts[0]
        artist = (
            " ".join(parts[1:]) if used_separator == "by" else " - ".join(parts[1:])
        )
    elif artist_title_format == "artist-title":
        artist = parts[0]
        title = " - ".join(parts[1:])
    else:
        part1 = parts[0]
        part2 = " - ".join(parts[1:])

        # Heuristic rules for part 1 being the title
        part1_lower = part1.lower()
        part1_is_title_prob = 0

        # ... (rest of heuristic rules)
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

    # Clean up literal (Remix) or [Remix] tags from the artist string and move to title
    artist_tags = []

    def extract_remix(m):
        artist_tags.append(m.group(1).strip())
        return ""

    artist = re.sub(
        r"\s*([\(\[]remix[\)\]])", extract_remix, artist, flags=re.IGNORECASE
    )

    # Also strip trailing " Remix" if the performer string ends with it
    def extract_trailing_remix(m):
        artist_tags.append(m.group(1).strip())
        return ""

    artist = re.sub(
        r"\s+(remix)$", extract_trailing_remix, artist, flags=re.IGNORECASE
    ).strip()

    all_tags = global_tags + artist_tags
    if all_tags:
        title = title.strip() + " " + " ".join(all_tags)

    return extract_feat_artists(title, artist, extract_feat)
