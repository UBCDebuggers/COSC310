import unittest
from unittest.mock import patch, ANY
from app.schemas.user import User, UserCreate
from app.schemas.authentication import LoginRequest
import pytest
from app.services import waitlist_service
from app.services.users_service import create_user, authenticate_user
from app.services.waitlist_service import create_waitlist, delete_specific_waitlist, get_waitlists_for_books, get_waitlists_for_user, delete_waitlists_for_user, delete_waitlists_for_book
from app.schemas.requests import Request, RequestCreate
from app.schemas.waitlist import WaitList, WaitListCreate
from fastapi import HTTPException
from datetime import datetime

def test_create_user_success():
    # Arrange
    test_request = UserCreate(
        email = "test",
        password = "123",
        username = "  hello world  ",
        is_admin = "no",
        department = "test",
        age = 0,
        firstname = 'john',
        lastname = 'doe'
    )
    
    # Act
    result = create_user(test_request)
    
    # Assert
    assert isinstance(result, User)
    assert result.username == "hello world"
    assert result.firstname == "john"
    assert result.hash_password != "123"
        
def test_authenticate_user():
    test = LoginRequest(
        username_email= "test",
        password= "123"
    )
    
    result = authenticate_user(test)
    
    assert result.username == "hello world"
    assert result.firstname == "john"
    assert result.lastname == "doe"

class TestWaitlistService(unittest.TestCase):

    def setUp(self):
        # Clear global list before each test
        waitlist_service.WAITLISTS = []
    
    @patch('app.services.waitlist_service.save_all')
    def test_create_waitlist_successful_addition(self, mock_save_all):
        input_data = WaitListCreate(isbn="123", userid="321")
        
        expected_result = WaitList(
            isbn=input_data.isbn, 
            userid=input_data.userid, 
            timestamp=datetime.now(),
            position=0
        )
        
        mock_save_all.return_value = None 
        result = create_waitlist(newWaitList=input_data)
        
        mock_save_all.assert_called_once()
        
        self.assertEqual(result.isbn, expected_result.isbn)
        self.assertEqual(result.userid, expected_result.userid)
        self.assertIsInstance(result.timestamp, datetime)
        self.assertEqual(result.position, expected_result.position)
        
    def test_create_waitlist_unsuccessful_addition(self):
        input_data = WaitListCreate(isbn="123", userid="321")
        
        create_waitlist(newWaitList=input_data)
        with self.assertRaises(HTTPException) as context:
           create_waitlist(newWaitList=input_data)

        self.assertEqual(context.exception.status_code, 406) 
        
    @patch('app.services.waitlist_service.save_all')
    def test_get_waitlists_for_user_successful(self, mock_save_all):
        mock_save_all.return_value = None

        input1 = WaitListCreate(isbn="111", userid="U1")
        input2 = WaitListCreate(isbn="222", userid="U1")
        create_waitlist(newWaitList=input1)
        create_waitlist(newWaitList=input2)

        result = get_waitlists_for_user("U1")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(isinstance(item, WaitList) for item in result))
        self.assertEqual(result[0].userid, "U1")

    @patch('app.services.waitlist_service.save_all')
    def test_get_waitlists_for_user_unsuccessful(self, mock_save_all):
        mock_save_all.return_value = None

        input_data = WaitListCreate(isbn="999", userid="AnotherUser")
        create_waitlist(newWaitList=input_data)

        with self.assertRaises(HTTPException) as context:
            get_waitlists_for_user("NonExistingUser")

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("No waitlists for 'NonExistingUser' not found", context.exception.detail)

    @patch('app.services.waitlist_service.save_all')
    def test_get_waitlists_for_books_successful(self, mock_save_all):
        mock_save_all.return_value = None

        input1 = WaitListCreate(isbn="BOOK123", userid="User1")
        input2 = WaitListCreate(isbn="BOOK123", userid="User2")
        create_waitlist(newWaitList=input1)
        create_waitlist(newWaitList=input2)

        result = get_waitlists_for_books("BOOK123")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(item.isbn == "BOOK123" for item in result))

    @patch('app.services.waitlist_service.save_all')
    def test_get_waitlists_for_books_unsuccessful(self, mock_save_all):
        mock_save_all.return_value = None

        input_data = WaitListCreate(isbn="DIFFERENTBOOK", userid="User1")
        create_waitlist(newWaitList=input_data)

        with self.assertRaises(HTTPException) as context:
            get_waitlists_for_books("UNKNOWNBOOK")

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("No waitlists for 'UNKNOWNBOOK' not found", context.exception.detail)

    @patch('app.services.waitlist_service.save_all')
    def test_delete_waitlists_for_user_successful(self, mock_save_all):
        mock_save_all.return_value = None

        create_waitlist(WaitListCreate(isbn="BOOK1", userid="USER1"))
        create_waitlist(WaitListCreate(isbn="BOOK2", userid="USER1"))
        create_waitlist(WaitListCreate(isbn="BOOK3", userid="OTHER"))
        
        mock_save_all.reset_mock()

        delete_waitlists_for_user("USER1")

        self.assertEqual(len(waitlist_service.WAITLISTS), 1)
        self.assertTrue(all(w['userid'] != "USER1" for w in waitlist_service.WAITLISTS))
        mock_save_all.assert_called_once()

    @patch('app.services.waitlist_service.save_all')
    def test_delete_waitlists_for_user_not_found(self, mock_save_all):
        mock_save_all.return_value = None
        create_waitlist(WaitListCreate(isbn="BOOKX", userid="USERX"))
        
        mock_save_all.reset_mock()

        with self.assertRaises(HTTPException) as ctx:
            delete_waitlists_for_user("NOT_FOUND_USER")

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("not found", ctx.exception.detail.lower())
        mock_save_all.assert_not_called()

    @patch('app.services.waitlist_service.save_all')
    def test_delete_waitlists_for_book_successful(self, mock_save_all):
        mock_save_all.return_value = None

        create_waitlist(WaitListCreate(isbn="TARGET", userid="U1"))
        create_waitlist(WaitListCreate(isbn="TARGET", userid="U2"))
        create_waitlist(WaitListCreate(isbn="OTHER", userid="U3"))
        
        mock_save_all.reset_mock()
        
        delete_waitlists_for_book("TARGET")

        self.assertEqual(len(waitlist_service.WAITLISTS), 1)
        self.assertTrue(all(w['isbn'] != "TARGET" for w in waitlist_service.WAITLISTS))
        mock_save_all.assert_called_once()

    @patch('app.services.waitlist_service.save_all')
    def test_delete_waitlists_for_book_not_found(self, mock_save_all):
        mock_save_all.return_value = None
        create_waitlist(WaitListCreate(isbn="BOOKZ", userid="USERZ"))
        
        mock_save_all.reset_mock()

        with self.assertRaises(HTTPException) as ctx:
            delete_waitlists_for_book("MISSING_BOOK")

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("not found", ctx.exception.detail.lower())
        mock_save_all.assert_not_called()

    @patch('app.services.waitlist_service.save_all')
    def test_delete_specific_waitlist_successful(self, mock_save_all):
        mock_save_all.return_value = None

        create_waitlist(WaitListCreate(isbn="BOOK1", userid="USER1"))
        create_waitlist(WaitListCreate(isbn="BOOK1", userid="USER2"))
        before_len = len(waitlist_service.WAITLISTS)
        
        mock_save_all.reset_mock()

        delete_specific_waitlist("BOOK1", "USER1")

        self.assertEqual(len(waitlist_service.WAITLISTS), before_len - 1)
        self.assertFalse(any(w['isbn'] == "BOOK1" and w['userid'] == "USER1" for w in waitlist_service.WAITLISTS))
        mock_save_all.assert_called_once()

    @patch('app.services.waitlist_service.save_all')
    def test_delete_specific_waitlist_not_found(self, mock_save_all):
        mock_save_all.return_value = None
        create_waitlist(WaitListCreate(isbn="BOOKX", userid="USERX"))
        
        mock_save_all.reset_mock()

        with self.assertRaises(HTTPException) as ctx:
            delete_specific_waitlist("BOOKY", "USERY")

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("not found", ctx.exception.detail.lower())
        mock_save_all.assert_not_called()
        
    
    
if __name__ == "__main__":
    pytest.main([__file__])