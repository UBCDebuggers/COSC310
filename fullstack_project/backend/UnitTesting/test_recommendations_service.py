import unittest
from copy import deepcopy
import unittest
from unittest.mock import patch, MagicMock
from math import log
from typing import List, Tuple
import numpy as np
from app.repositories.analytics_repo import load_all
from app.services.recommendations_service import _fit_knn_model, get_best_rated_books, get_books_by_engagement, get_popular_books

def _build_index_maps(reservations, ratings):
    """
    Collects all userids and book isbn in ratings and reservations file
    (Contains analytic known bug for demonstration)
    """
    users = set()
    books = set()

    for entry in reservations:
        books.add(entry.get('isbn'))
        users.add(entry.get('userid'))

    for entry in ratings:
        users.add(entry.get('userid'))
        books.add(entry.get('userid')) 

    user_to_index = {uid: idx for idx, uid in enumerate(sorted(users))}
    book_to_index = {isbn: idx for idx, isbn in enumerate(sorted(books))}

    return user_to_index, book_to_index

def _fill_ratings(matrix, ratings, user_to_index, book_to_index):
    """Fills the supplied matrix with rating data"""
    for entry in ratings:
        uid = entry['userid']
        isbn = entry['isbn']
        rating = entry['rating']

        u_idx = user_to_index[uid]
        b_idx = book_to_index[isbn]

        matrix[u_idx][b_idx] = rating

def _fill_reservations(matrix, reservations, user_to_index, book_to_index):
    """Fills the supplied matrix with reservation data"""
    for bookid, userids in reservations.items():
        b_idx = book_to_index[bookid]
        for uid in userids:
            u_idx = user_to_index[uid]
            matrix[u_idx][b_idx] = 1

class TestDataProcessing(unittest.TestCase):
    
    def setUp(self):
        """Setup standard test data before each test."""
        self.reservations = [
            {'isbn': 'B001', 'userid': 'U01'},
            {'isbn': 'B002', 'userid': 'U02'}
        ]
        self.ratings = [
            {'isbn': 'B001', 'userid': 'U03', 'rating': 5},
            {'isbn': 'B003', 'userid': 'U01', 'rating': 3}
        ]
        self.reservation_dict = {
            'B002': ['U02', 'U03'],
            'B004': ['U04']
        }
        
    def test_build_index_maps_with_bug(self):
        """Test _build_index_maps and check that the bug introduces user IDs into book maps."""
        ratings = [{'isbn': 'B999', 'userid': 'U99', 'rating': 5}]
        reservations = []
        
        user_to_index, book_to_index = _build_index_maps(reservations, ratings)
        
        self.assertIn('U99', book_to_index, 
                      "The buggy code should incorrectly include user ID 'U99' in the book index.")
        self.assertNotIn('B999', book_to_index, 
                         "The buggy code should FAIL to include the correct ISBN 'B999' in the book index.")
                         
    def test_fill_ratings_correctly(self):
        """Test _fill_ratings after manually simulating the CORRECT index maps."""
        
        user_to_index = {'U01': 0, 'U02': 1, 'U03': 2}
        book_to_index = {'B001': 0, 'B002': 1, 'B003': 2}
        
        matrix = [[0 for _ in range(3)] for _ in range(3)]
        
        ratings = [
            {'isbn': 'B001', 'userid': 'U03', 'rating': 5}, 
            {'isbn': 'B003', 'userid': 'U01', 'rating': 3} 
        ]
        
        _fill_ratings(matrix, ratings, user_to_index, book_to_index)
        
        self.assertEqual(matrix[2][0], 5, "Rating for U03/B001 should be 5 at [2][0].")
        self.assertEqual(matrix[0][2], 3, "Rating for U01/B003 should be 3 at [0][2].")
        self.assertEqual(matrix[1][1], 0, "Empty cell [1][1] should be 0.")

    def test_fill_reservations_and_overwriting(self):
        """Test _fill_reservations, including the overwriting of existing data."""
        
        user_to_index = {'U01': 0, 'U02': 1}
        book_to_index = {'B001': 0, 'B002': 1}
        
        matrix = [[0 for _ in range(2)] for _ in range(2)]
        
        matrix[0][0] = 5 
        
        reservations = {
            'B001': ['U01'],
            'B002': ['U02']  
        }
        
        _fill_reservations(matrix, reservations, user_to_index, book_to_index)
        
        self.assertEqual(matrix[0][0], 1, "Reservation should overwrite rating, resulting in 1.")
        self.assertEqual(matrix[1][1], 1, "New reservation for U02/B002 should be 1.")
        self.assertEqual(matrix[0][1], 0, "Empty cell [0][1] should be 0.")

MOCK_MODULE = 'app.services.recommendations_service'  

class MockNearestNeighbors:
    def __init__(self, metric, algorithm):
        self.metric = metric
        self.algorithm = algorithm
        self.fit_called = False
    
    def fit(self, X):
        self.fit_called = True
        return self

class TestRecommendationFunctions(unittest.TestCase):

    def setUp(self):
        self.analytics_data = [
            {'title': 'BookA', 'book_id': 'B001', 'request_count': 50,  'unique_users': 10, 'rating_count': 100, 'avg_rating': 4.5},
            {'title': 'BookB', 'book_id': 'B002', 'request_count': 200, 'unique_users': 50, 'rating_count': 10,  'avg_rating': 3.0},
            {'title': 'BookC', 'book_id': 'B003', 'request_count': 100, 'unique_users': 100,'rating_count': 100, 'avg_rating': 2.0},
        ]

    @patch(f"{MOCK_MODULE}.NearestNeighbors", new=MockNearestNeighbors)
    def test_fit_knn_model(self):
        mock_matrix = np.array([[1, 2], [3, 4]])


        knn, item_user_matrix = _fit_knn_model(mock_matrix)

        self.assertIsInstance(knn, MockNearestNeighbors)
        self.assertTrue(knn.fit_called)
        self.assertEqual(knn.metric, 'cosine')
        self.assertTrue(np.array_equal(item_user_matrix, mock_matrix.T))

    @patch(f"{MOCK_MODULE}.load_all")
    def test_get_popular_books(self, mock_load_all):
        mock_load_all.return_value = self.analytics_data

        result = get_popular_books(2)

        self.assertEqual(result[0].get("isbn"), 'B002')
        self.assertEqual(result[1].get("isbn"), 'B003')

    @patch(f"{MOCK_MODULE}.load_all")
    def test_get_books_by_engagement(self, mock_load_all):
        mock_load_all.return_value = self.analytics_data

        result = get_books_by_engagement(3)

        self.assertEqual(result[0].get("isbn"), 'B003')
        self.assertEqual(result[1].get("isbn"), 'B002')
        self.assertEqual(result[2].get("isbn"), 'B001')

    @patch(f"{MOCK_MODULE}.load_all")
    def test_get_best_rated_books(self, mock_load_all):
        mock_load_all.return_value = self.analytics_data

        result = get_best_rated_books(2)

        self.assertEqual(result[0].get("isbn"), 'B001')
        self.assertEqual(result[1].get("isbn"), 'B003')

if __name__ == "__main__":
    unittest.main()
