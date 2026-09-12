from basic_chan import ChanReporter
from basic_chan.snapshots.engine import SnapshotEngine


def test_reporter_outputs(tmp_path):
    reporter = ChanReporter(chan_name="Test-chan", output_dir=tmp_path)

    # Markdown
    md_file = reporter.export_report(
        title="Audit Report",
        summary="Audit completed cleanly.",
        headers=["Category", "Count"],
        rows=[["Auth", 0], ["Injection", 0]],
        format_type="markdown",
    )
    assert md_file.exists()
    assert "# Audit Report" in md_file.read_text(encoding="utf-8")

    # HTML
    html_file = reporter.export_report(
        title="Audit Report",
        summary="Audit completed cleanly.",
        headers=["Category", "Count"],
        rows=[["Auth", 0]],
        format_type="html",
    )
    assert html_file.exists()
    assert "<!DOCTYPE html>" in html_file.read_text(encoding="utf-8")

    # JSON
    json_file = reporter.export_report(
        title="Audit Report",
        summary="Audit completed cleanly.",
        headers=["Category"],
        rows=[["Auth"]],
        format_type="json",
    )
    assert json_file.exists()


def test_snapshot_engine(tmp_path):
    engine = SnapshotEngine(storage_dir=tmp_path / ".snapshots")
    snap_path = engine.record_snapshot("scan", {"findings": 5})
    assert snap_path.exists()

    latest = engine.get_latest("scan")
    assert latest is not None
    assert latest["payload"]["findings"] == 5
