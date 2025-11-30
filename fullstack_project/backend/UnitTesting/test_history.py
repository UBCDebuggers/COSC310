import pytest
from fastapi import HTTPException
from datetime import datetime
from unittest.mock import MagicMock

from app.services.create_history_item import (
    create_history,
    get_last_books,
    get_history_by_isbn,
    get_history_by_userid,
    delete_history_item,
)

from app.schemas.history import HistoryItem
from app.repositories import history_repo

#Universal mock for history_repo. Ensures all tests use the same stubbed repo without repeating boilerplate.
@pytest.fixture
def mock_repo(monkeypatch):
    
    repo = MagicMock()
    repo.add_history_item = MagicMock()
    repo.load_all = MagicMock()
    repo.delete_history_item = MagicMock()

    monkeypatch.setattr(history_repo, "add_history_item", repo.add_history_item)
    monkeypatch.setattr(history_repo, "load_all", repo.load_all)
    monkeypatch.setattr(history_repo, "delete_history_item", repo.delete_history_item)

    return repo


#Factory helper to ensure consistent date formatting.
def make_item(userid: str, isbn: str, date_str: str) -> dict:
    return {
        "userid": userid,
        "isbn": isbn,
        "date": datetime.fromisoformat(date_str)
    }


#History Creation Tests

def test_create_history_success(mock_repo):
    mock_repo.add_history_item.return_value = make_item(
        "user1", "isbn1", "2024-01-01T00:00:00"
    )

    result = create_history("user1", "isbn1")

    assert isinstance(result, HistoryItem)
    assert result.userid == "user1"
    assert result.isbn == "isbn1"
    mock_repo.add_history_item.assert_called_once_with("user1", "isbn1")


#last books tests created
def test_get_last_books_sorting(mock_repo):
    mock_repo.load_all.return_value = [
        make_item("user1", "isbn1", "2024-01-02T00:00:00"),  # middle
        make_item("user1", "isbn2", "2024-01-03T00:00:00"),  # newest
        make_item("user1", "isbn3", "2024-01-01T00:00:00"),  # oldest
    ]

    result = get_last_books("user1", limit=2)

    assert len(result) == 2
    assert result[0].isbn == "isbn2"   # newest first
    assert result[1].isbn == "isbn1"   # then middle
    assert result[0].date > result[1].date


def test_get_last_books_respects_limit(mock_repo):
    mock_repo.load_all.return_value = [
        make_item("user1", f"isbn{i}", f"2024-01-0{6-i}T00:00:00") for i in range(1, 6)
    ]

    result = get_last_books("user1", limit=3)
    assert len(result) == 3


def test_get_last_books_default_limit(mock_repo):
    mock_repo.load_all.return_value = [
        make_item("user1", f"isbn{i}", f"2024-01-{str(i).zfill(2)}T00:00:00")
        for i in range(1, 16)
    ]

    result = get_last_books("user1")
    assert len(result) == 10  # default limit


def test_get_last_books_fewer_than_limit(mock_repo):
    mock_repo.load_all.return_value = [
        make_item("user1", "isbn1", "2024-01-02T00:00:00"),
        make_item("user1", "isbn2", "2024-01-01T00:00:00"),
    ]

    result = get_last_books("user1", limit=10)
    assert len(result) == 2


def test_get_last_books_empty_history(mock_repo):
    mock_repo.load_all.return_value = []

    with pytest.raises(HTTPException) as exc:
        get_last_books("user_with_no_history")

    assert exc.value.status_code == 404


#ISBN HISTORY TESTS
def test_get_history_by_isbn_single_result(mock_repo):
    mock_repo.load_all.return_value = [
        make_item("user1", "isbn1", "2024-01-01T00:00:00"),
        make_item("user2", "isbn2", "2024-01-02T00:00:00"),
    ]

    result = get_history_by_isbn("isbn1")

    assert len(result) == 1
    assert result[0].isbn == "isbn1"
    assert result[0].userid == "user1"


def test_get_history_by_isbn_multiple_users(mock_repo):
    mock_repo.load_all.return_value = [
        make_item("user1", "popular_isbn", "2024-01-01T00:00:00"),
        make_item("user2", "popular_isbn", "2024-01-02T00:00:00"),
        make_item("user3", "popular_isbn", "2024-01-03T00:00:00"),
    ]

    result = get_history_by_isbn("popular_isbn")

    assert len(result) == 3
    assert all(item.isbn == "popular_isbn" for item in result)


def test_get_history_by_isbn_not_found(mock_repo):
    mock_repo.load_all.return_value = []

    with pytest.raises(HTTPException) as exc:
        get_history_by_isbn("nonexistent_isbn")

    assert exc.value.status_code == 404


#History by UserId test
def test_get_history_by_userid_single_item(mock_repo):
    mock_repo.load_all.return_value = [
        make_item("user1", "isbn1", "2024-01-01T00:00:00"),
        make_item("user2", "isbn2", "2024-01-02T00:00:00"),
    ]

    result = get_history_by_userid("user1")

    assert len(result) == 1
    assert result[0].userid == "user1"


def test_get_history_by_userid_multiple_items(mock_repo):
    mock_repo.load_all.return_value = [
        make_item("user1", "isbn1", "2024-01-01T00:00:00"),
        make_item("user1", "isbn2", "2024-01-02T00:00:00"),
        make_item("user1", "isbn3", "2024-01-03T00:00:00"),
    ]

    result = get_history_by_userid("user1")

    assert len(result) == 3
    assert all(item.userid == "user1" for item in result)


def test_get_history_by_userid_not_found(mock_repo):
    mock_repo.load_all.return_value = []

    with pytest.raises(HTTPException) as exc:
        get_history_by_userid("nonexistent_user")

    assert exc.value.status_code == 404


#Delete history item tests

def test_delete_history_item_success(mock_repo):
    mock_repo.delete_history_item.return_value = True

    delete_history_item("item_id_1")

    mock_repo.delete_history_item.assert_called_once_with("item_id_1")


def test_delete_history_item_not_found(mock_repo):
    mock_repo.delete_history_item.return_value = False

    with pytest.raises(HTTPException) as exc:
        delete_history_item("nonexistent_id")

    assert exc.value.status_code == 404


def test_delete_history_item_empty_string(mock_repo):
    mock_repo.delete_history_item.return_value = False

    with pytest.raises(HTTPException):
        delete_history_item("")
