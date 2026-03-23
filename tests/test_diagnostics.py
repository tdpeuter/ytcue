from pathlib import Path

from ytcue.core.diagnostics import Diagnostic, ProcessingResult, Severity, format_summary


def test_processing_result_initialization():
    result = ProcessingResult(file_path=Path("test.mp3"))
    assert not result.success
    assert not result.cue_written
    assert not result.has_errors
    assert not result.has_warnings
    assert len(result.diagnostics) == 0


def test_add_warning():
    result = ProcessingResult(file_path=Path("test.mp3"))
    result.add_warning("This is a warning", track_index=1)

    assert not result.has_errors
    assert result.has_warnings
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].severity == Severity.WARNING
    assert result.diagnostics[0].message == "This is a warning"
    assert result.diagnostics[0].track_index == 1


def test_add_error():
    result = ProcessingResult(file_path=Path("test.mp3"))
    result.success = True  # Should be set to False when error added
    result.add_error("This is an error")

    assert result.has_errors
    assert not result.has_warnings
    assert not result.success
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].severity == Severity.ERROR
    assert result.diagnostics[0].message == "This is an error"
    assert result.diagnostics[0].track_index is None


def test_diagnostic_formatting():
    diag_sys = Diagnostic(Severity.ERROR, "System failure")
    assert str(diag_sys) == "[ERROR] System failure"

    diag_track = Diagnostic(Severity.WARNING, "Title too long", track_index=3)
    assert str(diag_track) == "[WARNING] Track 3: Title too long"


def test_format_summary_empty():
    assert format_summary([]) == "No files processed."


def test_format_summary_with_mixed_results():
    success_result = ProcessingResult(file_path=Path("success.mp3"), success=True, cue_written=True)

    warn_result = ProcessingResult(file_path=Path("warning.mp3"), success=True, cue_written=True)
    warn_result.add_warning("Audio duration exceeded", 2)

    error_result = ProcessingResult(file_path=Path("error.mp3"), success=False, cue_written=False)
    error_result.add_error("No tracklist found")

    results = [success_result, warn_result, error_result]
    summary = format_summary(results)

    # Check header stats
    assert "Total files: 3" in summary
    assert "Succeeded:   2" in summary
    assert "Failed:      1" in summary
    assert "CUE written: 2" in summary

    # Check details section
    assert "--- Details ---" in summary
    assert "warning.mp3 [PASS]" in summary
    assert "[WARNING] Track 2: Audio duration exceeded" in summary
    assert "error.mp3 [FAIL]" in summary
    assert "[ERROR] No tracklist found" in summary

    # Success without diagnostics should NOT be in the details section
    assert "success.mp3" not in summary.split("--- Details ---")[1]


def test_validate_timestamps_valid():
    from ytcue.core.diagnostics import validate_timestamps
    from ytcue.core.models import Track

    tracks = [
        Track(start_time_str="00:00", artist="A", title="T1"),
        Track(start_time_str="01:30", artist="A", title="T2"),
        Track(start_time_str="00:15:00", artist="A", title="T3"),
    ]

    # Duration is 15 minutes (900 seconds) + 1 second.
    # Track 3 is exactly at 15:00.
    diags = validate_timestamps(tracks, 901.0)
    assert len(diags) == 0


def test_validate_timestamps_exceed():
    from ytcue.core.diagnostics import validate_timestamps
    from ytcue.core.models import Track

    tracks = [
        Track(start_time_str="00:00", artist="A", title="T1"),
        Track(start_time_str="05:30", artist="A", title="T2"),
        Track(start_time_str="15:30", artist="A", title="T3"),  # Exceeds bounds
        Track(start_time_str="01:10:00", artist="A", title="T4"), # Exceeds bounds significantly
    ]

    # Duration is 10 minutes (600 seconds).
    diags = validate_timestamps(tracks, 600.0)
    assert len(diags) == 2

    assert diags[0].track_index == 3
    assert "15:30" in diags[0].message
    assert "10:00" in diags[0].message  # Should formatted duration 10:00

    assert diags[1].track_index == 4
    assert "01:10:00" in diags[1].message
    assert "10:00" in diags[1].message


def test_validate_timestamps_grace_period():
    from ytcue.core.diagnostics import validate_timestamps
    from ytcue.core.models import Track

    tracks = [
        Track(start_time_str="10:04", artist="A", title="T1"), # Within grace
        Track(start_time_str="10:06", artist="A", title="T2"), # Outside grace
    ]

    # Duration is 10:00 (600 seconds). Grace is 5 seconds.
    diags = validate_timestamps(tracks, 600.0)
    assert len(diags) == 1
    assert diags[0].track_index == 2

