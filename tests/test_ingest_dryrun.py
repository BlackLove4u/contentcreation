import subprocess


def test_ingest_dry_run():
    """Run ingest_uploads.py in dry-run mode and assert it reports actions."""
    cmd = ["python3", "content-system/system/ingest_uploads.py", "--dry-run", "--verbose"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout + proc.stderr
    # Expect to see at least one of the file-type markers
    assert "Text:" in out or "Audio:" in out or "Video:" in out
