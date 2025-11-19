import csv
from pathlib import Path

from app.repositories import analytics_repo


def test_load_all_returns_empty_if_file_missing(tmp_path, monkeypatch):
    # patch DATA_PATH to temporary path
    temp_file = tmp_path / "analytics.csv"
    monkeypatch.setattr(analytics_repo, "DATA_PATH", temp_file)

    assert analytics_repo.load_all() == []


def test_save_all_writes_rows_correctly(tmp_path, monkeypatch):
    temp_file = tmp_path / "analytics.csv"
    monkeypatch.setattr(analytics_repo, "DATA_PATH", temp_file)

    rows_to_write = [
        {"book_id": "A1", "total_borrows": "10"},
        {"book_id": "A2", "total_borrows": "5"}
    ]

    analytics_repo.save_all(rows_to_write)

    # read file manually to verify correctness
    with temp_file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        read_rows = list(reader)

    assert read_rows == rows_to_write


def test_save_all_removes_file_when_empty(tmp_path, monkeypatch):
    temp_file = tmp_path / "analytics.csv"
    temp_file.touch()  # create empty file
    monkeypatch.setattr(analytics_repo, "DATA_PATH", temp_file)

    # call save_all with empty list
    analytics_repo.save_all([])

    assert not temp_file.exists()
