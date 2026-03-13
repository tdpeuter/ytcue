# Parsing Heuristics

The `ytdesc2cue` program tries to intelligently extract track titles and artist names from raw YouTube chapter or description lines. Since YouTube descriptions don't enforce a standardized format, this tool relies on a series of heuristics located in `src/ytdesc2cue/heuristics.py`.

This document explains the strategies the program takes to split text boundaries.

## 0. Timestamp Parsing (`parser.py`)

### Supported Timestamp Formats
The parser recognizes timestamps in the following formats at the beginning of a line:
- `MM:SS` or `HH:MM:SS` (colons)
- `MM.SS` or `HH.MM.SS` (dots)
- `[MM:SS]` or `[HH:MM:SS]` (bracketed)

### Timestamp Separators
Some YouTube descriptions use a separator character between the timestamp and the track info:
```
00:00 | ASC - Vapour Trail
06:48 - Eusebeia - More Than Lucky
1:00:14 – Pixl - Empath
```
The parser handles various characters as separators transparently, including hyphens `-`, en-dashes `–`, em-dashes `—`, colons `:`, and pipes `|`. These are consumed during the timestamp parsing phase and never reach the track splitting heuristics.

### Label/Publisher Extraction
Some descriptions include the record label on the line immediately following each track:
```
00:00 | ASC - Vapour Trail
Over/Shadow

06:48 | Eusebeia - More Than Lucky
Modern Conveniences
```
The `parse_lines_with_labels` function peeks at the next non-empty line after each timestamp line. If that line is **not** itself a timestamped track, it is captured as the track's `label`. This label can be optionally included in the CUE output as a `REM LABEL` comment per track via the `--include-labels` flag.

## 1. Tracklist-Level Evaluation

Before processing individual lines, the program evaluates the entire tracklist (all parsed lines) in `src/ytdesc2cue/cli.py` to identify unified patterns.

- If a significant majority of lines (e.g., > 60%) contain the string `" by "` and fewer than 40% contain a hyphen (`"-"`), the program enforces `"by"` as the *primary separator* for the entire list.
- If this check doesn't pass, the program processes each line individually, assuming a hyphen (`-`) as the primary separator by default.

## 2. Line-by-Line Splitting (`split_track_string`)

### The Hyphen Separator (`-`)
By default, the easiest and most common separator is a hyphen surrounded by spaces: ` - `.
If `artist-title` or `title-artist` format is specifically provided by the user, the program simply blindly takes the first half as the artist/title and the remaining joined halves as the other.

If the requested format is `auto` (default) and a hyphen exists, the program falls back to probabilistic heuristics to decide which side is the Title and which is the Artist:
- **Title Keywords:** Left side is heavily favored if it contains `remix`, `edit`, `mix`, or `dub`. (Counter-balanced against the right side).
- **Quotes:** The presence of single or double quotes adds weight (`"`, `'`, `’`).
- **Parentheses:** The presence of both `(` and `)` adds weight.

### The "by" Separator (`by`)
When a line doesn't contain a hyphen, or if the tracklist-level evaluation determined `"by"` is the primary separator, the program attempts to split the string on the word `"by"`. 

Because "by" is a common English word, checking for it inline is extremely prone to false positives (e.g., "Stand by Me", "Down by the River"). The `_find_by_split` function utilizes several smart safeguards:

1. **Backwards Evaluation**: Assumes the *last* valid occurrence of "by" usually separates Title and Artist.
2. **Bracket & Quote Evasion**: Ignores any `"by"` found inside balanced parentheses `()`, brackets `[]`, or quote blocks `""`, `''`.
3. **Pronoun Avoidance**: Ignored if the right side is a standalone pronoun like `me`, `you`, `him`, `it`, `them`.
4. **Article Avoidance**: Ignored if the right side starts with `the `, `a `, or `an ` and is followed by lowercase words (suggesting a sentence clause rather than a formalized band name).
5. **Verb Avoidance**: Ignored if the left side ends with common positional verbs like `stand`, `down`, `close`, `pass`, `fly`, `go` (e.g., "Stand by Me").

### "Mixed" and "Remix" Tag Cleanup
YouTube Music and DJ sets often natively append tags like `(Mixed)` or `[Mixed]` to the end of track names or artists. Because they use brackets and parentheses, they can heavily bias the auto-formatting heuristics if they wind up on the Artist side of the string, and they incorrectly clutter the CUE `PERFORMER` fields.

To prevent this, `ytdesc2cue` performs a case-insensitive, global extraction of any `(Mixed)` or `[Mixed]` tags across the entire trackline string immediately before running any of the separation heuristics listed above. The tags are safely stored in memory.

Additionally, after a string is split, the program performs one last pass on the isolated **Artist** string to extract any standalone `(Remix)`, `[Remix]`, or tailing `" Remix"` words that shouldn't be formally stored in the CUE `PERFORMER` parameters. 

Finally, all extracted `(Mixed)` and `Remix` variations are cleanly appended to the **Title** string, where they logically belong!

### Long Dash Support
In addition to standard hyphens `-`, the heuristic separator detection now supports en-dashes `–` and em-dashes `—`. These are commonly used in YouTube descriptions when copy-pasted from other sources.

### Trailing Dot Cleanup
Some tracklists contain trailing periods at the end of every line (e.g., `"Artist - Title."`). If `ytdesc2cue` detects that more than 80% of the tracks in a list end with a period, it will automatically strip the trailing period from all track titles to ensure clean metadata.

## 3. Embellishment Extraction (`extract_feat_artists`)

Once a string has successfully been cut into a `Title` and `Artist`, the program offers an optional `extract_feat` feature. When enabled, it natively searches both the `Title` AND the `Artist` string for expressions that designate featured guests.

Supported patterns:
- `(feat. XYZ)`
- `(ft. XYZ)`
- `feat XYZ` at the tail end of the string
- `ft XYZ` at the tail end of the string

The identified artist `XYZ` is removed from its original location and normalized. It is then intelligently deduplicated and appended to the final Artist string using semicolons (e.g. `Main Artist; XYZ`), ready for direct export into the CUE performer metadata.
