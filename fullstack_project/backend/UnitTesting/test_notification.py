import unittest
import pytest
from fastapi import HTTPException
from datetime import datetime, timezone
from app.services.notification_service import (
    add_notification,
    get_notifications_by_userid,
    get_notification_by_id,
    update_notification,
    delete_notification,
    delete_read_notifications,
)
from app.schemas.notification import Notification
from app.repositories import notification_repo
from unittest.mock import MagicMock, patch

# Mock Repository
@pytest.fixture
def mock_notification_repo(monkeypatch):
    class MockRepo:
        load_all = MagicMock()
        save_all = MagicMock()

    monkeypatch.setattr(notification_repo, "load_all", MockRepo.load_all)
    monkeypatch.setattr(notification_repo, "save_all", MockRepo.save_all)

    return MockRepo

# Adding a notification with valid inputs
def test_add_notification_success(mock_notification_repo):
    mock_notification_repo.load_all.return_value = []
    mock_notification_repo.save_all.return_value = None
    
    result = add_notification(
        userid="user1",
        notification_type="book_added",
        category="wishlist",
        message="Book added to wishlist",
        relatedid="isbn1"
    )
    
    assert result["userid"] == "user1"
    assert result["type"] == "book_added"
    assert result["category"] == "wishlist"
    assert result["message"] == "Book added to wishlist"
    assert result["relatedid"] == "isbn1"
    assert result["isread"] == "false"
    assert "notificationid" in result
    assert "timestamp" in result
    mock_notification_repo.save_all.assert_called_once()

# Getting notifications by userid - returns sorted by timestamp descending
def test_get_notifications_by_userid_sorted(mock_notification_repo):
    mock_notification_repo.load_all.return_value = [
        {
            "userid": "user1",
            "notificationid": "notif1",
            "type": "book_added",
            "message": "Book 1 added",
            "timestamp": "2024-01-01T00:00:00",
            "isread": "false",
            "relatedid": "isbn1",
            "category": "wishlist"
        },
        {
            "userid": "user1",
            "notificationid": "notif2",
            "type": "book_available",
            "message": "Book 2 available",
            "timestamp": "2024-01-03T00:00:00",  # Newest
            "isread": "true",
            "relatedid": "isbn2",
            "category": "availability"
        },
        {
            "userid": "user2",
            "notificationid": "notif3",
            "type": "rating_update",
            "message": "Rating updated",
            "timestamp": "2024-01-02T00:00:00",
            "isread": "false",
            "relatedid": "isbn3",
            "category": "rating"
        },
        {
            "userid": "user1",
            "notificationid": "notif4",
            "type": "book_returned",
            "message": "Book returned",
            "timestamp": "2024-01-02T00:00:00",
            "isread": "false",
            "relatedid": "isbn4",
            "category": "library"
        }
    ]
    
    result = get_notifications_by_userid("user1")
    
    assert len(result) == 3
    assert result[0]["notificationid"] == "notif2"  # Newest first
    assert result[1]["notificationid"] == "notif4"
    assert result[2]["notificationid"] == "notif1"  # Oldest last

# Getting notifications for user with no notifications
def test_get_notifications_by_userid_empty(mock_notification_repo):
    mock_notification_repo.load_all.return_value = [
        {
            "userid": "user2",
            "notificationid": "notif1",
            "type": "book_added",
            "message": "Book added",
            "timestamp": "2024-01-01T00:00:00",
            "isread": "false",
            "relatedid": "isbn1",
            "category": "wishlist"
        }
    ]
    
    result = get_notifications_by_userid("user1")
    
    assert len(result) == 0

# Updating a notification
def test_update_notification_success(mock_notification_repo):
    mock_notification_repo.load_all.return_value = [
        {
            "userid": "user1",
            "notificationid": "notif1",
            "type": "book_added",
            "message": "Book added",
            "timestamp": "2024-01-01T00:00:00",
            "isread": "false",
            "relatedid": "isbn1",
            "category": "wishlist"
        }
    ]
    mock_notification_repo.save_all.return_value = None
    
    result = update_notification("notif1", {"isread": "true"})
    
    assert result is not None
    assert result["notificationid"] == "notif1"
    assert result["isread"] == "true"
    mock_notification_repo.save_all.assert_called_once()

# Deleting a notification
def test_delete_notification_success(mock_notification_repo):
    mock_notification_repo.load_all.return_value = [
        {
            "userid": "user1",
            "notificationid": "notif1",
            "type": "book_added",
            "message": "Book added",
            "timestamp": "2024-01-01T00:00:00",
            "isread": "false",
            "relatedid": "isbn1",
            "category": "wishlist"
        },
        {
            "userid": "user1",
            "notificationid": "notif2",
            "type": "book_available",
            "message": "Book available",
            "timestamp": "2024-01-02T00:00:00",
            "isread": "true",
            "relatedid": "isbn2",
            "category": "availability"
        }
    ]
    mock_notification_repo.save_all.return_value = None
    
    result = delete_notification("notif1")
    
    assert result is True
    mock_notification_repo.save_all.assert_called_once()
    # Verify the saved list has only notif2
    saved_list = mock_notification_repo.save_all.call_args[0][0]
    assert len(saved_list) == 1
    assert saved_list[0]["notificationid"] == "notif2"

# Deleting read notifications for specific user
def test_delete_read_notifications_success(mock_notification_repo):
    mock_notification_repo.load_all.return_value = [
        {
            "userid": "user1",
            "notificationid": "notif1",
            "type": "book_added",
            "message": "Book added",
            "timestamp": "2024-01-01T00:00:00",
            "isread": "true",  # Will be deleted
            "relatedid": "isbn1",
            "category": "wishlist"
        },
        {
            "userid": "user1",
            "notificationid": "notif2",
            "type": "book_available",
            "message": "Book available",
            "timestamp": "2024-01-02T00:00:00",
            "isread": "false",  # Won't be deleted
            "relatedid": "isbn2",
            "category": "availability"
        },
        {
            "userid": "user1",
            "notificationid": "notif3",
            "type": "rating_update",
            "message": "Rating updated",
            "timestamp": "2024-01-03T00:00:00",
            "isread": "true",  # Will be deleted
            "relatedid": "isbn3",
            "category": "rating"
        },
        {
            "userid": "user2",
            "notificationid": "notif4",
            "type": "book_returned",
            "message": "Book returned",
            "timestamp": "2024-01-04T00:00:00",
            "isread": "true",  # Won't be deleted (different user)
            "relatedid": "isbn4",
            "category": "library"
        }
    ]
    mock_notification_repo.save_all.return_value = None
    
    result = delete_read_notifications("user1")
    
    assert result == 2  # 2 read notifications deleted for user1
    mock_notification_repo.save_all.assert_called_once()
    # Verify the saved list has notif2 and notif4 only
    saved_list = mock_notification_repo.save_all.call_args[0][0]
    assert len(saved_list) == 2
    saved_ids = {n["notificationid"] for n in saved_list}
    assert saved_ids == {"notif2", "notif4"}

#  Deleting read notifications when user has none
def test_delete_read_notifications_empty(mock_notification_repo):
    mock_notification_repo.load_all.return_value = [
        {
            "userid": "user1",
            "notificationid": "notif1",
            "type": "book_added",
            "message": "Book added",
            "timestamp": "2024-01-01T00:00:00",
            "isread": "false",
            "relatedid": "isbn1",
            "category": "wishlist"
        }
    ]
    
    result = delete_read_notifications("user1")
    
    assert result == 0
    mock_notification_repo.save_all.assert_not_called()