import pytest
from unittest.mock import patch
from datetime import datetime

from app.services.analytics_service import (
    load_foundational_data,
    make_analytics_record,
    rebuild_analytics
)


# -------------------------------
# Test: load_foundational_data
# -------------------------------

@patch("app.services.analytics_service.books_repo.load_all")
@patch("app.services.analytics_service.ratings_repo.load_all")
@patch("app.services.analytics_service.users_repo.load_all")
def test_load_foundational_data(mock_users, mock_ratings, mock_books):
    # Arrange
    mock_books.return_value = [{"isbn": "1"}]
    mock_ratings.return_value = [{"isbn": "1", "rating": 5}]
    mock_users.return_value = [{"id": "u1"}]

    # Act
    books, ratings, users = load_foundational_data()

    # Assert
    assert books == [{"isbn": "1"}]
    assert ratings == [{"isbn": "1", "rating": 5}]
    assert users == [{"id": "u1"}]


# -------------------------------
# Test: make_analytics_record
# -------------------------------

def test_make_analytics_record_creates_correct_dict():
    book = {"isbn": "123", "title": "Test Book"}
    rating_summary = {"count": 4, "avg": 3.5}
    users = ["u1", "u2"]
    today = "2025-01-01"

    result = make_analytics_record(book, rating_summary, users, today)

    assert result["date"] == "2025-01-01"
    assert result["book_id"] == "123"
    assert result["title"] == "Test Book"
    assert result["request_count"] == "0"
    assert result["rating_count"] == "4"
    assert result["avg_rating"] == "3.5"
    assert result["unique_users"] == "2"


# -------------------------------
# Test: rebuild_analytics
# Integration-like test (mock repos)
# -------------------------------

@patch("app.services.analytics_service.analytics_repo.save_all")
@patch("app.services.analytics_service.get_unique_users_by_isbn")
@patch("app.services.analytics_service.get_ratings_summary")
@patch("app.services.analytics_service.load_foundational_data")
def test_rebuild_analytics_builds_records(mock_load_data, mock_rating_summary, mock_unique_users, mock_save_all):
    # Arrange
    mock_load_data.return_value = (
        [{"isbn": "111", "title": "Book A"}],  # books
        [],  # ratings
        []   # users
    )
    mock_rating_summary.return_value = {
        "111": {"count": 5, "avg": 4.0}
    }
    mock_unique_users.return_value = {
        "111": ["u1", "u2", "u3"]
    }

    # Act
    rebuild_analytics()

    # Assert analytics_repo.save_all was called with one record
    assert mock_save_all.called

    saved_records = mock_save_all.call_args[0][0]
    assert len(saved_records) == 1

    record = saved_records[0]
    assert record["book_id"] == "111"
    assert record["rating_count"] == "5"
    assert record["unique_users"] == "3"
