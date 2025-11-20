from datetime import datetime, timedelta, timezone
from unittest import mock
from unittest.mock import MagicMock
from fastapi import HTTPException, status
import pytest
from app.routers.library import book_return, borrow, get_book_history, get_book_status, get_outstanding_loans, get_user_loans
from app.schemas.reservation import RETURNED, RETURNED_OVERDUE, NOT_RETURNED
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

BookReservationCreate = mock.MagicMock()

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
    

# Service functions to be mocked
ROUTER_MOCK_PATH = {
    'update_reservation': 'app.routers.library.update_reservation',
    'borrow_book': 'app.routers.library.borrow_book',
    'return_book': 'app.routers.library.return_book',
    'get_reservations_by_userid': 'app.routers.library.get_reservations_by_userid',
    'get_latest_reservation_by_isbn': 'app.routers.library.get_latest_reservation_by_isbn',
    'get_reservations_by_isbn': 'app.routers.library.get_reservations_by_isbn',
    'find_outstanding': 'app.routers.library.find_outstanding',
}

class MockReservationPayload:
    """Mocks the Pydantic model for input."""
    def __init__(self, isbn, expiry_date):
        self.isbn = isbn
        self.expiry_date = expiry_date

class MockReservationObj():
    """Mocks a database reservation object."""
    def __init__(self, status, active=True):
        self.status = status
        self.active = active

@pytest.fixture
def router_test_data():
    """Provides reusable test parameters for routes."""
    return {
        "reservation_id": "res123",
        "userid": "user_A",
        "admin_user": {"userid": "admin_01", "is_admin": True},
        "regular_user": {"userid": "user_01", "is_admin": False},
        "isbn": "978-111",
        "payload": MockReservationPayload("978-111", datetime.now() + timedelta(days=7))
    }

@pytest.fixture
def mock_router_services(mocker):
    """Mocks the service functions called within the routes."""
    return {
        'update_reservation': mocker.patch(ROUTER_MOCK_PATH['update_reservation']),
        'borrow_book': mocker.patch(ROUTER_MOCK_PATH['borrow_book']),
        'return_book': mocker.patch(ROUTER_MOCK_PATH['return_book']),
        'get_reservations_by_userid': mocker.patch(ROUTER_MOCK_PATH['get_reservations_by_userid']),
        'get_latest_reservation_by_isbn': mocker.patch(ROUTER_MOCK_PATH['get_latest_reservation_by_isbn']),
        'get_reservations_by_isbn': mocker.patch(ROUTER_MOCK_PATH['get_reservations_by_isbn']),
        'find_outstanding': mocker.patch(ROUTER_MOCK_PATH['find_outstanding']),
    }
    
@pytest.mark.asyncio
async def test_borrow_route_as_admin(mock_router_services, router_test_data):
    """Test borrow route delegates to update_reservation for admins."""
    mock_router_services['update_reservation'].return_value = {"msg": "updated"}
    
    result = await borrow(
        reservation_id=router_test_data['reservation_id'],
        payload=router_test_data['payload'],
        current_user=router_test_data['admin_user']
    )
    
    assert result == {"msg": "updated"}
    mock_router_services['update_reservation'].assert_called_once_with(
        router_test_data['reservation_id'], 
        router_test_data['payload']
    )
    mock_router_services['borrow_book'].assert_not_called()

@pytest.mark.asyncio
async def test_borrow_route_as_regular_user(mock_router_services, router_test_data):
    """Test borrow route delegates to borrow_book for regular users."""
    mock_router_services['borrow_book'].return_value = {"msg": "borrowed"}
    
    result = await borrow(
        reservation_id=router_test_data['reservation_id'],
        payload=router_test_data['payload'],
        current_user=router_test_data['regular_user']
    )
    
    assert result == {"msg": "borrowed"}
    mock_router_services['borrow_book'].assert_called_once_with(
        userid=router_test_data['regular_user']['userid'],
        isbn=router_test_data['payload'].isbn,
        due_date=router_test_data['payload'].expiry_date,
        is_admin=False
    )
    mock_router_services['update_reservation'].assert_not_called()

@pytest.mark.asyncio
async def test_return_route_success_admin(mock_router_services, router_test_data):
    """Test return route allows admin to process return."""
    mock_router_services['return_book'].return_value = {"msg": "returned"}
    
    result = await book_return(
        userid=router_test_data['userid'],
        isbn=router_test_data['isbn'],
        current_user=router_test_data['admin_user']
    )
    
    assert result == {"msg": "returned"}
    mock_router_services['return_book'].assert_called_once_with(
        router_test_data['userid'], 
        router_test_data['isbn']
    )

@pytest.mark.asyncio
async def test_return_route_forbidden_non_admin(mock_router_services, router_test_data):
    """Test return route raises 403 for non-admin users."""
    
    with pytest.raises(HTTPException) as excinfo:
        await book_return(
            userid=router_test_data['userid'],
            isbn=router_test_data['isbn'],
            current_user=router_test_data['regular_user']
        )
    
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert "You do not have the privilege" in excinfo.value.detail
    mock_router_services['return_book'].assert_not_called()

@pytest.mark.asyncio
async def test_get_user_loans_admin(mock_router_services, router_test_data):
    """Admin can view loans for any specific user ID provided in arguments."""
    target_user = "other_user_id"
    
    await get_user_loans(
        userid=target_user,
        current_user=router_test_data['admin_user']
    )
    
    mock_router_services['get_reservations_by_userid'].assert_called_once_with(target_user)

@pytest.mark.asyncio
async def test_get_user_loans_regular_user(mock_router_services, router_test_data):
    """Regular users can only view their own loans, ignoring the userid argument."""
    arbitrary_user_arg = "someone_else"
    
    await get_user_loans(
        userid=arbitrary_user_arg,
        current_user=router_test_data['regular_user']
    )
    
    mock_router_services['get_reservations_by_userid'].assert_called_once_with(
        router_test_data['regular_user']['userid']
    )

@pytest.mark.asyncio
async def test_get_book_status_available(mock_router_services, router_test_data):
    """Returns 'available' if status is RETURNED/CANCELLED or not active."""
    mock_router_services['get_latest_reservation_by_isbn'].return_value = MockReservationObj(RETURNED)
    result = await get_book_status(router_test_data['isbn'])
    assert result == {"status": "available"}

    mock_router_services['get_latest_reservation_by_isbn'].return_value = MockReservationObj("ANY", active=False)
    result = await get_book_status(router_test_data['isbn'])
    assert result == {"status": "available"}

@pytest.mark.asyncio
async def test_get_book_status_unavailable(mock_router_services, router_test_data):
    """Returns 'unavailable' if status is NOT_RETURNED."""
    mock_router_services['get_latest_reservation_by_isbn'].return_value = MockReservationObj(NOT_RETURNED)
    
    result = await get_book_status(router_test_data['isbn'])
    
    assert result == {"status": "unavailable"}

@pytest.mark.asyncio
async def test_get_book_status_no_content(mock_router_services, router_test_data):
    """Raises 204 if status is unknown/unhandled."""
    mock_router_services['get_latest_reservation_by_isbn'].return_value = MockReservationObj("UNKNOWN_STATUS")
    
    with pytest.raises(HTTPException) as excinfo:
        await get_book_status(router_test_data['isbn'])
    
    assert excinfo.value.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.asyncio
async def test_get_book_history(mock_router_services, router_test_data):
    """Test simple pass-through for book history."""
    expected_list = ["res1", "res2"]
    mock_router_services['get_reservations_by_isbn'].return_value = expected_list
    
    result = await get_book_history(router_test_data['isbn'])
    
    assert result == expected_list
    mock_router_services['get_reservations_by_isbn'].assert_called_once_with(router_test_data['isbn'])

@pytest.mark.asyncio
async def test_get_outstanding_loans_admin(mock_router_services, router_test_data):
    """Test admin access to outstanding loans."""
    mock_router_services['find_outstanding'].return_value = []
    
    await get_outstanding_loans(current_user=router_test_data['admin_user'])
    
    mock_router_services['find_outstanding'].assert_called_once()

@pytest.mark.asyncio
async def test_get_outstanding_loans_forbidden(mock_router_services, router_test_data):
    """Test regular user access denied for outstanding loans."""
    
    with pytest.raises(HTTPException) as excinfo:
        await get_outstanding_loans(current_user=router_test_data['regular_user'])
    
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    mock_router_services['find_outstanding'].assert_not_called()