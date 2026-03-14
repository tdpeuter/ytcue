# ytcue

*Note: This repository was written as an experiment exploring AI-assisted development with Google Antigravity.*

A modular Python CLI tool suite that converts YouTube tracklist descriptions into MusicBee-compatible CUE sheets. Built with the Unix DOTADIW philosophy — each tool does one thing, and they compose via piping.

## Installation

```bash
uv pip install -e .
```

For full YouTube compatibility, install [Deno](https://deno.land/) (`winget install --id=DenoLand.Deno` on Windows).

## Quick Start

```bash
# From multiple local audio files (auto-searches each, writes .cue files)
ytcue track1.mp3 track2.flac URL1

# Batch: interactively process folders or multiple files
ytcue-batch ./my_mixes/ file1.mp3

# Fully autonomous: recursively process directories or multiple files
ytcue-auto ./music_library/ file1.mp3
```

## Tool Suite

| Tool | Purpose |
|---|---|
| `ytcue` | All-in-one orchestrator (description → comments fallback → CUE) |
| `ytcue-batch` | Interactive batch processing for directories |
| `ytcue-auto` | Fully autonomous recursive processing |
| `ytcue` | Core parser: tracklist text → CUE sheet |
| `ytdesc` | Fetch YouTube description → stdout |
| `ytcomments` | Find tracklist in comments → stdout |
| `ytaudio-query` | Audio file tags → search query string |

## Piping Examples

```bash
ytdesc "https://youtube..." | ytcue -a mix.flac > mix.cue
ytcomments "https://youtube..." | ytcue -a mix.flac > mix.cue
```

## Documentation

- **[Usage Guide](docs/usage.md)** — Detailed tool reference, options, and composition examples
- **[Parsing Heuristics](docs/heuristics.md)** — How the parser splits artists, titles, and handles edge cases
- **[MusicBee Compatibility](docs/musicbee.md)** — CUE sheet format requirements for MusicBee

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to get started.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
