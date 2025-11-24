from datetime import datetime
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.core.security import verify_access_token
import app.routers.notification as notification_router
from fastapi import HTTPException

# Fixture for client
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_notification_services(mocker):
    mocks = {
        "get_notifications_by_userid": mocker.patch("app.routers.notification.notification_service.get_notifications_by_userid"),
        "add_notification": mocker.patch("app.routers.notification.notification_service.add_notification"),
        "update_notification": mocker.patch("app.routers.notification.notification_service.update_notification"),
        "get_user_by_id": mocker.patch("app.routers.notification.users_service.get_user_by_id"),
        "send_notification_email": mocker.patch("app.routers.notification.send_notification_email"),
    }
    return mocks

# Helper
def setup_notification_auth(is_authenticated: bool = True):    
    if is_authenticated:
        app.dependency_overrides[verify_access_token] = lambda: {
            "user_id": "test_user",
            "is_admin": False
        }
    else:
        app.dependency_overrides.clear()

# Clear all dependency overrides after notification tests
def cleanup_notification_auth():
    app.dependency_overrides.clear()

# Test: Get all notifications for a user
def test_get_user_notifications_success(client: TestClient, mock_notification_services):
    setup_notification_auth(is_authenticated=True)
    
    mock_notification_services["get_notifications_by_userid"].return_value = [
        {
            "userid": "user1",
            "notificationid": "notif1",
            "type": "book_added",
            "message": "New book added to wishlist",
            "timestamp": "2024-01-03T00:00:00",
            "isread": "false",
            "relatedid": "isbn1",
            "category": "wishlist"
        },
        {
            "userid": "user1",
            "notificationid": "notif2",
            "type": "book_available",
            "message": "Book is now available",
            "timestamp": "2024-01-02T00:00:00",
            "isread": "true",
            "relatedid": "isbn2",
            "category": "availability"
        }
    ]
    
    response = client.get("/notifications/user1")
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["notificationid"] == "notif1"
    assert response.json()[1]["notificationid"] == "notif2"
    
    cleanup_notification_auth()

# Test: Get all notifications returns empty list when user has none
def test_get_user_notifications_empty(client: TestClient, mock_notification_services):
    setup_notification_auth(is_authenticated=True)
    
    mock_notification_services["get_notifications_by_userid"].return_value = []
    
    response = client.get("/notifications/user1")
    
    assert response.status_code == 200
    assert response.json() == []
    
    cleanup_notification_auth()

# Test: Get unread notifications with count
def test_get_unread_notifications_success(client: TestClient, mock_notification_services):
    setup_notification_auth(is_authenticated=True)
    
    mock_notification_services["get_notifications_by_userid"].return_value = [
        {
            "userid": "user1",
            "notificationid": "notif1",
            "type": "book_added",
            "message": "New book added",
            "timestamp": "2024-01-03T00:00:00",
            "isread": "false",
            "relatedid": "isbn1",
            "category": "wishlist"
        },
        {
            "userid": "user1",
            "notificationid": "notif2",
            "type": "book_available",
            "message": "Book is available",
            "timestamp": "2024-01-02T00:00:00",
            "isread": "true",
            "relatedid": "isbn2",
            "category": "availability"
        },
        {
            "userid": "user1",
            "notificationid": "notif3",
            "type": "rating_update",
            "message": "Your rating was updated",
            "timestamp": "2024-01-01T00:00:00",
            "isread": "false",
            "relatedid": "isbn3",
            "category": "rating"
        }
    ]
    
    response = client.get("/notifications/user1/unread")
    
    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert len(response.json()["notifications"]) == 2
    
    cleanup_notification_auth()

# Test: Get unread notifications when user has no unread
def test_get_unread_notifications_empty(client: TestClient, mock_notification_services):
    setup_notification_auth(is_authenticated=True)
    
    mock_notification_services["get_notifications_by_userid"].return_value = [
        {
            "userid": "user1",
            "notificationid": "notif1",
            "type": "book_added",
            "message": "New book added",
            "timestamp": "2024-01-01T00:00:00",
            "isread": "true",
            "relatedid": "isbn1",
            "category": "wishlist"
        }
    ]
    
    response = client.get("/notifications/user1/unread")
    
    assert response.status_code == 200
    assert response.json()["count"] == 0
    assert len(response.json()["notifications"]) == 0
    
    cleanup_notification_auth()

# Test: Create notification successfully with email
def test_create_notification_with_email(client: TestClient, mock_notification_services):
    setup_notification_auth(is_authenticated=True)
    
    from app.schemas.user import User
    mock_notification_services["get_user_by_id"].return_value = User(
        userid="user1",
        email="user1@example.com",
        hash_password="hashed",
        is_admin=False,
        department="eng",
        age=25,
        username="user1",
        firstname="John",
        lastname="Doe"
    )
    
    mock_notification_services["add_notification"].return_value = {
        "userid": "user1",
        "notificationid": "notif1",
        "type": "book_added",
        "message": "New book added",
        "timestamp": "2024-01-03T00:00:00",
        "isread": "false",
        "relatedid": "isbn1",
        "category": "wishlist"
    }
    
    response = client.post(
        "/notifications/create",
        params={
            "userid": "user1",
            "notification_type": "book_added",
            "category": "wishlist",
            "message": "New book added",
            "relatedid": "isbn1",
            "send_email": True
        }
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "email queued" in response.json()["message"]
    assert response.json()["notification"]["notificationid"] == "notif1"
    
    cleanup_notification_auth()

# Test: Create notification without email
def test_create_notification_without_email(client: TestClient, mock_notification_services):
    setup_notification_auth(is_authenticated=True)
    
    from app.schemas.user import User
    mock_notification_services["get_user_by_id"].return_value = User(
        userid="user1",
        email="user1@example.com",
        hash_password="hashed",
        is_admin=False,
        department="eng",
        age=25,
        username="user1",
        firstname="John",
        lastname="Doe"
    )
    
    mock_notification_services["add_notification"].return_value = {
        "userid": "user1",
        "notificationid": "notif1",
        "type": "book_added",
        "message": "New book added",
        "timestamp": "2024-01-03T00:00:00",
        "isread": "false",
        "relatedid": "isbn1",
        "category": "wishlist"
    }
    
    response = client.post(
        "/notifications/create",
        params={
            "userid": "user1",
            "notification_type": "book_added",
            "category": "wishlist",
            "message": "New book added",
            "relatedid": "isbn1",
            "send_email": False
        }
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "email queued" not in response.json()["message"]
    
    cleanup_notification_auth()

# Test: Create notification for non-existent user
def test_create_notification_user_not_found(client: TestClient, mock_notification_services):
    setup_notification_auth(is_authenticated=True)
    
    mock_notification_services["get_user_by_id"].side_effect = Exception("User not found")
    
    response = client.post(
        "/notifications/create",
        params={
            "userid": "nonexistent",
            "notification_type": "book_added",
            "category": "wishlist",
            "message": "New book added",
            "relatedid": "isbn1",
            "send_email": False
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    
    cleanup_notification_auth()

# Test: Mark notification as read
def test_mark_notification_as_read_success(client: TestClient, mock_notification_services):
    setup_notification_auth(is_authenticated=True)
    
    mock_notification_services["update_notification"].return_value = {
        "userid": "user1",
        "notificationid": "notif1",
        "type": "book_added",
        "message": "New book added",
        "timestamp": "2024-01-03T00:00:00",
        "isread": "true",
        "relatedid": "isbn1",
        "category": "wishlist"
    }
    
    response = client.put("/notifications/notif1/read")
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["notification"]["isread"] == True
    
    cleanup_notification_auth()

# Test: Mark non-existent notification as read
def test_mark_notification_as_read_not_found(client: TestClient, mock_notification_services):
    setup_notification_auth(is_authenticated=True)
    
    mock_notification_services["update_notification"].return_value = None
    
    response = client.put("/notifications/nonexistent/read")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    
    cleanup_notification_auth()