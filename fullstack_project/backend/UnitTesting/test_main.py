import unittest
from unittest.mock import patch, ANY
from datetime import datetime, timedelta, timezone
from app.core.security import _ALGORITHM, _SECRET_KEY, create_access_token, verify_access_token
from app.schemas.filter import Filter
from app.schemas.user import User, UserCreate
from app.schemas.authentication import LoginRequest
import pytest
from app.services import waitlist_service
from app.services.users_service import create_user, authenticate_user
from app.services.books_service import create_book, delete_book, filter, get_book_by_isbn, search_books, update_book
from app.services.waitlist_service import create_waitlist, delete_specific_waitlist, get_waitlists_for_books, get_waitlists_for_user, delete_waitlists_for_user, delete_waitlists_for_book
from app.schemas.requests import Request, RequestCreate
from app.schemas.waitlist import WaitList, WaitListCreate
from fastapi import HTTPException
from datetime import datetime
from fastapi import HTTPException, status
from jose import jwt

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
        
    
    
_ACCESS_TOKEN_EXPIRE_MINUTES = 30



def test_create_access_token_returns_valid_jwt():
    data = {"sub": "user123", "admin": True}

    token = create_access_token(data)

    assert isinstance(token, str)

    decoded = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])

    assert decoded["sub"] == "user123"
    assert decoded["admin"] is True
    assert "exp" in decoded
    assert datetime.fromtimestamp(decoded["exp"], timezone.utc) > datetime.now(timezone.utc)

def test_verify_access_token_valid_token(monkeypatch):
    data = {"sub": "user123", "admin": False}
    token = create_access_token(data)

    result = verify_access_token(token)

    assert result["userid"] == "user123"
    assert result["is_admin"] is False


def test_verify_access_token_expired_token(monkeypatch):
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    data = {"sub": "user123", "admin": False, "exp": expire}
    token = jwt.encode(data, _SECRET_KEY, algorithm=_ALGORITHM)

    with pytest.raises(HTTPException) as exc:
        verify_access_token(token)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "expired" in exc.value.detail.lower()


def test_verify_access_token_invalid_signature():
    data = {"sub": "user123", "admin": False}
    wrong_token = jwt.encode(data, "WRONG_KEY", algorithm=_ALGORITHM)

    with pytest.raises(HTTPException) as exc:
        verify_access_token(wrong_token)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "validate" in exc.value.detail.lower()


def test_verify_access_token_missing_userid():
    data = {"admin": False}
    token = create_access_token(data)

    with pytest.raises(HTTPException) as exc:
        verify_access_token(token)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "validate" in exc.value.detail.lower()
    
# test filter by author
def test_filter_author():
    query = Filter(author="Kathleen E. Woodiwiss")
    books = [{'isbn': '0380816792', 'title': 'A Rose in Winter', 'author': 'Kathleen E. Woodiwiss', 'year_of_publication': '2011', 'publisher': 'Harper Mass Market Paperbacks'}, 
             {'isbn': '068160204X', 'title': 'The Royals', 'author': 'Kitty Kelley', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '068107468X', 'title': 'Edgar Allen Poe Collected Poems', 'author': 'Edgar Allan Poe', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '0743457226', 'title': 'Deep Waters', 'author': 'Jayne Ann Krentz', 'year_of_publication': '2010', 'publisher': 'Pocket'}
    ]
    assert all("Kathleen E. Woodiwiss" == book.get('author') for book in filter(query, books))

# test filter by publisher
def test_filter_publisher():
    query = Filter( publisher="Harper Mass Market Paperbacks")
    books = [{'isbn': '0380816792', 'title': 'A Rose in Winter', 'author': 'Kathleen E. Woodiwiss', 'year_of_publication': '2011', 'publisher': 'Harper Mass Market Paperbacks'}, 
             {'isbn': '068160204X', 'title': 'The Royals', 'author': 'Kitty Kelley', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '068107468X', 'title': 'Edgar Allen Poe Collected Poems', 'author': 'Edgar Allan Poe', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '0743457226', 'title': 'Deep Waters', 'author': 'Jayne Ann Krentz', 'year_of_publication': '2010', 'publisher': 'Pocket'}
    ]
    assert all("Harper Mass Market Paperbacks" == book.get('publisher') for book in filter(query, books))

# test filter by bounded date ranges
def test_filter_date():
    query = Filter(publish_date_min= 2019, publish_date_max= 2022)
    books = [{'isbn': '0380816792', 'title': 'A Rose in Winter', 'author': 'Kathleen E. Woodiwiss', 'year_of_publication': '2011', 'publisher': 'Harper Mass Market Paperbacks'}, 
             {'isbn': '068160204X', 'title': 'The Royals', 'author': 'Kitty Kelley', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '068107468X', 'title': 'Edgar Allen Poe Collected Poems', 'author': 'Edgar Allan Poe', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '0743457226', 'title': 'Deep Waters', 'author': 'Jayne Ann Krentz', 'year_of_publication': '2010', 'publisher': 'Pocket'}
    ]
    filtered_results = filter(query, books)
    assert all(int(book.get('year_of_publication')) <= 2022 for book in filtered_results)
    assert all(int(book.get('year_of_publication')) >= 2019 for book in filtered_results)

# test filter by unbounded date ranges
def test_filter_date_single():
    query = Filter(publish_date_max= 2019)
    books = [{'isbn': '0380816792', 'title': 'A Rose in Winter', 'author': 'Kathleen E. Woodiwiss', 'year_of_publication': '2011', 'publisher': 'Harper Mass Market Paperbacks'}, 
             {'isbn': '068160204X', 'title': 'The Royals', 'author': 'Kitty Kelley', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '068107468X', 'title': 'Edgar Allen Poe Collected Poems', 'author': 'Edgar Allan Poe', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '0743457226', 'title': 'Deep Waters', 'author': 'Jayne Ann Krentz', 'year_of_publication': '2010', 'publisher': 'Pocket'}
    ]
    filtered_results = filter(query, books)
    assert all(int(book.get('year_of_publication')) <= 2019 for book in filtered_results)
    
    query = Filter(publish_date_min= 2012)
    books = [{'isbn': '0380816792', 'title': 'A Rose in Winter', 'author': 'Kathleen E. Woodiwiss', 'year_of_publication': '2011', 'publisher': 'Harper Mass Market Paperbacks'}, 
             {'isbn': '068160204X', 'title': 'The Royals', 'author': 'Kitty Kelley', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '068107468X', 'title': 'Edgar Allen Poe Collected Poems', 'author': 'Edgar Allan Poe', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '0743457226', 'title': 'Deep Waters', 'author': 'Jayne Ann Krentz', 'year_of_publication': '2010', 'publisher': 'Pocket'}
    ]
    filtered_results = filter(query, books)
    assert all(int(book.get('year_of_publication')) >= 2012 for book in filtered_results)
    
 # test none filter
def test_none_filter():
    query = None
    books = [{'isbn': '0380816792', 'title': 'A Rose in Winter', 'author': 'Kathleen E. Woodiwiss', 'year_of_publication': '2011', 'publisher': 'Harper Mass Market Paperbacks'}, 
             {'isbn': '068160204X', 'title': 'The Royals', 'author': 'Kitty Kelley', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '068107468X', 'title': 'Edgar Allen Poe Collected Poems', 'author': 'Edgar Allan Poe', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '0743457226', 'title': 'Deep Waters', 'author': 'Jayne Ann Krentz', 'year_of_publication': '2010', 'publisher': 'Pocket'}
    ]
    filtered_results = filter(query, books)
    
    assert len(books) == len(filtered_results)
    
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

def get_base_mock_data():
    """Returns a fresh, immutable list for each test run."""
    return [
        {
            "isbn": "978-0134768560",
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "year_of_publication": "2008",
            "publisher": "Prentice Hall",
            "img_url_s": "s1.jpg",
            "img_url_m": "m1.jpg",
            "img_url_l": "l1.jpg",
        },
        {
            "isbn": "978-0321765723",
            "title": "The Pragmatic Programmer",
            "author": "Andrew Hunt",
            "year_of_publication": "1999",
            "publisher": "Addison-Wesley",
            "img_url_s": "s2.jpg",
            "img_url_m": "m2.jpg",
            "img_url_l": "l2.jpg",
        },
    ]

# --- 4. Mocking the Dependencies and Test Class ---

# IMPORTANT: You MUST adjust the patch strings below (e.g., 'your_service_file_name.load_all')
# to match the exact module path where load_all and save_all are imported in your service code.

@patch('app.services.books_service.save_all')  # <--- Adjust 'book_service' if your file is named differently
@patch('app.services.books_service.load_all')  # <--- Adjust 'book_service' if your file is named differently
class TestBookFunctions:
    
    def test_create_book_success(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests successful creation of a new book."""
        mock_load_all.return_value = get_base_mock_data()
        new_book_data = BookCreate(
            isbn="978-1234567890",
            title="Design Patterns",
            author="Erich Gamma",
            year_of_publication= 1994,
            publisher="Addison-Wesley",
            img_url_s="s3.jpg",
            img_url_m="m3.jpg",
            img_url_l="l3.jpg",
        )
        
        result = create_book(new_book_data)

        assert result.isbn == new_book_data.isbn
        assert result.title == "Design Patterns"
        mock_save_all.assert_called_once()
        saved_data = mock_save_all.call_args[0][0]
        assert len(saved_data) == 3
        assert saved_data[-1]['isbn'] == "978-1234567890"

    def test_create_book_success_stripping_whitespace(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests that all string fields are stripped of leading/trailing whitespace."""
        mock_load_all.return_value = []
        new_book_data = BookCreate(
            isbn=" 999-9999999999 ",
            title=" The Title ",
            author=" The Author ",
            year_of_publication=2024,
            publisher=" The Publisher ",
            img_url_s=" s.jpg ",
            img_url_m=" m.jpg ",
            img_url_l=" l.jpg ",
        )
        
        result = create_book(new_book_data)

        assert result.isbn == "999-9999999999"
        assert result.title == "The Title"
        assert result.author == "The Author"
        mock_save_all.assert_called_once()

    def test_create_book_failure_isbn_collision(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests failure when attempting to create a book with a non-unique ISBN."""
        mock_load_all.return_value = get_base_mock_data()
        duplicate_data = BookCreate(
            isbn="978-0134768560",
            title="A different title",
            author="A different author",
            year_of_publication=2020,
            publisher="New Publisher",
            img_url_s="s1.jpg",
            img_url_m="m1.jpg",
            img_url_l="l1.jpg",
        )

        with pytest.raises(HTTPException) as excinfo:
            create_book(duplicate_data)
        
        assert excinfo.value.status_code == 409
        assert "ISBN collision; retry." in excinfo.value.detail
        mock_save_all.assert_not_called()

    def test_get_book_by_isbn_success(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests successful retrieval of a book by its ISBN."""
        mock_load_all.return_value = get_base_mock_data()
        
        isbn = "978-0321765723"
        result = get_book_by_isbn(isbn)
        
        assert isinstance(result, Book)
        assert result.isbn == isbn
        assert result.title == "The Pragmatic Programmer"

    def test_get_book_by_isbn_failure_not_found(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests failure when requesting a non-existent ISBN."""
        mock_load_all.return_value = get_base_mock_data()
        non_existent_isbn = "999-9999999999"

        with pytest.raises(HTTPException) as excinfo:
            get_book_by_isbn(non_existent_isbn)
        
        assert excinfo.value.status_code == 404
        assert f"Book '{non_existent_isbn}' not found" in excinfo.value.detail
    
    def test_update_book_success(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests successful update of an existing book."""
        mock_load_all.return_value = get_base_mock_data()
        target_isbn = "978-0134768560"
        
        update_data = BookUpdate(
            isbn=target_isbn,
            title="Clean Code Updated",
            author="Bob Martin",
            year_of_publication=2009,
            publisher="Updated Publisher",
            img_url_s="s_new.jpg",
            img_url_m="m_new.jpg",
            img_url_l="l_new.jpg",
        )
        
        result = update_book(target_isbn, update_data)
        
        assert result.title == "Clean Code Updated"
        assert result.author == "Bob Martin"
        mock_save_all.assert_called_once()
        
        saved_data = mock_save_all.call_args[0][0]
        updated_record = next(book for book in saved_data if book['isbn'] == target_isbn)
        assert updated_record['title'] == "Clean Code Updated"

    def test_update_book_success_stripping_whitespace(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests that all string fields are stripped during the update."""
        mock_load_all.return_value = get_base_mock_data()
        target_isbn = "978-0134768560"
        
        update_data = BookUpdate(
            isbn=" 978-0134768560 ",
            title=" Updated Title ",
            author=" Updated Author ",
            year_of_publication=2020,
            publisher=" Updated Pub ",
            img_url_s=" s.jpg ",
            img_url_m=" m.jpg ",
            img_url_l=" l.jpg ",
        )
        
        result = update_book(target_isbn, update_data)
        
        assert result.title == "Updated Title"
        assert result.year_of_publication == 2020
        mock_save_all.assert_called_once()
        
        saved_data = mock_save_all.call_args[0][0]
        updated_record = next(book for book in saved_data if book['isbn'] == target_isbn)
        assert updated_record['title'] == "Updated Title"

    def test_update_book_failure_not_found(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests failure when attempting to update a non-existent book."""
        mock_load_all.return_value = get_base_mock_data()
        non_existent_isbn = "999-9999999999"

        update_data = BookUpdate(
            isbn=non_existent_isbn, title="X", author="X", year_of_publication=0, 
            publisher="X", img_url_s="X", img_url_m="X", img_url_l="X"
        )

        with pytest.raises(HTTPException) as excinfo:
            update_book(non_existent_isbn, update_data)
        
        assert excinfo.value.status_code == 404
        assert f"Book '{non_existent_isbn}' not found" in excinfo.value.detail
        mock_save_all.assert_not_called()

    def test_delete_book_success(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests successful deletion of a book."""
        initial_data = get_base_mock_data()
        mock_load_all.return_value = initial_data
        target_isbn = "978-0134768560"
        
        delete_book(target_isbn)
        
        mock_save_all.assert_called_once()
        saved_data = mock_save_all.call_args[0][0]
        assert len(saved_data) == 1
        assert saved_data[0]['isbn'] == "978-0321765723"

    def test_delete_book_failure_not_found(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests failure when attempting to delete a non-existent book."""
        initial_data = get_base_mock_data()
        mock_load_all.return_value = initial_data
        non_existent_isbn = "999-9999999999"
        
        with pytest.raises(HTTPException) as context:
            delete_book(non_existent_isbn)
        
        mock_save_all.assert_not_called()
        assert context.value.status_code == status.HTTP_404_NOT_FOUND
    
if __name__ == "__main__":
    pytest.main([__file__]) 