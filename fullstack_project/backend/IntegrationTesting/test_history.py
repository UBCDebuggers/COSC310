from datetime import datetime
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.core.security import verify_access_token
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

# Integration Test: Get Last Books Viewed by User
# GET /history/user/{userid}/last
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
    assert "history_items" in data
    assert len(data["history_items"]) == 2
    assert data["history_items"][0]["isbn"] == "isbn1"
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

# GET /history/isbn/{isbn} - Get History by ISBN
def test_get_history_by_isbn_endpoint(client: TestClient, mock_history_services):
    setup_history_auth(is_authenticated=True)
    
    mock_history_services["get_history_by_isbn"].return_value = [
        {
            "userid": "user1",
            "isbn": "isbn123",
            "date": datetime.fromisoformat("2024-01-01T00:00:00")
        }
    ]

    response = client.get("/history/isbn/isbn123")
    
    assert response.status_code == 200
    data = response.json()
    assert "history_items" in data
    assert len(data["history_items"]) == 1
    
    cleanup_history_auth()

# GET /history/user/{userid} - Get History by User ID
def test_get_history_by_userid_endpoint(client: TestClient, mock_history_services):
    setup_history_auth(is_authenticated=True)
    
    mock_history_services["get_history_by_userid"].return_value = [
        {
            "userid": "user1",
            "isbn": "isbn1",
            "date": datetime.fromisoformat("2024-01-03T00:00:00")
        },
        {
            "userid": "user1",
            "isbn": "isbn2",
            "date": datetime.fromisoformat("2024-01-02T00:00:00")
        }
    ]

    response = client.get("/history/user/user1")
    
    assert response.status_code == 200
    data = response.json()
    assert "history_items" in data
    assert len(data["history_items"]) == 2
    
    cleanup_history_auth()

# DELETE /history/delete/{item_id} - Delete History Item
def test_delete_history_item_endpoint_success(client: TestClient, mock_history_services):
    setup_history_auth(is_authenticated=True)
    mock_history_services["delete_history_item"].return_value = None
    
    response = client.delete("/history/delete/item1")
    
    assert response.status_code == 204
    mock_history_services["delete_history_item"].assert_called_once_with("item1")
    
    cleanup_history_auth()

# Delete history without authentication
def test_delete_history_no_authentication(client: TestClient):
    response = client.delete("/history/delete/item1")
    assert response.status_code in [401, 403]
    cleanup_history_auth()
