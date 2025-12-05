import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from fastapi import HTTPException

from app.services import recommendations_service
from app.services.recommendations_service import (
    get_recommender,
    get_similar_books,
    recommend_for_user
)

MOCK_MODULE = "app.services.recommendations_service"


class MockKNN:
    def __init__(self):
        self.kneighbors_called = None
        self.distances = np.array([[0.1, 0.2, 0.3]])
        self.indices = np.array([[1, 5, 7]])

    def kneighbors(self, X, n_neighbors):
        self.kneighbors_called = (X, n_neighbors)
        return self.distances, self.indices


class TestRecommenderSystem(unittest.TestCase):

    def tearDown(self):
        if hasattr(recommendations_service.get_recommender, "model"):
            del recommendations_service.get_recommender.model

    @patch(f"{MOCK_MODULE}._fit_knn_model")
    @patch(f"{MOCK_MODULE}._build_user_book_matrix")
    def test_get_recommender_initializes_once(self, mock_build, mock_fit):
        """Ensure get_recommender only initializes the model once."""

        mock_matrix = np.array([[1, 0], [0, 1]])
        mock_user_map = {"U01": 0, "U02": 1}
        mock_book_map = {"B01": 0, "B02": 1}
        mock_knn = MockKNN()

        mock_build.return_value = (mock_matrix, mock_user_map, mock_book_map)
        mock_fit.return_value = (mock_knn, mock_matrix.T)

        knn1, items1, users1, books1 = get_recommender()
        knn2, items2, users2, books2 = get_recommender()

        self.assertIs(knn1, knn2, "KNN instance must be reused")
        self.assertEqual(mock_build.call_count, 1)
        self.assertEqual(mock_fit.call_count, 1)

    @patch(f"{MOCK_MODULE}.get_recommender")
    def test_get_similar_books_calls_knn_correctly(self, mock_get_rec):
        """Ensure nearest neighbors function is called properly."""

        mock_knn = MockKNN()

        item_user_matrix = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])

        mock_get_rec.return_value = (mock_knn, item_user_matrix, {}, {})

        result = get_similar_books(book_index=1, k=2)

        self.assertEqual(result.tolist(), [5, 7])

        X, n = mock_knn.kneighbors_called
        self.assertEqual(n, 3)
        self.assertTrue(np.array_equal(X, item_user_matrix[1].reshape(1, -1)))

    @patch(f"{MOCK_MODULE}.get_similar_books")
    @patch(f"{MOCK_MODULE}.get_recommender")
    def test_recommend_for_user_ranking(self, mock_get_rec, mock_similar):
        """Ensure correct scoring + ranking for user recommendations."""

        matrix = np.array([
        [1, 0, 1],
        [0, 0, 0]
        ])

        user_map = {"U01": 0}

        book_map = {
        "ISBN0": 0,
        "ISBN1": 1,
        "ISBN2": 2,
        "ISBN4": 4,
        "ISBN5": 5
        }

        item_user_matrix = matrix.T
        mock_knn = MockKNN()

        mock_get_rec.return_value = (mock_knn, item_user_matrix, user_map, book_map)

        mock_similar.side_effect = [
        np.array([2, 5]),  
        np.array([2, 4])  
        ]

        result = recommend_for_user("U01", N=3)

        expected = ["ISBN2", "ISBN5", "ISBN4"]
        self.assertEqual(result, expected)

    @patch(f"{MOCK_MODULE}.get_recommender")
    def test_recommend_for_user_invalid_user(self, mock_get_rec):
        """Ensure invalid user raises 404 exception."""

        matrix = np.zeros((1, 3))
        user_map = {"U01": 0}
        book_map = {}

        mock_knn = MockKNN()

        mock_get_rec.return_value = (mock_knn, matrix.T, user_map, book_map)

        with self.assertRaises(HTTPException):
            recommend_for_user("NOT FOUND")


if __name__ == "__main__":
    unittest.main()
