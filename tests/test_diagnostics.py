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
