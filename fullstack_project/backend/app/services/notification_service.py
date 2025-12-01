import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.repositories import notification_repo

def add_notification(userid: str, notification_type: str, category: str, message: str, relatedid: str) -> Dict[str, Any]:
    notifications = notification_repo.load_all()

    new_notification = {
        "userid": userid,
        "notificationid": str(uuid.uuid4()),
        "type": notification_type,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "isread": "false",
        "relatedid": relatedid,
        "category": category
    }
    notifications.append(new_notification)
    notification_repo.save_all(notifications)
    return new_notification

def get_notifications_by_userid(userid: str) -> List[Dict[str, Any]]:
    notifications = notification_repo.load_all()
    user_notifications = [n for n in notifications if n.get("userid") == userid]

    return sorted(
        user_notifications,
        key=lambda x: x.get("timestamp", ""),
        reverse=True
    )

def get_notification_by_id(notificationid: str) -> Optional[Dict[str, Any]]:
    notifications = notification_repo.load_all()
    for notif in notifications:
        if notif.get("notificationid") == notificationid:
            return notif
    return None

def update_notification(notificationid: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    notifications = notification_repo.load_all()

    for i, notif in enumerate(notifications):
        if notif.get("notificationid") == notificationid:
            notifications[i].update(updates)
            notification_repo.save_all(notifications)
            return notifications[i]

    return None

def delete_notification(notificationid: str) -> bool:
    notifications = notification_repo.load_all()
    filtered = [n for n in notifications if n.get("notificationid") != notificationid]

    if len(filtered) < len(notifications):
        notification_repo.save_all(filtered)
        return True

    return False

def delete_read_notifications(userid: str) -> int:
    notifications = notification_repo.load_all()
    original_count = len(notifications)

    filtered = [
        n for n in notifications
        if not (n.get("userid") == userid and n.get("isread") == "true")
    ]

    deleted_count = original_count - len(filtered)
    if deleted_count > 0:
        notification_repo.save_all(filtered)
    return deleted_count