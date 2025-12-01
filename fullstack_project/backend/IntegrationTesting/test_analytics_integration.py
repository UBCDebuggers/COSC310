import csv
from datetime import datetime as real_datetime
from unittest.mock import patch
import pytest
from app.repositories import analytics_repo, ratings_repo
from app.services import analytics_service, ratings_service

@pytest.fixture
def analytics_paths(tmp_path, monkeypatch):
    analytics_path = tmp_path / "analytics.csv"
    ratings_path = tmp_path / "ratings.csv"

    monkeypatch.setattr(analytics_repo, "DATA_PATH", analytics_path)
    monkeypatch.setattr(ratings_repo, "DATA_PATH", ratings_path)

    return analytics_path, ratings_path


@pytest.fixture
def sample_books(monkeypatch):

    books = [
        {"isbn": "ISBN-001", "title": "Integration Testing 101"},
        {"isbn": "ISBN-002", "title": "Advanced Integration"},
    ]

    monkeypatch.setattr(
        "app.repositories.books_repo.load_all",
        lambda: books
    )

    return books

@pytest.fixture
def fixed_today(monkeypatch):
    class FixedDatetime:
        @staticmethod
        def now():
            return real_datetime(2024, 5, 1, 0, 0, 0)

    monkeypatch.setattr(analytics_service, "datetime", FixedDatetime)
    return "2024-05-01"

# reads the analytics.csv file and returns its rows as a list of dictionaries.
def _read_analytics_csv(path):
    with path.open("r", encoding="utf-8", newline="") as f: 
        return list(csv.DictReader(f))


@patch("app.services.analytics_service.get_ratings_summary")
@patch("app.services.analytics_service.get_unique_users_by_isbn")
def test_rebuild_analytics_creates_expected_rows(mock_unique_users, mock_summary, analytics_paths, sample_books, fixed_today):
    analytics_path, ratings_path = analytics_paths

    mock_summary.return_value = {
        "ISBN-001": {"count": 2, "avg": 4.0},
        "ISBN-002": {"count": 1, "avg": 4.0},
    }

    mock_unique_users.return_value = {
        "ISBN-001": [],
        "ISBN-002": [],
    }

    analytics_service.rebuild_analytics()

    rows = _read_analytics_csv(analytics_path)
    assert len(rows) == 2

    first, second = rows

    assert first["book_id"] == "ISBN-001"
    assert first["rating_count"] == "2"
    assert first["avg_rating"] == "4.0"

    assert second["book_id"] == "ISBN-002"
    assert second["rating_count"] == "1"
    assert second["avg_rating"] == "4.0"


@patch("app.services.analytics_service.get_ratings_summary")
@patch("app.services.analytics_service.get_unique_users_by_isbn")
def test_rebuild_analytics_overwrites_stale_data(mock_unique_users, mock_summary, analytics_paths, sample_books, fixed_today):
    analytics_path, ratings_path = analytics_paths

    mock_summary.return_value = {
        "ISBN-001": {"count": 0, "avg": 0},
        "ISBN-002": {"count": 1, "avg": 2.0},
    }

    mock_unique_users.return_value = {
        "ISBN-001": [],
        "ISBN-002": [],
    }

    analytics_service.rebuild_analytics()

    rows = _read_analytics_csv(analytics_path)

    no_ratings_row = next(r for r in rows if r["book_id"] == "ISBN-001")
    assert no_ratings_row["rating_count"] == "0"
    assert no_ratings_row["avg_rating"] == "0"

    rated_row = next(r for r in rows if r["book_id"] == "ISBN-002")
    assert rated_row["rating_count"] == "1"
    assert rated_row["avg_rating"] == "2.0"
