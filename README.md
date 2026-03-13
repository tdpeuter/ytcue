# ytdesc2cue

*Note: This repository was written as an experiment exploring AI-assisted development with Google Antigravity.*

A modular Python CLI tool suite that converts YouTube tracklist descriptions into MusicBee-compatible CUE sheets. Built with the Unix DOTADIW philosophy — each tool does one thing, and they compose via piping.

## Installation

```bash
uv pip install -e .
```

For full YouTube compatibility, install [Deno](https://deno.land/) (`winget install --id=DenoLand.Deno` on Windows).

## Quick Start

```bash
# From a local audio file (auto-searches YouTube, writes mix.cue)
ytcue mix.flac

# From a YouTube URL
ytcue "https://youtube.com/watch?v=..." -a mix.flac -o mix.cue

# Batch: interactively process a directory
ytcue-batch ./my_mixes/

# Fully autonomous: recursively process everything
ytcue-auto ./music_library/
```

## Tool Suite

| Tool | Purpose |
|---|---|
| `ytcue` | All-in-one orchestrator (description → comments fallback → CUE) |
| `ytcue-batch` | Interactive batch processing for directories |
| `ytcue-auto` | Fully autonomous recursive processing |
| `ytdesc2cue` | Core parser: tracklist text → CUE sheet |
| `ytdesc` | Fetch YouTube description → stdout |
| `ytcomments` | Find tracklist in comments → stdout |
| `ytaudio-query` | Audio file tags → search query string |

## Piping Examples

```bash
ytdesc "https://youtube..." | ytdesc2cue -a mix.flac > mix.cue
ytcomments "https://youtube..." | ytdesc2cue -a mix.flac > mix.cue
```

## Documentation

- **[Usage Guide](docs/usage.md)** — Detailed tool reference, options, and composition examples
- **[Parsing Heuristics](docs/heuristics.md)** — How the parser splits artists, titles, and handles edge cases
- **[MusicBee Compatibility](docs/musicbee.md)** — CUE sheet format requirements for MusicBee
