"""Test --dry-run --explain CLI mode."""

import subprocess
import sys
import tempfile
from pathlib import Path


def test_dry_run_explain_help():
    """Verify --dry-run and --explain options appear in help."""
    result = subprocess.run(
        [sys.executable, "library_pipeline/cli.py", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert "--dry-run" in result.stdout, "Missing --dry-run in help"
    assert "--explain" in result.stdout, "Missing --explain in help"
    print("✓ --dry-run and --explain options present in help")


def test_dry_run_requires_file():
    """Verify --dry-run without --file produces error."""
    result = subprocess.run(
        [sys.executable, "library_pipeline/cli.py", "--dry-run"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode != 0, "Should fail when --dry-run without --file"
    assert "requires --file" in result.stderr, "Error message should mention --file requirement"
    print("✓ --dry-run correctly requires --file")


def test_dry_run_file_not_found():
    """Verify --dry-run with nonexistent file produces error."""
    result = subprocess.run(
        [sys.executable, "library_pipeline/cli.py", "--dry-run", "--file", "/tmp/nonexistent_xyz.pdf"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode != 0, "Should fail for nonexistent file"
    assert "not found" in result.stderr, "Error message should mention file not found"
    print("✓ --dry-run correctly handles missing files")


if __name__ == "__main__":
    test_dry_run_explain_help()
    test_dry_run_requires_file()
    test_dry_run_file_not_found()
    print("\n✓ All dry-run/explain tests passed")
