from pathlib import Path

from ytcue.core.metadata import gather_audio_files


def test_gather_audio_files(tmp_path):
    """
    Test that gather_audio_files correctly collects missing CUE files
    from a mix of individual files and directories.
    """
    # Create a mock directory structure
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir2").mkdir()

    f1 = tmp_path / "track1.mp3"
    f1.touch()

    f2 = tmp_path / "dir1" / "track2.flac"
    f2.touch()

    f3 = tmp_path / "dir2" / "track3.m4a"
    f3.touch()

    # Existing CUE file (should be ignored)
    f4 = tmp_path / "dir2" / "track4.mp3"
    f4.touch()
    (tmp_path / "dir2" / "track4.cue").touch()

    # Non-audio file
    f5 = tmp_path / "readme.txt"
    f5.touch()

    # 1. Gather from individual file
    collected = gather_audio_files([f1])
    assert collected == [f1]

    # 2. Gather from directory (non-recursive)
    collected = gather_audio_files([tmp_path])
    assert collected == [f1]  # Only f1 is in Root

    # 3. Gather from mix (non-recursive)
    collected = gather_audio_files([f1, tmp_path / "dir1"])
    assert collected == sorted([f1, f2])

    # 4. Gather recursive
    collected = gather_audio_files([tmp_path], recursive=True)
    assert collected == sorted([f1, f2, f3])  # track4 ignored because it has a cue

    # 5. Handle duplicates
    collected = gather_audio_files([f1, f1, tmp_path], recursive=True)
    assert collected == sorted([f1, f2, f3])


def test_gather_audio_files_with_invalid_paths():
    """Test that invalid paths are ignored gracefully."""
    collected = gather_audio_files([Path("non_existent_file.mp3")])
    assert collected == []
