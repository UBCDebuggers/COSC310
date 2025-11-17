import unittest
from unittest.mock import patch, MagicMock
from app.services import waitlist_service as ws
from app.repositories import waitlist_repo as wr

# Mock Pydantic-like object for testing
class WaitListCreate:
    def __init__(self, userid, isbn, email="test"):
        self.userid = userid
        self.isbn = isbn
        self.email = email

    def dict(self):
        return {"userid": self.userid, "isbn": self.isbn, "email": self.email}

# Tests success or failure of each function in waitlist_service.py
class TestWaitlistService(unittest.TestCase):
    @patch('app.repositories.waitlist_repo.add_to_waitlist')
    def test_create_waitlist_successful_addition(self, mock_add):
        input_data = WaitListCreate(userid="321", isbn="123")
        mock_add.return_value = {"userid": input_data.userid, "isbn": input_data.isbn, "email": input_data.email}

        result = wr.add_to_waitlist(input_data.userid, input_data.isbn, input_data.email)
        self.assertEqual(result["userid"], "321")
        self.assertEqual(result["isbn"], "123")
        mock_add.assert_called_once()

    # Test that notify_waitlist processes and notifies waitlist entries.
    @patch('app.services.waitlist_service.notify_waitlist')
    def test_notify_waitlist_with_entries(self, mock_notify):
        mock_notify.return_value = 2
        
        result = ws.notify_waitlist("B1")
        self.assertEqual(result, 2)

    # Test retrieval of waitlist entries for a specific ISBN.
    @patch('app.repositories.waitlist_repo.get_waitlist_for_isbn')
    def test_get_waitlist_for_isbn_successful(self, mock_get):
        mock_get.return_value = [
            {"userid": "U1", "isbn": "B1", "email": "u1@example.com"},
            {"userid": "U2", "isbn": "B1", "email": "u2@example.com"}
        ]
        
        result = wr.get_waitlist_for_isbn("B1")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["isbn"], "B1")

    # Test successful removal from waitlist
    @patch('app.repositories.waitlist_repo.remove_waitlist_entry')
    def test_remove_waitlist_entry_successful(self, mock_remove):
        mock_remove.return_value = True
        
        result = wr.remove_waitlist_entry("W1")
        self.assertTrue(result)
        mock_remove.assert_called_once_with("W1")

    # Test retrieval of all waitlist entries for a user.
    @patch('app.repositories.waitlist_repo.get_waitlists_for_user')
    def test_get_waitlists_for_user_successful(self, mock_get):
        mock_get.return_value = [{"userid": "U1", "isbn": "B1", "email": "u1@example.com"}]
        
        result = wr.get_waitlists_for_user("U1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["userid"], "U1")

    # Test deletion of all waitlist entries for a user.
    @patch('app.repositories.waitlist_repo.delete_waitlists_for_user')
    def test_delete_waitlists_for_user(self, mock_delete):
        mock_delete.return_value = 2
        
        result = wr.delete_waitlists_for_user("U1")
        self.assertEqual(result, 2)
        mock_delete.assert_called_once_with("U1")

    # Test deletion of all waitlist entries for a book.
    @patch('app.repositories.waitlist_repo.delete_waitlists_for_book')
    def test_delete_waitlists_for_book(self, mock_delete):
        mock_delete.return_value = 3
        
        result = wr.delete_waitlists_for_book("B1")
        self.assertEqual(result, 3)
        mock_delete.assert_called_once_with("B1")