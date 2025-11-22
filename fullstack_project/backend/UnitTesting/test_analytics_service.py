import unittest
from unittest.mock import patch, MagicMock

from app.services.analytics_service import (
    get_genre_popularity,
    get_top_rated_books,
    get_trending_books,
)

class TestAnalyticsService(unittest.TestCase):

    @patch("app.services.analytics_service.books_repo")
    @patch("app.services.analytics_service.analytics_repo")
    @patch("app.services.analytics_service.ratings_repo")
    @patch("app.services.analytics_service.get_ratings_summary")
    @patch("app.services.analytics_service.get_unique_users_by_isbn")
    def test_genre_popularity(
        self,
        mock_users,
        mock_summary,
        mock_ratings,
        mock_analytics,
        mock_books
    ):

        # --- Fake book metadata ---
        mock_books.load_all.return_value = [
            {"isbn": "9780590353403", "genres": ["Fantasy"]},
            {"isbn": "9780439420873", "genres": ["Mystery", "Thriller"]},
        ]

        # --- Fake analytics rows ---
        mock_analytics.load_all.return_value = [
            {"book_id": "9780590353403", "rating_count": "3"},
            {"book_id": "9780439420873", "rating_count": "5"},
        ]

        result = get_genre_popularity()

        expected = [
            {"genre": "Mystery", "total_rating_count": 5},
            {"genre": "Thriller", "total_rating_count": 5},
            {"genre": "Fantasy", "total_rating_count": 3},
        ]

        self.assertEqual(result, expected)

    # ------------------------------------------------------------

    @patch("app.services.analytics_service.get_ratings_summary")
    def test_top_rated_books(self, mock_summary):

        mock_summary.return_value = {
            "111": {"count": 5, "avg": 4.2},
            "222": {"count": 2, "avg": 3.8},
            "333": {"count": 7, "avg": 4.9},
        }

        result = get_top_rated_books(2)

        expected = [
            {"isbn": "333", "rating_count": 7, "avg_rating": 4.9},
            {"isbn": "111", "rating_count": 5, "avg_rating": 4.2},
        ]

        self.assertEqual(result, expected)

    # ------------------------------------------------------------

    @patch("app.services.analytics_service.analytics_repo")
    def test_trending_books(self, mock_analytics):

        mock_analytics.load_all.return_value = [
            {"book_id": "111", "date": "2025-01-03", "request_count": "8"},
            {"book_id": "111", "date": "2025-01-02", "request_count": "3"},
            {"book_id": "222", "date": "2025-01-03", "request_count": "1"},
            {"book_id": "222", "date": "2025-01-02", "request_count": "1"},
        ]

        result = get_trending_books(2)

        expected = [
            {
                "book_id": "111",
                "total_requests": 11,
                "delta_requests": 5
            },
            {
                "book_id": "222",
                "total_requests": 2,
                "delta_requests": 0
            }
        ]

        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
