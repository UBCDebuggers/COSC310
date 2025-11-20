import unittest
import pytest
from fastapi import HTTPException
from datetime import datetime
from app.services.create_history_item import (
    create_history,
    get_last_books,
    get_history_by_isbn,
    get_history_by_userid,
    delete_history_item,
)
from app.schemas.history import HistoryItem
from app.repositories import history_repo
from unittest.mock import patch

# Mock Repository
@pytest.fixture
def mock_history_repo(monkeypatch):
    mock_repo = unittest.TestCase()
    monkeypatch.setattr(history_repo, "add_history_item", mock_repo.add_history_item)
    monkeypatch.setattr(history_repo, "load_all", mock_repo.load_all)
    monkeypatch.setattr(history_repo, "delete_history_item", mock_repo.delete_history_item)
    return mock_repo

# Creating a history item with valid inputs
def test_create_history_success(mock_history_repo):
    mock_history_repo.add_history_item.return_value = {
        "userid": "user1",
        "isbn": "isbn1",
        "date": datetime.fromisoformat("2024-01-01T00:00:00")
    }
    
    result = create_history("user1", "isbn1")
    
    assert isinstance(result, HistoryItem)
    assert result.userid == "user1"
    assert result.isbn == "isbn1"
    mock_history_repo.add_history_item.assert_called_once_with("user1", "isbn1")

# Verify books are sorted by date in descending order (newest first)
def test_get_last_books_sorting(mock_history_repo):
    mock_history_repo.load_all.return_value = [
        {
            "userid": "user1",
            "isbn": "isbn1",
            "date": datetime.fromisoformat("2024-01-02T00:00:00")  # Middle
        },
        {
            "userid": "user1",
            "isbn": "isbn2",
            "date": datetime.fromisoformat("2024-01-03T00:00:00")  # Newest
        },
        {
            "userid": "user1",
            "isbn": "isbn3",
            "date": datetime.fromisoformat("2024-01-01T00:00:00")  # Oldest
        },
    ]
    
    result = get_last_books("user1", limit=2)
    assert len(result) == 2, "Should return only 2 items due to limit"
    assert result[0].isbn == "isbn2", "First should be newest (2024-01-03)"
    assert result[1].isbn == "isbn1", "Second should be middle (2024-01-02)"
    assert result[0].date > result[1].date, "Dates should be in descending order"

# Verify limit parameter is respected
def test_get_last_books_respects_limit(mock_history_repo):
    mock_history_repo.load_all.return_value = [
        {"userid": "user1", "isbn": f"isbn{i}", "date": datetime.fromisoformat(f"2024-01-0{5-i}T00:00:00")}
        for i in range(1, 6)
    ]
    result = get_last_books("user1", limit=3)
    assert len(result) == 3

# Verify default limit is 10 when not specified
def test_get_last_books_default_limit(mock_history_repo):
    mock_history_repo.load_all.return_value = [
        {"userid": "user1", "isbn": f"isbn{i}", "date": datetime.fromisoformat(f"2024-01-{str(i).zfill(2)}T00:00:00")}
        for i in range(1, 16)
    ]
    result = get_last_books("user1")  # No limit specified
    assert len(result) == 10, "Should use default limit of 10"

# When user has fewer books than limit, return all
def test_get_last_books_fewer_than_limit(mock_history_repo):
    mock_history_repo.load_all.return_value = [
        {"userid": "user1", "isbn": "isbn1", "date": datetime.fromisoformat("2024-01-02T00:00:00")},
        {"userid": "user1", "isbn": "isbn2", "date": datetime.fromisoformat("2024-01-01T00:00:00")},
    ]   
    result = get_last_books("user1", limit=10)  # Request 10 but only 2 exist
    assert len(result) == 2, "Should return all 2 items even though limit is 10"

# User with no history should raise 404
def test_get_last_books_empty_history(mock_history_repo):
    mock_history_repo.load_all.return_value = []
    
    with pytest.raises(HTTPException) as exc_info:
        get_last_books("user_with_no_history")
    
    assert exc_info.value.status_code == 404

# get_history_by_isbn
# Finding history items for a specific ISBN
def test_get_history_by_isbn_single_result(mock_history_repo):
    mock_history_repo.load_all.return_value = [
        {"userid": "user1", "isbn": "isbn1", "date": datetime.fromisoformat("2024-01-01T00:00:00")},
        {"userid": "user2", "isbn": "isbn2", "date": datetime.fromisoformat("2024-01-02T00:00:00")},
    ]
    
    result = get_history_by_isbn("isbn1")
    
    assert len(result) == 1
    assert result[0].isbn == "isbn1"
    assert result[0].userid == "user1"

# Multiple users viewing same book
def test_get_history_by_isbn_multiple_users(mock_history_repo):
    mock_history_repo.load_all.return_value = [
        {"userid": "user1", "isbn": "popular_isbn", "date": datetime.fromisoformat("2024-01-01T00:00:00")},
        {"userid": "user2", "isbn": "popular_isbn", "date": datetime.fromisoformat("2024-01-02T00:00:00")},
        {"userid": "user3", "isbn": "popular_isbn", "date": datetime.fromisoformat("2024-01-03T00:00:00")},
        {"userid": "user1", "isbn": "other_isbn", "date": datetime.fromisoformat("2024-01-04T00:00:00")},
    ]
    
    result = get_history_by_isbn("popular_isbn")
    
    assert len(result) == 3, "Should return all 3 users who viewed this ISBN"
    assert all(item.isbn == "popular_isbn" for item in result)

# ISBN not in history should raise 404
def test_get_history_by_isbn_not_found(mock_history_repo):
    mock_history_repo.load_all.return_value = []
    
    with pytest.raises(HTTPException) as exc_info:
        get_history_by_isbn("nonexistent_isbn")
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()

# get_history_by_userid
# User with one book in history
def test_get_history_by_userid_single_item(mock_history_repo):
    mock_history_repo.load_all.return_value = [
        {"userid": "user1", "isbn": "isbn1", "date": datetime.fromisoformat("2024-01-01T00:00:00")},
        {"userid": "user2", "isbn": "isbn2", "date": datetime.fromisoformat("2024-01-02T00:00:00")},
    ]
    result = get_history_by_userid("user1")
    assert len(result) == 1
    assert result[0].userid == "user1"
    assert result[0].isbn == "isbn1"

# User with multiple books in history
def test_get_history_by_userid_multiple_items(mock_history_repo):
    mock_history_repo.load_all.return_value = [
        {"userid": "user1", "isbn": "isbn1", "date": datetime.fromisoformat("2024-01-01T00:00:00")},
        {"userid": "user1", "isbn": "isbn2", "date": datetime.fromisoformat("2024-01-02T00:00:00")},
        {"userid": "user1", "isbn": "isbn3", "date": datetime.fromisoformat("2024-01-03T00:00:00")},
        {"userid": "user2", "isbn": "isbn4", "date": datetime.fromisoformat("2024-01-04T00:00:00")},
    ]
    result = get_history_by_userid("user1")
    assert len(result) == 3, "Should return all 3 items for user1"
    assert all(item.userid == "user1" for item in result)

# Non-existent user should raise 404
def test_get_history_by_userid_not_found(mock_history_repo):
    mock_history_repo.load_all.return_value = []
    
    with pytest.raises(HTTPException) as exc_info:
        get_history_by_userid("nonexistent_user")
    
    assert exc_info.value.status_code == 404

# delete_history_item
# Successfully delete an existing history item
def test_delete_history_item_success(mock_history_repo):
    mock_history_repo.delete_history_item.return_value = True
    try:
        delete_history_item("item_id_1")
    except HTTPException:
        pytest.fail("HTTPException was raised unexpectedly!")
    
    mock_history_repo.delete_history_item.assert_called_once_with("item_id_1")

# Deleting non-existent item should raise 404
def test_delete_history_item_not_found(mock_history_repo):
    mock_history_repo.delete_history_item.return_value = False
    
    with pytest.raises(HTTPException) as exc_info:
        delete_history_item("nonexistent_id")
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()

# Attempt to delete with empty string ID
def test_delete_history_item_empty_string(mock_history_repo):
    mock_history_repo.delete_history_item.return_value = False
    
    with pytest.raises(HTTPException):
        delete_history_item("")