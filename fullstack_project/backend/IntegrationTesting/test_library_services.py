from datetime import datetime, timedelta, timezone
from unittest import mock
from unittest.mock import MagicMock
from fastapi import HTTPException, status
import pytest
from app.schemas.reservation import RETURNED, RETURNED_OVERDUE
from app.services.library_service import borrow_book, return_book


MOCK_PATH = {
    'create_reservation': 'app.services.library_service.create_reservation',
    'create_waitlist': 'app.services.library_service.create_waitlist',
    'get_waitlists_for_books': 'app.services.library_service.get_waitlists_for_books',
    'get_specific_waitlist': 'app.services.library_service.get_specific_waitlist',
    'delete_specific_waitlist': 'app.services.library_service.delete_specific_waitlist',
}

class MockWaitlistEntry:
    def __init__(self, position):
        self.position = position

# Mocked constants
BookReservationCreate = mock.MagicMock()
NOT_RETURNED = "NOT_RETURNED"

# --- PYTEST FIXTURES ---
@pytest.fixture
def test_data():
    """Provides reusable test parameters."""
    return {
        "user_id": "user123",
        "isbn": "978-0321765723",
        "due_date": datetime.now() + timedelta(days=14)
    }

@pytest.fixture
def mock_services(mocker):
    """Mocks all external service functions using pytest-mock's 'mocker' fixture."""
    return {
        'get_specific_waitlist': mocker.patch(MOCK_PATH['get_specific_waitlist']),
        'get_waitlists_for_books': mocker.patch(MOCK_PATH['get_waitlists_for_books']),
        'create_reservation': mocker.patch(MOCK_PATH['create_reservation']),
        'create_waitlist': mocker.patch(MOCK_PATH['create_waitlist']),
        'delete_specific_waitlist': mocker.patch(MOCK_PATH['delete_specific_waitlist']),
    }

def test_book_available_success(mock_services : MagicMock, test_data):
    """Tests successful reservation when no waitlist is found."""
    mock_services['get_specific_waitlist'].side_effect = HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    mock_services['get_waitlists_for_books'].side_effect = HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    result = borrow_book(
        test_data['user_id'], test_data['isbn'], is_admin=False, due_date=test_data['due_date']
    )

    assert result["message"] == "Book reserved successfully. Please visit a librarian as soon as possible finish the transaction."
    mock_services['create_reservation'].assert_called_once()
    mock_services['create_waitlist'].assert_not_called()

def test_add_to_waitlist_success(mock_services, test_data):
    """Tests successful addition to the waitlist."""
    mock_services['get_specific_waitlist'].side_effect = HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    mock_services['get_waitlists_for_books'].return_value = [{"position": 0, "userid": "otheruser"}]

    result = borrow_book(
        test_data['user_id'], test_data['isbn'], is_admin=False, due_date=test_data['due_date']
    )

    assert result["message"] == "Book is unavailable. You have been added to the waitlist."
    mock_services['create_waitlist'].assert_called_once()
    mock_services['create_reservation'].assert_not_called()

def test_borrow_from_waitlist_admin_success(mock_services, test_data):
    """Tests reservation by an admin when the user is at position 0."""
    mock_services['get_specific_waitlist'].return_value = MockWaitlistEntry(position=0)

    result = borrow_book(
        test_data['user_id'], test_data['isbn'], is_admin=True, due_date=test_data['due_date']
    )

    assert result["message"] == "Book reserved from the top of the waitlist."
    mock_services['create_reservation'].assert_called_once()
    mock_services['delete_specific_waitlist'].assert_called_once_with(test_data['isbn'], test_data['user_id'])
    mock_services['get_waitlists_for_books'].assert_not_called()


def test_borrow_from_waitlist_not_admin_denied(mock_services, test_data):
    """Tests denial when user at position 0 is not an admin."""
    mock_services['get_specific_waitlist'].return_value = MockWaitlistEntry(position=0)

    with pytest.raises(HTTPException) as excinfo:
        borrow_book(test_data['user_id'], test_data['isbn'], is_admin=False, due_date=test_data['due_date'])

    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Please ask your librarian" in excinfo.value.detail
    mock_services['create_reservation'].assert_not_called()

def test_on_waitlist_not_top_denied(mock_services, test_data):
    """Tests denial when user is on the waitlist but not at position 0."""
    mock_services['get_specific_waitlist'].return_value = MockWaitlistEntry(position=2)

    with pytest.raises(HTTPException) as excinfo:
        borrow_book(test_data['user_id'], test_data['isbn'], is_admin=False, due_date=test_data['due_date'])

    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert "try again when you are at the top of the waitlist!" in excinfo.value.detail
    
@pytest.fixture
def mock_return_mocks(mocker):
    """Mocks functions used inside return_book."""
    return {
        "get_latest_reservation_by_isbn": mocker.patch("app.services.library_service.get_latest_reservation_by_isbn"),
        "update_reservation": mocker.patch("app.services.library_service.update_reservation"),
        "BookReservationCreate": mocker.patch("app.services.library_service.BookReservationCreate"),
    }


class MockReservation:
    """Simple mock reservation object."""
    def __init__(self, userid, isbn, expiry_date, reservation_id="ABC123"):
        self.userid = userid
        self.isbn = isbn
        self.expiry_date = expiry_date
        self.reservation_id = reservation_id


def test_return_book_success_not_overdue(mock_return_mocks):
    """Test when a user returns a book on time."""
    expiry = datetime.now(timezone.utc) + timedelta(days=1)
    mock_res = MockReservation("u1", "B1", expiry)

    mock_return_mocks["get_latest_reservation_by_isbn"].return_value = mock_res

    result = return_book("u1", "B1")

    assert result["message"] == "Book successfully returned!"

    mock_return_mocks["BookReservationCreate"].assert_called_once()
    args, kwargs = mock_return_mocks["BookReservationCreate"].call_args
    assert kwargs["status"] == RETURNED

    mock_return_mocks["update_reservation"].assert_called_once_with(
        mock_res.reservation_id, mock_return_mocks["BookReservationCreate"]()
    )


def test_return_book_success_overdue(mock_return_mocks):
    """Test when a user returns a book after the due date."""
    expiry = datetime.now(timezone.utc) - timedelta(days=1)
    mock_res = MockReservation("u1", "B1", expiry)

    mock_return_mocks["get_latest_reservation_by_isbn"].return_value = mock_res

    result = return_book("u1", "B1")

    assert result["message"] == "Book successfully returned!"

    mock_return_mocks["BookReservationCreate"].assert_called_once()
    args, kwargs = mock_return_mocks["BookReservationCreate"].call_args
    assert kwargs["status"] == RETURNED_OVERDUE


def test_return_book_wrong_user(mock_return_mocks):
    """Error if someone attempts to return a book they did not borrow."""
    mock_res = MockReservation("actual_user", "B1", datetime.now())

    mock_return_mocks["get_latest_reservation_by_isbn"].return_value = mock_res

    with pytest.raises(HTTPException) as excinfo:
        return_book("wrong_user", "B1")

    assert excinfo.value.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_return_mocks["update_reservation"].assert_not_called()
    mock_return_mocks["BookReservationCreate"].assert_not_called()