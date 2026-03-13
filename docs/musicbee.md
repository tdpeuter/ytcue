# MusicBee CUE Sheet Compatibility

This document describes the requirements for a CUE sheet to be correctly recognized and used by [MusicBee](https://getmusicbee.com/).

## File Requirements

| Requirement | Detail |
|---|---|
| **Encoding** | UTF-8 with BOM (`utf-8-sig`). Without the BOM, MusicBee may interpret Unicode characters as ANSI, causing mojibake. |
| **File name** | Must match the audio file name (e.g., `mix.flac` → `mix.cue`). |
| **Location** | Must be in the same directory as the audio file it references. |
| **Extension** | `.cue` |

## FILE Command

The `FILE` command must reference the **exact filename** (including extension) of the audio file.

```
FILE "mix.flac" WAVE
```

### File Type Keywords

| Audio Format | CUE Type | Notes |
|---|---|---|
| `.wav`, `.flac`, `.aiff` | `WAVE` | MusicBee treats `WAVE` as a generic lossless container. |
| `.mp3` | `MP3` | Must use `MP3` explicitly for MP3 files. |
| `.ogg`, `.opus`, `.m4a` | `WAVE` | No formal CUE type exists; `WAVE` is the safest fallback. |

## Track Structure

Each track block must follow this order:

```
  TRACK 01 AUDIO
    TITLE "Track Name"
    PERFORMER "Artist Name"
    INDEX 01 MM:SS:FF
```

- **TITLE**: Required. Double quotes inside values should be escaped or replaced with single quotes.
- **PERFORMER**: Optional at track level. If omitted, inherits disc-level `PERFORMER`.
- **INDEX 01**: Required. Format is `MM:SS:FF` where FF is frames (00–74). Minutes can exceed 99 for long mixes.

## Multiple Artists

MusicBee recognizes `;` as the separator for multiple artists in `PERFORMER` fields:

```
    PERFORMER "Artist A; Artist B"
```

## Optional REM Fields

```
REM GENRE "Mix"
REM DATE 2024
REM LABEL "Record Label"
```

These are metadata hints. MusicBee reads `REM GENRE` and `REM DATE` for library organization.

## Common Pitfalls

- **Wrong FILE type**: Using `WAVE` for an `.mp3` file may cause MusicBee to fail to load tracks.
- **Missing BOM**: Without UTF-8 BOM, non-ASCII characters (emojis, accented letters) will appear garbled.
- **Filename mismatch**: If the `FILE` command references a different filename than the actual audio file, MusicBee will silently ignore the CUE sheet.
- **Quotes in metadata**: Unescaped `"` inside `TITLE` or `PERFORMER` values will break the CUE parser.
