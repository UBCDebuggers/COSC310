import csv
from datetime import datetime as real_datetime
import pytest
from app.repositories import analytics_repo, ratings_repo
from app.services import analytics_service , ratings_service

@pytest.fixture
def analytics_paths(tmp_path, monkeypatch):

# For every test, redirect both analytics.csv and ratings.csv into a temporary folder 
# instead of touching the real files.This lets us run tests safely without messing up actual data.
    analytics_path = tmp_path / "analytics.csv"
    ratings_path = tmp_path / "ratings.csv"

# Replace the original DATA_PATH inside each repo with our temp paths
    monkeypatch.setattr(analytics_repo, "DATA_PATH", analytics_path)
    monkeypatch.setattr(ratings_repo, "DATA_PATH", ratings_path)

    return analytics_path, ratings_path


@pytest.fixture
def sample_books(monkeypatch):

    books = [
        {"isbn": "ISBN-001", "title": "Integration Testing 101"},
        {"isbn": "ISBN-002", "title": "Advanced Integration"},
    ]

    # Patch load_all() inside books_repo so analytics_service uses these fake books
    monkeypatch.setattr(
        "app.repositories.books_repo.load_all",
        lambda: books
    )

    return books


@pytest.fixture
def fixed_today(monkeypatch):
    # Force datetime.now() to always return the same date.
    # therefore making the analytics.csv rows predictable.
    class FixedDatetime:
        @staticmethod
        def now():
            return real_datetime(2024, 5, 1, 0, 0, 0)

    monkeypatch.setattr(analytics_service, "datetime", FixedDatetime)
    return "2024-05-01"

# this function writes to our file, fake ratings.csv used in tests.
def _write_ratings_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f: # open the file for writing, ensuring utf-8 encoding and no extra newlines
        writer = csv.DictWriter(f, fieldnames=["isbn", "rating", "id"])
        writer.writeheader()
        writer.writerows(rows)

# reads the analytics.csv file and returns its rows as a list of dictionaries.
def _read_analytics_csv(path):
    with path.open("r", encoding="utf-8", newline="") as f: # open the file for reading with utf-8 encoding and no extra newlines
        return list(csv.DictReader(f))


def test_rebuild_analytics_creates_expected_rows(analytics_paths, sample_books, fixed_today):
    analytics_path, ratings_path = analytics_paths
# Test that when rebuild_analytics() runs with a normal ratings file, 
# it produces exactly one analytics row per book with correctly calculated stats.
    _write_ratings_csv(
        ratings_path,
        [
            {"isbn": "ISBN-001", "rating": "5", "id": "u1"},
            {"isbn": "ISBN-001", "rating": "3", "id": "u2"},
            {"isbn": "ISBN-002", "rating": "4", "id": "u1"},
        ],
    )

    analytics_service.rebuild_analytics() # this regenerates the analytics.csv file based on the ratings above

    rows = _read_analytics_csv(analytics_path) # reads back the generated analytics.csv file
    assert len(rows) == len(sample_books) # if there is one row per book then the lengths should match

    #book 1 calc:
    first, second = rows
    assert first["book_id"] == "ISBN-001"
    assert first["title"] == "Integration Testing 101"
    assert first["date"] == fixed_today
    assert first["rating_count"] == "2" #two ratings for ISBN-001
    assert first["avg_rating"] == "4.0"# average of 5 and 3 is 4.0 ( 5+ 3 / 2 = 4.0 )
    assert first["unique_users"] == "2" # two unique users rated ISBN-001
    #book 2 calc:
    assert second["book_id"] == "ISBN-002"
    assert second["rating_count"] == "1"
    assert second["avg_rating"] == "4.0"
    assert second["unique_users"] == "1"


def test_rebuild_analytics_overwrites_stale_data(analytics_paths, sample_books, fixed_today):
    #If analytics.csv already exists and contains garbage/stale content,
    #rebuild_analytics() should completely overwrite it with fresh data.
    analytics_path, ratings_path = analytics_paths
    analytics_path.write_text("stale", encoding="utf-8")

    _write_ratings_csv(
        ratings_path,
        [
            {"isbn": "ISBN-002", "rating": "2", "id": "user-x"},
        ],
    )

    analytics_service.rebuild_analytics()

    rows = _read_analytics_csv(analytics_path)
    assert len(rows) == len(sample_books)

    # Book without ratings should default to zeros
    no_ratings_row = next(row for row in rows if row["book_id"] == "ISBN-001")
    assert no_ratings_row["rating_count"] == "0"
    assert no_ratings_row["avg_rating"] == "0"
    assert no_ratings_row["unique_users"] == "0"
    # Book with one rating should show correct stats
    rated_row = next(row for row in rows if row["book_id"] == "ISBN-002")
    assert rated_row["rating_count"] == "1"
    assert rated_row["avg_rating"] == "2.0"
    assert rated_row["unique_users"] == "1"