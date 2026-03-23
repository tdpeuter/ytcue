# Diagnostics & Validation

ytcue includes a centralized diagnostic system to help identify issues when parsing YouTube tracklists and generating CUE sheets. 

## Warning & Error Collection
In **auto mode** (`ytcue-auto`), the sheer volume of output can make it difficult to spot issues. The diagnostic system collects all warnings and errors encountered during processing and prints a grouped summary at the end of the run.

### Severity Levels
- **WARNING**: Informational issues that do not prevent the generation of a CUE sheet.
- **ERROR**: Critical issues that abort the generation of a CUE sheet for a specific file (e.g., no tracklist found).

## Timestamp Duration Validation
A common issue when parsing YouTube descriptions is that the video corresponding to the audio file might be a different cut, extended version, or mix. 

To help catch these discrepancies, ytcue reads the duration of your local audio file and validates all parsed timestamps against it.

If a timestamp exceeds the audio file's duration (with a 5-second grace period for encoding differences), a **WARNING** is generated.

### Behavior by Tool
- **ytcue-auto**: Warnings are printed inline as they are found, and then summarized at the end of the run. The CUE sheet is still generated (a slightly off CUE sheet is often better than none).
- **ytcue-batch**: Warnings are displayed immediately after parsing the tracklist, *before* you are asked to confirm the generation. This gives you the opportunity to cancel (`n`) and retry with a different YouTube URL.
- **ytcue (main)**: Warnings are printed inline before the CUE sheet is written (only when a local audio file is provided).
