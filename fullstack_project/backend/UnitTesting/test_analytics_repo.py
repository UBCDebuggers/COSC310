import csv
from pathlib import Path
import pytest
from app.repositories import analytics_repo


@pytest.fixture
def analytics_csv_path(tmp_path, monkeypatch):
    """Provide a temp CSV path and patch the repository to use it."""
    data_path = tmp_path / "analytics.csv"
    monkeypatch.setattr(analytics_repo, "DATA_PATH", data_path)
    # every test uses its own fake CSV file, NOT the real one. As this prevents overwriting real analytics data 
    # and also ensures tests dont interfere with each other.
    return data_path

def test_load_all_returns_empty_when_file_missing(analytics_csv_path):
#If the CSV file does not exist, load_all() should return an empty list.
    assert analytics_repo.load_all() == []
    


def test_load_all_reads_existing_rows(analytics_csv_path: Path):
    rows = [
        {"book_id": "123", "title": "Some Book", "total_borrows": "5"},
        {"book_id": "456", "title": "Another Book", "total_borrows": "2"},
    ]
    #We want full control over the input data, so we use the temporary path, and assign our own row values .

    with analytics_csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    # Asserts the returned data matches exactly the rows we wrote above
    assert analytics_repo.load_all() == rows


def test_save_all_writes_header_and_rows(analytics_csv_path: Path):
    rows = [
        {"book_id": "111", "title": "First", "total_borrows": "7"},
        {"book_id": "222", "title": "Second", "total_borrows": "3"},
    ]

    analytics_repo.save_all(rows)
    #save_all() should create a new CSV file.

    with analytics_csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        # csv.DictReader preserves the original order of the fieldnames
        assert reader.fieldnames == list(rows[0].keys()) # the first row should be the header, so we check .
        assert list(reader) == rows # here we read all the rows and convert them into a list of dictionaries and then compare them ot the rows ( test data ).


def test_save_all_unlinks_file_when_no_rows(analytics_csv_path: Path):
    analytics_csv_path.write_text("stale data", encoding="utf-8")
    assert analytics_csv_path.exists()

    analytics_repo.save_all([]) # deleting the file, as the csv is empty .

    assert not analytics_csv_path.exists()
