from datetime import datetime
import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.core.security import verify_access_token
import app.routers.history as history_router
from fastapi import HTTPException

# Fixture for client
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_history_services(mocker):
    mocks = {
        "get_last_books": mocker.patch("app.routers.history.get_last_books"),
        "get_history_by_isbn": mocker.patch("app.routers.history.get_history_by_isbn"),
        "get_history_by_userid": mocker.patch("app.routers.history.get_history_by_userid"),
        "delete_history_item": mocker.patch("app.routers.history.delete_history_item"),
    }

    return mocks


# Helper
def setup_history_auth(is_authenticated: bool = True):    
    if is_authenticated:
        app.dependency_overrides[verify_access_token] = lambda: {
            "user_id": "test_user",
            "is_admin": False
        }
    else:
        app.dependency_overrides.clear()

# Clear all dependency overrides after history tests
def cleanup_history_auth():
    app.dependency_overrides.clear()

@pytest.mark.skip
def test_get_last_books_endpoint_authenticated(client: TestClient, mock_history_services):
    setup_history_auth(is_authenticated=True)
    
    mock_history_services["get_last_books"].return_value = [
        {
            "userid": "user1",
            "isbn": "isbn1",
            "date": datetime.fromisoformat("2024-01-03T00:00:00")
        },
        {
            "userid": "user1",
            "isbn": "isbn2",
            "date": datetime.fromisoformat("2024-01-02T00:00:00")
        },
    ]

    response = client.get("/history/user/user1/last?limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 2
    assert data["items"][0]["isbn"] == "isbn1"
    mock_history_services["get_last_books"].assert_called_once_with("user1", 10)
    
    cleanup_history_auth()

# GET /history/user/{userid}/last with custom limit
def test_get_last_books_with_custom_limit(client: TestClient, mock_history_services):
    setup_history_auth(is_authenticated=True)
    mock_history_services["get_last_books"].return_value = []
    response = client.get("/history/user/user1/last?limit=5")
    mock_history_services["get_last_books"].assert_called_once_with("user1", 5)
    cleanup_history_auth()

# GET /history/user/{userid}/last without authentication
def test_get_last_books_no_authentication(client: TestClient):
    response = client.get("/history/user/user1/last")
    assert response.status_code in [401, 403]
    cleanup_history_auth()

# Integration Test: Get History by ISBN
# GET /history/isbn/{isbn}
@pytest.mark.skip
def test_get_history_by_isbn_endpoint(client: TestClient, mock_history_services):
    setup_history_auth(is_authenticated=True)

    mock_history_services["get_history_by_isbn"].return_value = [
        {"userid": "user1", "isbn": "isbn123", "date": datetime.now()},
        {"userid": "user2", "isbn": "isbn123", "date": datetime.now()},
        {"userid": "user3", "isbn": "isbn123", "date": datetime.now()},
    ]

    response = client.get("/history/isbn/isbn123")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert all(item["isbn"] == "isbn123" for item in data["items"])
    mock_history_services["get_history_by_isbn"].assert_called_once_with("isbn123")
    cleanup_history_auth()

# GET /history/isbn/{isbn} when ISBN not found
def test_get_history_by_isbn_not_found(client: TestClient, mock_history_services):    
    setup_history_auth(is_authenticated=True)
    mock_history_services["get_history_by_isbn"].side_effect = HTTPException(
        status_code=404,
        detail="History for ISBN 'nonexistent' not found"
    )

    response = client.get("/history/isbn/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    
    cleanup_history_auth()

# Integration Test: Get History by User ID
# GET /history/user/{userid}
@pytest.mark.skip
def test_get_history_by_userid_endpoint(client: TestClient, mock_history_services):
    setup_history_auth(is_authenticated=True)
    mock_history_services["get_history_by_userid"].return_value = [
        {"userid": "user1", "isbn": f"isbn{i}", "date": datetime.now()}
        for i in range(1, 6)
    ]
    response = client.get("/history/user/user1")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert all(item["userid"] == "user1" for item in data["items"])
    mock_history_services["get_history_by_userid"].assert_called_once_with("user1")
    
    cleanup_history_auth()

# GET /history/user/{userid} for user with no history
def test_get_history_by_userid_not_found(client: TestClient, mock_history_services):    
    setup_history_auth(is_authenticated=True)
    mock_history_services["get_history_by_userid"].side_effect = HTTPException(
        status_code=404,
        detail="History for UserID 'nonexistent_user' not found"
    )
    response = client.get("/history/user/nonexistent_user")
    assert response.status_code == 404
    
    cleanup_history_auth()

# Integration Test: Delete History Item
# DELETE /history/delete/{item_id}
def test_delete_history_item_endpoint_success(client: TestClient, mock_history_services):
    setup_history_auth(is_authenticated=True)
    mock_history_services["delete_history_item"].return_value = None
    response = client.delete("/history/delete/item_id_123")
    assert response.status_code == 204
    assert response.content == b''  
    mock_history_services["delete_history_item"].assert_called_once_with("item_id_123")
    cleanup_history_auth()

# DELETE /history/delete/{item_id} for non-existent item
def test_delete_history_item_not_found(client: TestClient, mock_history_services):
    setup_history_auth(is_authenticated=True)
    mock_history_services["delete_history_item"].side_effect = HTTPException(
        status_code=404,
        detail="History item 'nonexistent' not found"
    )
    response = client.delete("/history/delete/nonexistent")
    assert response.status_code == 404
    
    cleanup_history_auth()

# DELETE /history/delete/{item_id} without authentication
def test_delete_history_no_authentication(client: TestClient):
    response = client.delete("/history/delete/item_id_123")
    assert response.status_code in [401, 403]
    cleanup_history_auth()