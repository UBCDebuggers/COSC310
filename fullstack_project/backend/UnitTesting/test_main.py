import unittest
from unittest.mock import MagicMock, patch, ANY
from datetime import datetime, timedelta, timezone
from app.core.security import _ALGORITHM, _SECRET_KEY, create_access_token, verify_access_token
from app.schemas.filter import DateRange, Filter
from app.schemas.user import User, UserCreate
from app.schemas.authentication import LoginRequest
import pytest
from app.services import waitlist_service
from app.services.users_service import create_user, authenticate_user
from app.services.books_service import filter, search_books
from app.services.waitlist_service import create_waitlist, delete_specific_waitlist, get_specific_waitlist, get_waitlists_for_books, get_waitlists_for_user, delete_waitlists_for_user, delete_waitlists_for_book, update_waitlists
from app.schemas.requests import Request, RequestCreate
from app.schemas.waitlist import WaitList, WaitListCreate
from fastapi import HTTPException
from datetime import datetime
from fastapi import HTTPException, status
from jose import jwt
from app.services import reservation_service
from app.services.reservation_service import (
    get_reservations_by_isbn,
    get_reservations_by_userid,
    get_latest_reservation_by_isbn,
    get_latest_reservation_by_userid,
    create_reservation,
    delete_reservation,
    delete_reservations_for_book,
    delete_reservations_for_user,
    cancel_reservation
)
from app.schemas.reservation import (
    CANCELLED,
    BookReservation,
    BookReservationCreate,
    RETURNED,
    NOT_RETURNED,
    NOT_RETURNED_OVERDUE
)

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

MOCK_WAITLIST_DATA = [
    {'isbn': '978-0321765723', 'userid': 'userA', 'position': 1},
    {'isbn': '978-0321765723', 'userid': 'userB', 'position': 2},
    {'isbn': '978-0321765723', 'userid': 'userC', 'position': 3},
    {'isbn': '978-0134768560', 'userid': 'userA', 'position': 1},
]

@patch('app.services.waitlist_service.save_all')
@patch('app.services.waitlist_service.load_all')
class TestWaitlistFunctions:

    def test_create_waitlist_success_new_book(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests creating a waitlist when the book is new (no existing entries)."""
        mock_load_all.return_value = []
        new_waitlist_data = WaitListCreate(isbn="978-1234567890", userid="newUser")
        
        result = create_waitlist(new_waitlist_data)

        assert result.isbn == new_waitlist_data.isbn
        assert result.userid == new_waitlist_data.userid
        assert result.position == 0 
        mock_save_all.assert_called_once()
        saved_data = mock_save_all.call_args[0][0]
        assert len(saved_data) == 1
        assert saved_data[0]['userid'] == 'newUser'
        assert saved_data[0]['position'] == 0

    def test_create_waitlist_success_existing_book(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests creating a waitlist when the book has existing entries."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA
        new_waitlist_data = WaitListCreate(isbn="978-0321765723", userid="userD")
        
        result = create_waitlist(new_waitlist_data)

        assert result.isbn == new_waitlist_data.isbn
        assert result.userid == new_waitlist_data.userid
        assert result.position == 4 
        mock_save_all.assert_called_once()
        saved_data = mock_save_all.call_args[0][0]
        assert len(saved_data) == 5
        assert saved_data[-1]['userid'] == 'userD'
        assert saved_data[-1]['position'] == 4
        
    def test_create_waitlist_failure_already_exists(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests failing to create a waitlist because the user is already on it."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA
        duplicate_data = WaitListCreate(isbn="978-0321765723", userid="userA")

        with pytest.raises(HTTPException) as excinfo:
            create_waitlist(duplicate_data)
        
        assert excinfo.value.status_code == status.HTTP_406_NOT_ACCEPTABLE
        assert "already exists" in excinfo.value.detail
        mock_save_all.assert_not_called()

    def test_get_waitlists_for_user_success(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests successfully retrieving all waitlists for a specific user."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA
        
        result = get_waitlists_for_user("userA")
        
        assert len(result) == 2
        assert all(isinstance(wl, WaitList) for wl in result)
        assert result[0].isbn == '978-0321765723'
        assert result[1].isbn == '978-0134768560'

    def test_get_waitlists_for_user_failure_not_found(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests failing to retrieve waitlists for a user that doesn't exist."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA

        with pytest.raises(HTTPException) as excinfo:
            get_waitlists_for_user("nonExistentUser")
        
        assert excinfo.value.status_code == 404
        assert "No waitlists for 'nonExistentUser' not found" in excinfo.value.detail

    def test_get_waitlists_for_books_success(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests successfully retrieving all waitlists for a specific book (ISBN)."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA
        
        result = get_waitlists_for_books("978-0321765723")
        
        assert len(result) == 4
        assert all(isinstance(wl, WaitList) for wl in result)
        positions = [wl.position for wl in result]
        assert sorted(positions) == [1, 2, 3, 4]

    def test_get_waitlists_for_books_failure_not_found(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests failing to retrieve waitlists for a book that doesn't exist."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA

        with pytest.raises(HTTPException) as excinfo:
            get_waitlists_for_books("999-9999999999")
        
        assert excinfo.value.status_code == 404
        assert "No waitlists for '999-9999999999' not found" in excinfo.value.detail
        
    def test_get_specific_waitlist_success(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests successfully retrieving a single specific waitlist record."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA
        
        result = get_specific_waitlist("userB", "978-0321765723")
        
        assert isinstance(result, WaitList)
        assert result.userid == 'userB'
        assert result.isbn == '978-0321765723'
        assert result.position == 2

    def test_get_specific_waitlist_failure_not_found(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests failing to retrieve a specific waitlist that doesn't exist."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA

        with pytest.raises(HTTPException) as excinfo:
            get_specific_waitlist("userX", "978-0321765723")
        
        assert excinfo.value.status_code == 404
        assert "No waitlists for user 'userX' under book 978-0321765723 found" in excinfo.value.detail

    def test_delete_waitlists_for_user_success(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests successfully deleting all waitlists for a user."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA.copy()
        
        delete_waitlists_for_user("userA")
        
        mock_save_all.assert_called_once()
        saved_data = mock_save_all.call_args[0][0]
        assert len(saved_data) == 3
        assert not any(wl['userid'] == 'userA' for wl in saved_data)
        assert any(wl['userid'] == 'userB' for wl in saved_data)

    def test_delete_waitlists_for_user_failure_not_found(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests failing to delete waitlists for a user that doesn't exist."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA.copy()
        
        with pytest.raises(HTTPException) as excinfo:
            delete_waitlists_for_user("nonExistentUser")
        
        assert excinfo.value.status_code == 404
        assert "Waitlists user nonExistentUser not found" in excinfo.value.detail
        mock_save_all.assert_not_called()

    def test_delete_waitlists_for_book_success(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests successfully deleting all waitlists for a book."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA.copy()
        
        delete_waitlists_for_book("978-0321765723")
        
        mock_save_all.assert_called_once()
        saved_data = mock_save_all.call_args[0][0]
        assert len(saved_data) == 1
        assert saved_data[0]['isbn'] == '978-0134768560'

    def test_delete_waitlists_for_book_failure_not_found(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests failing to delete waitlists for a book that doesn't exist."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA.copy()
        
        with pytest.raises(HTTPException) as excinfo:
            delete_waitlists_for_book("999-9999999999")
        
        assert excinfo.value.status_code == 404
        assert "Waitlists for book '999-9999999999' not found" in excinfo.value.detail
        mock_save_all.assert_not_called()
        
    def test_delete_specific_waitlist_success(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests successfully deleting a single specific waitlist."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA.copy()
        
        delete_specific_waitlist("978-0321765723", "userB")
        
        mock_save_all.assert_called_once()
        saved_data = mock_save_all.call_args[0][0]
        assert len(saved_data) == 4
        assert not any(wl['isbn'] == '978-0321765723' and wl['userid'] == 'userB' for wl in saved_data)

    def test_delete_specific_waitlist_failure_not_found(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests failing to delete a specific waitlist that doesn't exist."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA.copy()
        
        with pytest.raises(HTTPException) as excinfo:
            delete_specific_waitlist("978-0321765723", "userX")
        
        assert excinfo.value.status_code == 404
        assert "Waitlist for book '978-0321765723' and user userX not found" in excinfo.value.detail
        mock_save_all.assert_not_called()

    def test_update_waitlists_success_decrement(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests successfully decrementing positions for a book."""
        mock_load_all.return_value = MOCK_WAITLIST_DATA.copy()
        
        update_waitlists("978-0321765723")
        
        mock_save_all.assert_called_once()
        saved_data = mock_save_all.call_args[0][0]
        
        updated_positions = [wl['position'] for wl in saved_data if wl['isbn'] == '978-0321765723']
        assert sorted(updated_positions) == [0, 1, 2, 3]
        
        other_book_position = [wl['position'] for wl in saved_data if wl['isbn'] == '978-0134768560']
        assert other_book_position == [1]

    def test_update_waitlists_no_change_book_not_found(self, mock_load_all: MagicMock, mock_save_all: MagicMock):
        """Tests calling update_waitlists for a book that has no waitlists."""
        initial_data = MOCK_WAITLIST_DATA.copy()
        mock_load_all.return_value = initial_data
        
        with pytest.raises(HTTPException) as context:
            update_waitlists("999-9999999999")
        
        mock_save_all.assert_not_called()
        assert context.value.status_code == status.HTTP_404_NOT_FOUND
    
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
    query = Filter(author="Kathleen E. Woodiwiss",
                    publisher=None,
                    publish_date_range= None)
    books = [{'isbn': '0380816792', 'title': 'A Rose in Winter', 'author': 'Kathleen E. Woodiwiss', 'year_of_publication': '2011', 'publisher': 'Harper Mass Market Paperbacks'}, 
             {'isbn': '068160204X', 'title': 'The Royals', 'author': 'Kitty Kelley', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '068107468X', 'title': 'Edgar Allen Poe Collected Poems', 'author': 'Edgar Allan Poe', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '0743457226', 'title': 'Deep Waters', 'author': 'Jayne Ann Krentz', 'year_of_publication': '2010', 'publisher': 'Pocket'}
    ]
    assert all("Kathleen E. Woodiwiss" == book.get('author') for book in filter(query, books))

# test filter by publisher
def test_filter_publisher():
    query = Filter(author=None,
                    publisher="Harper Mass Market Paperbacks",
                    publish_date_range= None)
    books = [{'isbn': '0380816792', 'title': 'A Rose in Winter', 'author': 'Kathleen E. Woodiwiss', 'year_of_publication': '2011', 'publisher': 'Harper Mass Market Paperbacks'}, 
             {'isbn': '068160204X', 'title': 'The Royals', 'author': 'Kitty Kelley', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '068107468X', 'title': 'Edgar Allen Poe Collected Poems', 'author': 'Edgar Allan Poe', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '0743457226', 'title': 'Deep Waters', 'author': 'Jayne Ann Krentz', 'year_of_publication': '2010', 'publisher': 'Pocket'}
    ]
    assert all("Harper Mass Market Paperbacks" == book.get('publisher') for book in filter(query, books))

# test filter by bounded date ranges
def test_filter_date():
    query = Filter(author=None,
                    publisher=None,
                    publish_date_range= DateRange(min=2019, max=2022))
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
    query = Filter(author=None,
                    publisher=None,
                    publish_date_range= DateRange(min=None, max=2019))
    books = [{'isbn': '0380816792', 'title': 'A Rose in Winter', 'author': 'Kathleen E. Woodiwiss', 'year_of_publication': '2011', 'publisher': 'Harper Mass Market Paperbacks'}, 
             {'isbn': '068160204X', 'title': 'The Royals', 'author': 'Kitty Kelley', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '068107468X', 'title': 'Edgar Allen Poe Collected Poems', 'author': 'Edgar Allan Poe', 'year_of_publication': '2020', 'publisher': 'Bausch & Lombard'}, 
             {'isbn': '0743457226', 'title': 'Deep Waters', 'author': 'Jayne Ann Krentz', 'year_of_publication': '2010', 'publisher': 'Pocket'}
    ]
    filtered_results = filter(query, books)
    assert all(int(book.get('year_of_publication')) <= 2019 for book in filtered_results)
    
    query = Filter(author=None,
                    publisher=None,
                    publish_date_range= DateRange(min=2012, max= None))
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
    
class TestReservationService(unittest.TestCase):
    #Creates mock reservations for get_reservations_by_isbn and by userid
    def setUp(self):
        now = datetime.now()
        reservation_service.RESERVATIONS = [
            {
                "isbn": "111",
                "userid": "u1",
                "reservation_date": (now - timedelta(days=2)).isoformat(),
                "expiry_date": (now + timedelta(days=1)).isoformat(),
                "status": RETURNED
            },
            {
                "isbn": "111",
                "userid": "u2",
                "reservation_date": (now - timedelta(days=1)).isoformat(),
                "expiry_date": (now + timedelta(days=2)).isoformat(),
                "status": RETURNED
            },
            {
                "isbn": "222",
                "userid": "u1",
                "reservation_date": now.isoformat(),
                "expiry_date": (now + timedelta(days=3)).isoformat(),
                "status": RETURNED
            },
            {
                "reservation_id" : "000",
                "isbn": "223",
                "userid": "u3",
                "reservation_date": now.isoformat(),
                "expiry_date": (now + timedelta(days=3)).isoformat(),
                "status": RETURNED
            }
        ]
    
    def test_get_reservations_by_isbn_success(self):
        results = get_reservations_by_isbn("111")
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(isinstance(r, BookReservation) for r in results))

    def test_get_reservations_by_isbn_not_found(self):
        with self.assertRaises(HTTPException) as context:
            get_reservations_by_isbn("999")
        self.assertEqual(context.exception.status_code, 404)

    def test_get_reservations_by_userid_success(self):
        results = get_reservations_by_userid("u1")
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.userid == "u1" for r in results))

    def test_get_reservations_by_userid_not_found(self):
        with self.assertRaises(HTTPException) as context:
            get_reservations_by_userid("nouser")
        self.assertEqual(context.exception.status_code, 404)

    def test_get_latest_reservation_by_isbn_success(self):
        result = get_latest_reservation_by_isbn("111")
        self.assertIsInstance(result, BookReservation)
        self.assertEqual(result.isbn, "111")

    def test_get_latest_reservation_by_isbn_not_found(self):
        with self.assertRaises(HTTPException) as context:
            get_latest_reservation_by_isbn("999")
        self.assertEqual(context.exception.status_code, 404)

    def test_get_latest_reservation_by_userid_success(self):
        result = get_latest_reservation_by_userid("u1")
        self.assertIsInstance(result, BookReservation)
        self.assertEqual(result.userid, "u1")

    def test_get_latest_reservation_by_userid_not_found(self):
        with self.assertRaises(HTTPException) as context:
            get_latest_reservation_by_userid("nouser")
        self.assertEqual(context.exception.status_code, 404)

    @patch("app.services.reservation_service.save_all")
    def test_create_reservation_successful(self, mock_save_all):
        mock_save_all.return_value = None
        new_res = BookReservationCreate(
            isbn="333",
            userid="u3",
            expiry_date=(datetime.now() + timedelta(days=3)).isoformat(),
            status=RETURNED
        )

        result = create_reservation(new_res)
        mock_save_all.assert_called_once()

        self.assertEqual(result.isbn, "333")
        self.assertEqual(result.userid, "u3")
        self.assertIsInstance(result, BookReservation)
        self.assertEqual(result.status, RETURNED)

    @patch("app.services.reservation_service.save_all")
    def test_create_reservation_book_already_on_loan(self, mock_save_all):
        mock_save_all.return_value = None

        with patch("app.services.reservation_service.get_latest_reservation_by_isbn") as mock_isbn:
            mock_isbn.return_value = BookReservation(
                reservation_id="123",
                isbn="111", userid="u1", status=NOT_RETURNED,
                reservation_date=datetime.now(), expiry_date=datetime.now()
            )

            new_res = BookReservationCreate(
                isbn="111",
                userid="u2",
                expiry_date=(datetime.now() + timedelta(days=5)).isoformat(),
                status=RETURNED
            )

            with self.assertRaises(HTTPException) as context:
                create_reservation(new_res)
            self.assertEqual(context.exception.status_code, 403)
            mock_save_all.assert_not_called()

    @patch("app.services.reservation_service.save_all")
    def test_create_reservation_user_has_unreturned_book(self, mock_save_all):
        mock_save_all.return_value = None

        with patch("app.services.reservation_service.get_latest_reservation_by_isbn") as mock_isbn, \
             patch("app.services.reservation_service.get_latest_reservation_by_userid") as mock_user:

            mock_isbn.side_effect = HTTPException(status_code=404, detail="No book found")
            mock_user.return_value = BookReservation(
                reservation_id="124",
                isbn="222", userid="u1", status=NOT_RETURNED_OVERDUE,
                reservation_date=datetime.now(), expiry_date=datetime.now()
            )

            new_res = BookReservationCreate(
                isbn="222",
                userid="u1",
                expiry_date=(datetime.now() + timedelta(days=5)).isoformat()
            )

            with self.assertRaises(HTTPException) as context:
                create_reservation(new_res)
            self.assertEqual(context.exception.status_code, 403)
            mock_save_all.assert_not_called()
            
    @patch('app.services.reservation_service.save_all')
    def test_cancel_reservation_successful(self, mock_save_all):
        mock_save_all.return_value = None
        
        result = cancel_reservation("000")
        
        mock_save_all.assert_called_once()
        self.assertEqual(result.status, CANCELLED)
        self.assertEqual(reservation_service.RESERVATIONS[3]["status"], CANCELLED)
        
    @patch('app.services.reservation_service.save_all')
    def test_cancel_reservation_unsuccessful(self, mock_save_all):
        mock_save_all.return_value = None
        
        with self.assertRaises(HTTPException) as context:
            cancel_reservation("UNKOWN_RESERVATION_ID")
        
        self.assertEqual(context.exception.status_code, 404)
        mock_save_all.assert_not_called()
        
    @patch('app.services.reservation_service.save_all')
    def test_delete_reservations_unsuccessful(self, mock_save_all):
        mock_save_all.return_value = None
        
        with self.assertRaises(HTTPException) as context:
            delete_reservation("UNKNOWN_BOOK")
        
        mock_save_all.assert_not_called()
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(len(reservation_service.RESERVATIONS), 4)
        
    @patch('app.services.reservation_service.save_all')
    def test_delete_reservations_successful(self, mock_save_all):
        mock_save_all.return_value = None
        
        delete_reservation("000")
        
        self.assertEqual(len(reservation_service.RESERVATIONS), 3)
        
    @patch('app.services.reservation_service.save_all')
    def test_delete_reservations_for_user_unsuccessful(self, mock_save_all):
        mock_save_all.return_value = None
        
        with self.assertRaises(HTTPException) as context:
            delete_reservations_for_user("UNKNOWN_BOOK")
    
        mock_save_all.assert_not_called()
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(len(reservation_service.RESERVATIONS), 4)
        
    @patch('app.services.reservation_service.save_all')
    def test_delete_reservations_for_user_successful(self, mock_save_all):
        mock_save_all.return_value = None
        

        result = delete_reservations_for_user("u1")
        
        mock_save_all.assert_called_once()
        self.assertEqual(result, 2)
        self.assertEqual(len(reservation_service.RESERVATIONS), 2)
        
    @patch('app.services.reservation_service.save_all')
    def test_delete_reservations_for_book_unsuccessful(self, mock_save_all):
        mock_save_all.return_value = None
        
        with self.assertRaises(HTTPException) as context:
            delete_reservations_for_book("UNKNOWN_BOOK")
        
        mock_save_all.assert_not_called()
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(len(reservation_service.RESERVATIONS), 4)
        
    @patch('app.services.reservation_service.save_all')
    def test_delete_reservations_for_book_successful(self, mock_save_all):
        mock_save_all.return_value = None
        

        result = delete_reservations_for_book("111")
        
        mock_save_all.assert_called_once()
        self.assertEqual(result, 2)
        self.assertEqual(len(reservation_service.RESERVATIONS), 2)
        
        
if __name__ == "__main__":
    pytest.main([__file__]) 