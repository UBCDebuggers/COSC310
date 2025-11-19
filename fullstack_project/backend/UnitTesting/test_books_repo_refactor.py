import csv
from pathlib import Path

from app.repositories import books_repo


def test_load_all_returns_empty_when_missing(tmp_path, monkeypatch):
    temp_file = tmp_path / "books.csv"
    monkeypatch.setattr(books_repo, "DATA_PATH", temp_file)

    assert books_repo.load_all() == []


def test_load_all_reads_existing_rows(tmp_path, monkeypatch):
    temp_file = tmp_path / "books.csv"
    monkeypatch.setattr(books_repo, "DATA_PATH", temp_file)

    rows = [
        {"isbn": "123", "title": "Book A"},
        {"isbn": "456", "title": "Book B"},
    ]

    with temp_file.open("w", encoding="latin-1", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    assert books_repo.load_all() == rows


def test_save_all_writes_rows_correctly(tmp_path, monkeypatch):
    temp_file = tmp_path / "books.csv"
    monkeypatch.setattr(books_repo, "DATA_PATH", temp_file)

    rows = [
        {"isbn": "111", "title": "Alpha"},
        {"isbn": "222", "title": "Beta"},
    ]

    books_repo.save_all(rows)

    with temp_file.open("r", encoding="latin-1", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        assert list(reader) == rows


def test_save_all_removes_file_when_empty(tmp_path, monkeypatch):
    temp_file = tmp_path / "books.csv"
    temp_file.write_text("stale data", encoding="latin-1")
    monkeypatch.setattr(books_repo, "DATA_PATH", temp_file)

    books_repo.save_all([])

    assert not temp_file.exists()
