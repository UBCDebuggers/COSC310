import unittest
from unittest import mock
from unittest.mock import MagicMock, patch, ANY
from datetime import datetime, timedelta, timezone
from app.core.security import _ALGORITHM, _SECRET_KEY, create_access_token, verify_access_token
from app.schemas.book import Book, BookCreate, BookUpdate
from app.schemas.filter import Filter
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.authentication import LoginRequest
import pytest
from app.services import waitlist_service
from app.services.users_service import create_user, authenticate_user, delete_user, get_user_by_email, get_user_by_id, get_user_by_username, list_users, update_user
from app.services.books_service import create_book, delete_book, filter, get_book_by_isbn, search_books, update_book
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
import uuid

@pytest.fixture
def mock_user_data():
    """Provides a list of mock user dictionaries matching the storage format."""
    return [
        {"userid": "user-a", "email": "alice@example.com", "hash_password": "hashed_alice", "is_admin": "False", "department": "HR", "age": 30, "username": "alice_hr", "firstname": "Alice", "lastname": "Smith"},
        {"userid": "user-b", "email": "bob@example.com", "hash_password": "hashed_bob", "is_admin": "True", "department": "IT", "age": 45, "username": "bob_it", "firstname": "Bob", "lastname": "Jones"},
    ]

@pytest.fixture
def mock_new_user_create():
    """Provides a mock UserCreate payload."""
    return UserCreate(
        email="charlie@example.com ",
        password="secret_password ",
        is_admin="False ",
        department="Finance ",
        age=25,
        username="charlie_fin ",
        firstname="Charlie ",
        lastname="Brown "
    )

@pytest.fixture
def mock_user_update_payload():
    """Provides a mock UserUpdate payload."""
    return UserUpdate(
        email="updated@example.com ",
        password="new_password ",
        is_admin="True ",
        department="Executive ",
        age=55,
        username="top_brass ",
        firstname="Top ",
        lastname="Brass "
    )

def test_list_users_success(mocker, mock_user_data):
    """Tests successful retrieval and conversion of all users."""
    mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    
    users = list_users()
    
    assert len(users) == 2
    assert isinstance(users[0], User)
    assert users[1].email == "bob@example.com"

def test_list_users_empty(mocker):
    """Tests retrieval when no users exist."""
    mocker.patch('app.services.users_service.load_all', return_value=[])
    
    users = list_users()
    
    assert len(users) == 0

def test_create_user_success(mocker, mock_user_data, mock_new_user_create):
    """Tests successful creation of a new user."""
    mock_load = mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    mock_save = mocker.patch('app.services.users_service.save_all')
    mock_uuid = mocker.patch('app.services.users_service.uuid.uuid4', return_value=uuid.UUID('00000000-0000-0000-0000-00000000000c'))
    mock_hash = mocker.patch('app.services.users_service.bcrypt_context.hash', return_value="hashed_charlie")

    new_user = create_user(mock_new_user_create)

    assert new_user.userid == '00000000-0000-0000-0000-00000000000c'
    assert new_user.username == "charlie_fin" 
    assert new_user.hash_password == "hashed_charlie"
    
    mock_load.assert_called_once()
    mock_uuid.assert_called_once()
    mock_hash.assert_called_once()
    
    mock_save.assert_called_once()
    saved_data = mock_save.call_args[0][0]
    assert len(saved_data) == 3
    assert saved_data[2]['userid'] == new_user.userid

def test_create_user_handles_uuid_collision(mocker, mock_user_data, mock_new_user_create):
    """Tests that a UUID collision is detected and a new UUID is generated."""
    mock_user_data[0]['userid'] = '00000000-0000-0000-0000-00000000000c'
    mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    
    mock_uuid = mocker.patch('app.services.users_service.uuid.uuid4', side_effect=[
        uuid.UUID('00000000-0000-0000-0000-00000000000c'), 
        uuid.UUID('00000000-0000-0000-0000-00000000000d')   
    ])
    mocker.patch('app.services.users_service.save_all')
    mocker.patch('app.services.users_service.bcrypt_context.hash', return_value="hashed_charlie")

    new_user = create_user(mock_new_user_create)

    assert new_user.userid == '00000000-0000-0000-0000-00000000000d'
    assert mock_uuid.call_count == 2

def test_get_user_by_id_success(mocker, mock_user_data):
    """Tests successful retrieval of a user by ID."""
    mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    
    user = get_user_by_id("user-a")
    
    assert isinstance(user, User)
    assert user.email == "alice@example.com"

def test_get_user_by_id_not_found(mocker, mock_user_data):
    """Tests retrieval failure for a non-existent ID."""
    mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    
    with pytest.raises(HTTPException) as excinfo:
        get_user_by_id("user-z")
        
    assert excinfo.value.status_code == 404
    assert "User 'user-z' not found" in excinfo.value.detail

def test_get_user_by_email_success(mocker, mock_user_data):
    """Tests successful retrieval of a user by email (handling the original 'eamil' typo by using 'email')."""
    mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    
    user = get_user_by_email("bob@example.com")
    
    assert isinstance(user, User)
    assert user.userid == "user-b"

def test_get_user_by_email_not_found(mocker, mock_user_data):
    """Tests retrieval failure for a non-existent email."""
    mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    
    with pytest.raises(HTTPException) as excinfo:
        get_user_by_email("unknown@example.com")
        
    assert excinfo.value.status_code == 404
    assert "Email: 'unknown@example.com' not found" in excinfo.value.detail

def test_get_user_by_username_success(mocker, mock_user_data):
    """Tests successful retrieval of a user by username."""
    mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    
    user = get_user_by_username("alice_hr")
    
    assert isinstance(user, User)
    assert user.email == "alice@example.com"

def test_get_user_by_username_not_found(mocker, mock_user_data):
    """Tests retrieval failure for a non-existent username."""
    mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    
    with pytest.raises(HTTPException) as excinfo:
        get_user_by_username("ghost_user")
        
    assert excinfo.value.status_code == 404
    assert "User: 'ghost_user' not found" in excinfo.value.detail

@pytest.mark.parametrize("login_input, expected_user_id", [
    (LoginRequest(username_email="alice@example.com", password="password"), "user-a"),
    (LoginRequest(username_email="bob_it", password="password"), "user-b"),
])
def test_authenticate_user_success(mocker, mock_user_data, login_input, expected_user_id):
    """Tests successful authentication via email or username."""
    mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    mock_bcrypt = mocker.patch("app.services.users_service.bcrypt_context")
    mock_bcrypt.verify.return_value = True
    
    user = authenticate_user(login_input)
    
    assert user is not None
    assert user.userid == expected_user_id
    mock_bcrypt.verify.assert_called_once()

def test_authenticate_user_failure_wrong_password(mocker, mock_user_data):
    """Tests authentication failure due to incorrect password."""
    mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    mock_bcrypt = mocker.patch("app.services.users_service.bcrypt_context")
    mock_bcrypt.verify.return_value = False
    
    payload = LoginRequest(username_email="alice@example.com", password="wrong_password")
    user = authenticate_user(payload)
    
    assert user is None
    mock_bcrypt.verify.assert_called_once()

def test_authenticate_user_failure_not_found(mocker, mock_user_data):
    """Tests authentication failure for a non-existent user."""
    mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    mock_bcrypt = mocker.patch("app.services.users_service.bcrypt_context")
    mock_bcrypt.verify.return_value = None
    
    payload = LoginRequest(username_email="ghost@example.com", password="password")
    user = authenticate_user(payload)
    
    assert user is None
    mock_bcrypt.verify.assert_not_called()

def test_update_user_success(mocker, mock_user_data, mock_user_update_payload):
    """Tests successful update of an existing user's details."""
    mock_load = mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    mock_save = mocker.patch('app.services.users_service.save_all')
    
    user_id_to_update = "user-a"
    updated_user = update_user(user_id_to_update, mock_user_update_payload)
    
    assert updated_user.userid == user_id_to_update
    assert updated_user.email == "updated@example.com"
    assert updated_user.is_admin == "True"
    
    mock_load.assert_called_once()
    mock_save.assert_called_once()
    
    saved_data = mock_save.call_args[0][0]
    updated_record = saved_data[0]
    assert updated_record['email'] == "updated@example.com"

def test_update_user_not_found(mocker, mock_user_data, mock_user_update_payload):
    """Tests update failure for a non-existent ID."""
    mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    mock_save = mocker.patch('app.services.users_service.save_all')
    
    with pytest.raises(HTTPException) as excinfo:
        update_user("user-z", mock_user_update_payload)
        
    assert excinfo.value.status_code == 404
    assert "User 'user-z' not found" in excinfo.value.detail
    mock_save.assert_not_called()

def test_delete_user_success(mocker, mock_user_data):
    """Tests successful deletion of an existing user."""
    mock_load = mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    mock_save = mocker.patch('app.services.users_service.save_all')
    
    delete_user("user-a")
    
    mock_load.assert_called_once()
    mock_save.assert_called_once()
    
    saved_data = mock_save.call_args[0][0]
    assert len(saved_data) == 1
    assert saved_data[0]['userid'] == "user-b"

def test_delete_user_not_found(mocker, mock_user_data):
    """Tests deletion failure for a non-existent ID."""
    mocker.patch('app.services.users_service.load_all', return_value=mock_user_data)
    mock_save = mocker.patch('app.services.users_service.save_all')
    
    with pytest.raises(HTTPException) as excinfo:
        delete_user("user-z")
        
    assert excinfo.value.status_code == 404
    assert "User 'user-z' not found" in excinfo.value.detail
    mock_save.assert_not_called()

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
        assert "No waitlists for user 'nonExistentUser' found" in excinfo.value.detail

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
        assert "No waitlists for book '999-9999999999' found" in excinfo.value.detail
        
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