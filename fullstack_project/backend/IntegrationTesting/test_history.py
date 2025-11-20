from datetime import datetime
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.core.security import verify_access_token

# Fixture for client
@pytest.fixture
def client():
    return TestClient(app)

# Helper to set up authentication
def setup_history_auth(is_authenticated: bool = True):    
    if is_authenticated:
        app.dependency_overrides[verify_access_token] = lambda: {
            "user_id": "test_user",
            "is_admin": False
        }
    else:
        app.dependency_overrides.clear()

# Clean up dependency overrides after each test
@pytest.fixture(autouse=True)
def cleanup_auth():
    yield
    app.dependency_overrides.clear()

# Integration Test: Get Last Books Viewed by User
# GET /history/user/{userid}/last
def test_get_last_books_endpoint_authenticated(client: TestClient, mocker):
    setup_history_auth(is_authenticated=True)
    
    mock_get_last_books = mocker.patch("app.routers.history.get_last_books")
    mock_get_last_books.return_value = [
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
    mock_get_last_books.assert_called_once_with("user1", 10)

# GET /history/user/{userid}/last with custom limit
def test_get_last_books_with_custom_limit(client: TestClient, mocker):
    setup_history_auth(is_authenticated=True)
    mock_get_last_books = mocker.patch("app.routers.history.get_last_books")
    mock_get_last_books.return_value = []
    
    response = client.get("/history/user/user1/last?limit=5")
    
    assert response.status_code == 200
    mock_get_last_books.assert_called_once_with("user1", 5)

# GET /history/user/{userid}/last without authentication
def test_get_last_books_no_authentication(client: TestClient):
    app.dependency_overrides.clear()
    
    response = client.get("/history/user/user1/last")
    assert response.status_code in [401, 403]

# DELETE /history/delete/{item_id} - Delete History Item
def test_delete_history_item_endpoint_success(client: TestClient, mocker):
    setup_history_auth(is_authenticated=True)
    mock_delete = mocker.patch("app.routers.history.delete_history_item")
    mock_delete.return_value = None
    
    response = client.delete("/history/delete/item1")
    
    assert response.status_code == 204
    mock_delete.assert_called_once_with("item1")

# Delete history without authentication
def test_delete_history_no_authentication(client: TestClient):
    app.dependency_overrides.clear()
    
    response = client.delete("/history/delete/item1")
    assert response.status_code in [401, 403]

