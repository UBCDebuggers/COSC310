import csv
from pathlib import Path

from app.repositories import ratings_repo


def test_load_all_returns_empty_when_missing(tmp_path, monkeypatch):
    temp_file = tmp_path / "ratings.csv"
    monkeypatch.setattr(ratings_repo, "DATA_PATH", temp_file)

    assert ratings_repo.load_all() == []


def test_load_all_reads_existing_rows(tmp_path, monkeypatch):
    temp_file = tmp_path / "ratings.csv"
    monkeypatch.setattr(ratings_repo, "DATA_PATH", temp_file)

    rows = [
        {"isbn": "123", "rating": "5"},
        {"isbn": "456", "rating": "3"},
    ]

    with temp_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    assert ratings_repo.load_all() == rows


def test_save_all_writes_rows_correctly(tmp_path, monkeypatch):
    temp_file = tmp_path / "ratings.csv"
    monkeypatch.setattr(ratings_repo, "DATA_PATH", temp_file)

    rows = [
        {"isbn": "111", "rating": "4"},
        {"isbn": "222", "rating": "2"},
    ]

    ratings_repo.save_all(rows)

    with temp_file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert list(reader) == rows


def test_save_all_removes_file_when_empty(tmp_path, monkeypatch):
    temp_file = tmp_path / "ratings.csv"
    temp_file.write_text("stale data")
    monkeypatch.setattr(ratings_repo, "DATA_PATH", temp_file)

    ratings_repo.save_all([])

    assert not temp_file.exists()
