from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import MagicMock
from fastapi import HTTPException, status
import pytest
from app.schemas.reservation import RETURNED, RETURNED_OVERDUE
from app.services.notification_service import add_notification, get_notification_by_id, get_notifications_by_userid, update_notification, delete_notification, delete_read_notifications

MOCK_PATH = {
    'add_notification': 'app.services.notification_service.add_notification',
    'get_notification_by_userid': 'app.services.notification_service.get_notification_by_userid',
    'get_notification_by_id': 'app.services.notification_service.get_notification_by_id',
    'update_notification': 'app.services.notification_service.update_notification',
    'delete_notification': 'app.services.notification_service.delete_notification',
    'delete_read_notifications': 'app.services.notification_service.delete_read_notifications',
}

class MockNotification:
    def __init__(self, )