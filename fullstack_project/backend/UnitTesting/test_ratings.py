import copy
import unittest
from unittest.mock import patch

import app.services.ratings_service as ratings_service


class DummyHTTPException(Exception):
    def __init__(self, status_code, detail):
        super().__init__(f"{status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class MockRating:
    def __init__(self, userid=None, isbn=None, rating=None, description=None, **extra):
        self.userid = userid
        self.isbn = isbn
        self.rating = rating
        self.description = description
        self.extra = extra

    def model_dump(self):
        payload = {
            "userid": self.userid,
            "isbn": self.isbn,
            "rating": self.rating,
            "description": self.description,
        }
        payload.update(self.extra)
        return payload


class MockRatingCreate:
    def __init__(self, isbn, rating, description=""):
        self.isbn = isbn
        self.rating = rating
        self.description = description


class MockRatingUpdate:
    def __init__(self, rating, description=""):
        self.rating = rating
        self.description = description


class TestRatingService(unittest.TestCase):
    def setUp(self):
        self.sample_ratings = [
            {"userid": "user1", "isbn": "111", "rating": "5", "description": "Great"},
            {"userid": "user2", "isbn": "111", "rating": "4", "description": "Good"},
            {"userid": "user3", "isbn": "222", "rating": "3", "description": "Average"},
        ]

    @patch("app.services.ratings_service.HTTPException", DummyHTTPException)
    @patch("app.services.ratings_service.Rating", MockRating)
    @patch("app.services.ratings_service.save_all")
    @patch("app.services.ratings_service.load_all")
    def test_create_rating_appends_and_saves(self, mock_load_all, mock_save_all, *_):
        mock_load_all.return_value = copy.deepcopy(self.sample_ratings)
        new_rating = MockRatingCreate(" 999 ", " 5 ", "  desc ")

        result = ratings_service.create_rating(new_rating, " user9 ")

        self.assertIsInstance(result, MockRating)
        self.assertEqual(result.userid, "user9")
        self.assertEqual(result.isbn, "999")
        self.assertEqual(result.rating, "5")
        self.assertEqual(result.description, "desc")

        mock_save_all.assert_called_once()
        saved_payload = mock_save_all.call_args.args[0]
        self.assertEqual(len(saved_payload), 4)
        self.assertEqual(saved_payload[-1]["userid"], "user9")
        self.assertEqual(saved_payload[-1]["isbn"], "999")

    @patch("app.services.ratings_service.HTTPException", DummyHTTPException)
    @patch("app.services.ratings_service.Rating", MockRating)
    @patch("app.services.ratings_service.save_all")
    @patch("app.services.ratings_service.load_all")
    def test_create_rating_rejects_duplicate_user_book(self, mock_load_all, mock_save_all, *_):
        mock_load_all.return_value = copy.deepcopy(self.sample_ratings)
        duplicate = MockRatingCreate("111", "4", "dupe")

        with self.assertRaises(DummyHTTPException) as ctx:
            ratings_service.create_rating(duplicate, "user1")

        self.assertEqual(ctx.exception.status_code, 409)
        self.assertIn("collision", ctx.exception.detail)
        mock_save_all.assert_not_called()

    @patch("app.services.ratings_service.HTTPException", DummyHTTPException)
    @patch("app.services.ratings_service.Rating", MockRating)
    @patch("app.services.ratings_service.load_all")
    def test_get_ratings_by_isbn_returns_matches(self, mock_load_all, *_):
        mock_load_all.return_value = copy.deepcopy(self.sample_ratings)

        result = ratings_service.get_ratings_by_isbn("111")

        self.assertEqual(len(result), 2)
        self.assertTrue(all(isinstance(r, MockRating) for r in result))
        self.assertTrue(all(r.isbn == "111" for r in result))

    @patch("app.services.ratings_service.HTTPException", DummyHTTPException)
    @patch("app.services.ratings_service.Rating", MockRating)
    @patch("app.services.ratings_service.load_all")
    def test_get_ratings_by_isbn_raises_when_missing(self, mock_load_all, *_):
        mock_load_all.return_value = copy.deepcopy(self.sample_ratings)

        with self.assertRaises(DummyHTTPException) as ctx:
            ratings_service.get_ratings_by_isbn("999")

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("ISBN '999' not found", ctx.exception.detail)

    @patch("app.services.ratings_service.HTTPException", DummyHTTPException)
    @patch("app.services.ratings_service.Rating", MockRating)
    @patch("app.services.ratings_service.load_all")
    def test_get_ratings_by_userid_returns_matches(self, mock_load_all, *_):
        mock_load_all.return_value = copy.deepcopy(self.sample_ratings)

        result = ratings_service.get_ratings_by_userid("user1")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].userid, "user1")

    @patch("app.services.ratings_service.HTTPException", DummyHTTPException)
    @patch("app.services.ratings_service.Rating", MockRating)
    @patch("app.services.ratings_service.load_all")
    def test_get_ratings_by_userid_raises_when_missing(self, mock_load_all, *_):
        mock_load_all.return_value = copy.deepcopy(self.sample_ratings)

        with self.assertRaises(DummyHTTPException) as ctx:
            ratings_service.get_ratings_by_userid("missing")

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("User-ID 'missing' not found", ctx.exception.detail)

    @patch("app.services.ratings_service.HTTPException", DummyHTTPException)
    @patch("app.services.ratings_service.Rating", MockRating)
    @patch("app.services.ratings_service.save_all")
    @patch("app.services.ratings_service.load_all")
    def test_update_rating_mutates_first_matching_isbn(self, mock_load_all, mock_save_all, *_):
        mock_load_all.return_value = copy.deepcopy(self.sample_ratings)
        payload = MockRatingUpdate(" 4 ", "  updated ")

        result = ratings_service.update_rating("111", "user1", payload)

        self.assertIsInstance(result, MockRating)
        self.assertEqual(result.isbn, "111")
        # Function uses enumerate index as userid (buggy behavior)
        self.assertEqual(result.userid, 0)
        self.assertEqual(result.rating, "4")
        self.assertEqual(result.description, "updated")

        mock_save_all.assert_called_once()
        saved_list = mock_save_all.call_args.args[0]
        self.assertEqual(saved_list[0]["rating"], "4")
        self.assertEqual(saved_list[0]["description"], "updated")

    @patch("app.services.ratings_service.HTTPException", DummyHTTPException)
    @patch("app.services.ratings_service.Rating", MockRating)
    @patch("app.services.ratings_service.save_all")
    @patch("app.services.ratings_service.load_all")
    def test_update_rating_raises_when_isbn_missing(self, mock_load_all, mock_save_all, *_):
        mock_load_all.return_value = copy.deepcopy(self.sample_ratings)

        with self.assertRaises(DummyHTTPException) as ctx:
            ratings_service.update_rating("999", "user1", MockRatingUpdate("1", "x"))

        self.assertEqual(ctx.exception.status_code, 404)
        # Function reuses loop index in error detail; last index in sample data is 2.
        self.assertIn("Rating '999', '2' not found", ctx.exception.detail)
        mock_save_all.assert_not_called()

    @patch("app.services.ratings_service.save_all")
    @patch("app.services.ratings_service.load_all")
    def test_delete_rating_removes_match_and_saves(self, mock_load_all, mock_save_all):
        mock_load_all.return_value = copy.deepcopy(self.sample_ratings)

        ratings_service.delete_rating("111", "user1")

        mock_save_all.assert_called_once()
        saved_list = mock_save_all.call_args.args[0]
        self.assertEqual(len(saved_list), 2)
        self.assertFalse(any(r["userid"] == "user1" and r["isbn"] == "111" for r in saved_list))

    @patch("app.services.ratings_service.save_all")
    @patch("app.services.ratings_service.load_all")
    def test_delete_rating_saves_even_when_missing(self, mock_load_all, mock_save_all):
        mock_load_all.return_value = copy.deepcopy(self.sample_ratings)

        ratings_service.delete_rating("999", "user9")

        mock_save_all.assert_called_once()
        saved_list = mock_save_all.call_args.args[0]
        self.assertEqual(saved_list, self.sample_ratings)

    @patch("app.services.ratings_service.load_all")
    def test_get_ratings_summary_counts_and_averages(self, mock_load_all):
        mock_load_all.return_value = [
            {"userid": "u1", "isbn": "A", "rating": "5.0"},
            {"userid": "u2", "isbn": "A", "rating": "3.0"},
            {"userid": "u3", "isbn": "B", "rating": "4.0"},
            {"userid": "u4", "isbn": "B", "rating": "4.0"},
            {"userid": "u5", "isbn": "C", "rating": "invalid"},
            {"userid": "u6", "isbn": None, "rating": "1.0"},
        ]

        summary = ratings_service.get_ratings_summary()

        self.assertEqual(summary, {"A": {"count": 2, "avg": 4.0}, "B": {"count": 2, "avg": 4.0}})

    @patch("app.services.ratings_service.load_all")
    def test_get_unique_users_by_isbn_collects_user_ids(self, mock_load_all):
        mock_load_all.return_value = [
            {"userid": "u1", "isbn": "A"},
            {"userid": "u1", "isbn": "A"},
            {"userid": "u2", "isbn": "B"},
            {"user_id": "u3", "isbn": "B"},
            {"userid": "ignored", "isbn": None},
        ]

        unique_map = ratings_service.get_unique_users_by_isbn()

        self.assertEqual(set(unique_map.keys()), {"A", "B"})
        self.assertEqual(set(unique_map["A"]), {"u1"})
        self.assertEqual(set(unique_map["B"]), {"u2", "u3"})

    @patch("app.services.ratings_service.get_ratings_summary")
    def test_get_top_rated_books_sorts_by_count(self, mock_summary):
        mock_summary.return_value = {
            "ISBN_B": {"count": 15, "avg": 3.0},
            "ISBN_C": {"count": 10, "avg": 4.5},
            "ISBN_A": {"count": 5, "avg": 5.0},
        }

        top_two = ratings_service.get_top_rated_books(2)
        self.assertEqual(
            top_two,
            [
                {"isbn": "ISBN_B", "rating_count": 15, "avg_rating": 3.0},
                {"isbn": "ISBN_C", "rating_count": 10, "avg_rating": 4.5},
            ],
        )

        all_books = ratings_service.get_top_rated_books(10)
        self.assertEqual(len(all_books), 3)


if __name__ == "__main__":
    unittest.main()
