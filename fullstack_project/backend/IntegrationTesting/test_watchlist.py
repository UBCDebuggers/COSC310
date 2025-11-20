from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.core.security import create_access_token, verify_access_token
from app.services import watchlist_service

@pytest.fixture
def mock_watchlist_service(mocker):
    """
    Patches the individual functions imported in the router.
    Returns a dictionary so tests can access each mock specificially.
    """
    mock_get = mocker.patch("app.routers.watchlist.listWatchlist")
    mock_add = mocker.patch("app.routers.watchlist.addBookToWatchlist")
    mock_remove = mocker.patch("app.routers.watchlist.removeBookFromWatchlist")
    
    return {"get": mock_get, "add": mock_add, "remove": mock_remove}

@pytest.fixture
def client():
    def mock_verify_token():
        return {"userid": "test_user_123", "is_admin": False}

    app.dependency_overrides[verify_access_token] = mock_verify_token
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_get_watchlist_empty(client, mock_watchlist_service):
    """Test retrieving an empty watchlist."""
    mock_watchlist_service["get"].return_value = []

    response = client.get("/watchlist")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
    
    mock_watchlist_service["get"].assert_called_with("test_user_123")

def test_post_watchlist_adds(client, mock_watchlist_service):
    """Test adding a book to the watchlist."""
    mock_watchlist_service["add"].return_value = {"isbn": "123", "title": "Test Book"}

    response = client.post("/watchlist", json={"isbn": "123"})

    assert response.status_code == status.HTTP_201_CREATED
    
    mock_watchlist_service["add"].assert_called_with("test_user_123", "123")

def test_delete_watchlist_item(client, mock_watchlist_service):
    """Test deleting a book from the watchlist."""
    mock_watchlist_service["remove"].return_value = None

    response = client.delete("/watchlist/123")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    mock_watchlist_service["remove"].assert_called_with("test_user_123", "123")