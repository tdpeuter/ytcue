# Usage Guide

## Orchestrators

### `ytcue` — All-in-One

The simplest way to generate a CUE sheet. Give it a URL or an audio file:

```bash
# From a local audio file (auto-searches YouTube, writes mix.cue next to it)
ytcue mix.flac

# From a YouTube URL
ytcue "https://youtube.com/watch?v=..." -a mix.flac -o mix.cue
```

**What it does:**
1. Reads audio file metadata to build a YouTube search query.
2. Fetches the video description.
3. If no timestamps found, automatically tries fetching from comments.
4. Generates the CUE sheet (auto-named from the audio file).
5. Uses the video/audio title as the CUE sheet title.

### `ytcue-batch` — Interactive Batch

Process an entire directory of audio files missing CUE sheets with human-in-the-loop confirmation:

```bash
ytcue-batch ./my_mixes/
```

For each file, it will:
1. Extract metadata from the audio file to build a YouTube search query.
2. Prompt you for a URL (or auto-search on Enter, `s` to skip).
3. Fetch the description. If empty, offer to try comments interactively.
4. Preview parsed tracks and ask for confirmation before writing.

### `ytcue-auto` — Fully Autonomous

Zero-interaction recursive processing:

```bash
ytcue-auto ./music_library/
```

For every audio file missing a `.cue` sheet (recursively), it will:
1. Auto-search YouTube using the file's metadata.
2. Try the description, then fall back to comments.
3. Generate and write the CUE sheet — no prompts, no interaction.
4. Report a summary of successes/failures at the end.

---

## Standalone Tools

Each tool is independent and designed for piping.

### `ytdesc` — Fetch YouTube Descriptions

```bash
# Print a video's description to stdout
ytdesc "https://youtube.com/watch?v=..."

# Pipe directly into the CUE generator
ytdesc "https://youtube.com/watch?v=..." | ytdesc2cue -a mix.flac -o mix.cue
```

### `ytcomments` — Find Tracklists in Comments

Scans up to 100 top-sorted comments and picks the one with the most timestamps:

```bash
ytcomments "https://youtube.com/watch?v=..."

# Pipe into the CUE generator
ytcomments "https://youtube.com/watch?v=..." | ytdesc2cue -a mix.flac -o mix.cue
```

### `ytaudio-query` — Extract Search Queries from Audio Tags

Reads TinyTag metadata (artist, title) from an audio file and prints a search string:

```bash
ytaudio-query mix.flac
# Output: "DJ Shadow - Essential Mix 2016"
```

### `ytdesc2cue` — Core Parser

Reads a tracklist from stdin or a file and generates a CUE sheet:

```bash
# From a file
ytdesc2cue description.txt -a mix.flac -o mix.cue

# From stdin
cat tracklist.txt | ytdesc2cue -a mix.flac
```

---

## Composition Examples

The standalone tools compose freely via piping:

```bash
# Manual pipeline: description → CUE
ytdesc "https://youtube..." | ytdesc2cue -a mix.flac > mix.cue

# Manual pipeline: comments → CUE
ytcomments "https://youtube..." | ytdesc2cue -a mix.flac > mix.cue

# Full auto: audio tags → search → description → CUE
ytaudio-query mix.flac | xargs -I {} ytdesc "{}" | ytdesc2cue -a mix.flac > mix.cue
```

---

## `ytdesc2cue` Options

| Flag | Description |
|---|---|
| `-a, --audio` | Audio file name to reference in the CUE sheet |
| `-o, --output` | Output CUE file path (stdout if omitted) |
| `-f, --format` | `auto`, `artist-title`, or `title-artist` |
| `-s, --separator` | Artist separator (default: `; ` for MusicBee) |
| `--extract-feat` | Extract `(feat. XYZ)` into the performer field |
| `--include-labels` | Include record labels as `REM LABEL` comments |
| `-y, --yes` | Overwrite output without prompting |

---

## Emoji Support

CUE sheets are saved using `UTF-8 with BOM` encoding, ensuring emojis and Unicode characters render correctly in Windows media players like MusicBee and foobar2000.

## Non-Tracklist Text

The parser automatically ignores lines that don't begin with a timestamp. You can safely pipe entire raw YouTube descriptions without manual cleanup.

## YouTube JavaScript Runtimes

Recent YouTube changes require `yt-dlp` to use a JavaScript interpreter for metadata extraction. If you see warnings about missing JS runtimes or YouTube fails to return descriptions, install **Deno**:

- **Windows:** `winget install --id=DenoLand.Deno`
- **Linux:** `curl -fsSL https://deno.land/install.sh | sh`

The tools automatically suppress the benign "No supported JavaScript runtime" warning to keep your console clean.
