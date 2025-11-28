import pytest
from datetime import datetime, timezone
import csv
from pathlib import Path

from app.repositories import history_repo


@pytest.fixture
def fake_history_file(tmp_path, monkeypatch):
    """Creates an isolated temp CSV file and patches DATA_PATH."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    fake_csv = data_dir / "history.csv"
    monkeypatch.setattr(history_repo, "DATA_PATH", fake_csv)

    return fake_csv



# load_all()
def test_load_all_returns_empty_if_missing(fake_history_file):
    assert history_repo.load_all() == []


def test_load_all_parses_rows_and_dates(fake_history_file):
    fake_history_file.write_text(
        "userid;isbn;date\n"
        "u1;111;2025-01-01T00:00:00+00:00\n",
        encoding="utf-8"
    )

    items = history_repo.load_all()

    assert len(items) == 1
    assert items[0]["userid"] == "u1"
    assert items[0]["isbn"] == "111"
    assert isinstance(items[0]["date"], datetime)



# save_all()
def test_save_all_writes_valid_csv(fake_history_file):
    items = [
        {"userid": "u1", "isbn": "111", "date": datetime(2025, 1, 1, tzinfo=timezone.utc)}
    ]

    history_repo.save_all(items)

    text = fake_history_file.read_text(encoding="utf-8")
    assert "u1" in text
    assert "111" in text
    assert "2025-01-01T00:00:00+00:00" in text


def test_save_all_deletes_file_when_empty(fake_history_file):
    fake_history_file.write_text("dummy", encoding="utf-8")
    history_repo.save_all([])
    assert not fake_history_file.exists()


# add_history_item()
def test_add_history_item_appends_new_row(fake_history_file):
    result = history_repo.add_history_item("u1", "111")

    items = history_repo.load_all()

    assert len(items) == 1
    assert items[0]["userid"] == "u1"
    assert items[0]["isbn"] == "111"
    assert "T" in result["date"] 


# get_last_books()
def test_get_last_books_sorted_desc(fake_history_file):
    # Insert three records out of order
    data = (
        "userid;isbn;date\n"
        "u1;111;2025-01-02T00:00:00+00:00\n"
        "u1;222;2025-01-03T00:00:00+00:00\n"
        "u1;333;2025-01-01T00:00:00+00:00\n"
    )
    fake_history_file.write_text(data, encoding="utf-8")

    books = history_repo.get_last_books("u1", n=2)

    # Should return newest first
    assert books[0]["isbn"] == "222"
    assert books[1]["isbn"] == "111"
    assert len(books) == 2



# delete_history_item()
def test_delete_history_item_by_isbn(fake_history_file):
    data = (
        "userid;isbn;date\n"
        "u1;111;2025-01-01T00:00:00+00:00\n"
        "u1;222;2025-01-01T00:00:00+00:00\n"
    )
    fake_history_file.write_text(data, encoding="utf-8")

    result = history_repo.delete_history_item("u1", "111")

    assert result is True
    items = history_repo.load_all()
    assert len(items) == 1
    assert items[0]["isbn"] == "222"


def test_delete_history_item_returns_false_when_no_match(fake_history_file):
    fake_history_file.write_text(
        "userid;isbn;date\nu1;111;2025-01-01T00:00:00+00:00\n",
        encoding="utf-8"
    )

    result = history_repo.delete_history_item("u1", "999")  

    assert result is False
    assert len(history_repo.load_all()) == 1
