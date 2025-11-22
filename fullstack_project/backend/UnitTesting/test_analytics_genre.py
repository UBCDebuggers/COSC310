import pytest
from unittest.mock import patch

from app.services.analytics_service import (
    _map_isbn_to_genres,
    _aggregate_genre_counts,
    get_genre_popularity
)


# Test: _map_isbn_to_genres
def test_map_isbn_to_genres_creates_correct_mapping():
    books = [
        {"isbn": "111", "genres": ["Fantasy", "Adventure"]},
        {"isbn": "222", "genres": ["Romance"]},
        {"isbn": "333", "genres": []},
    ]

    result = _map_isbn_to_genres(books)

    assert result == {
        "111": ["Fantasy", "Adventure"],
        "222": ["Romance"],
        "333": []
    }



# Test: _aggregate_genre_counts
def test_aggregate_genre_counts_sums_ratings_correctly():
    records = [
        {"book_id": "111", "rating_count": "3"},
        {"book_id": "111", "rating_count": "2"},
        {"book_id": "222", "rating_count": "5"},
    ]

    isbn_to_genres = {
        "111": ["Fantasy"],
        "222": ["Romance"]
    }

    result = _aggregate_genre_counts(records, isbn_to_genres)

    assert result == {
        "Fantasy": 5,  
        "Romance": 5
    }

# Test: get_genre_popularity
# Integration-lite test
@patch("app.services.analytics_service.books_repo.load_all")
@patch("app.services.analytics_service.analytics_repo.load_all")
def test_get_genre_popularity_returns_sorted_list(mock_records, mock_books):

    mock_books.return_value = [
        {"isbn": "111", "genres": ["Fantasy"]},
        {"isbn": "222", "genres": ["Romance"]},
    ]

    mock_records.return_value = [
        {"book_id": "111", "rating_count": "10"},
        {"book_id": "222", "rating_count": "5"},
    ]

    result = get_genre_popularity()

    assert len(result) == 2

    assert result[0]["genre"] == "Fantasy"
    assert result[0]["total_rating_count"] == 10

    assert result[1]["genre"] == "Romance"
    assert result[1]["total_rating_count"] == 5
