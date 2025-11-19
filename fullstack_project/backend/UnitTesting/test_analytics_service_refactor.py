from app.services import analytics_service
from app.repositories import analytics_repo


def test_rebuild_analytics_writes_rows(monkeypatch, tmp_path):
    # Redirect analytics.csv to a temp file so we don't touch real data
    temp_file = tmp_path / "analytics.csv"
    monkeypatch.setattr(analytics_repo, "DATA_PATH", temp_file)

    # Run analytics rebuild
    analytics_service.rebuild_analytics()

    # Confirm file was created
    assert temp_file.exists()

    # Basic check: ensure CSV is not empty
    content = temp_file.read_text(encoding="utf-8")
    assert "book_id" in content  # header present
