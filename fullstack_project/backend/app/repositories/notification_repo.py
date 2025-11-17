from pathlib import Path
import csv, os, uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging
import dateutil

logger = logging.getLogger(__name__)

class NotificationRepository:
    DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "notification.csv"

    @classmethod
    def load_all(cls) -> List[Dict[str, Any]]:
        if not cls.DATA_PATH.exists():
            return []
        
        items: List[Dict[str, Any]] = []
        with cls.DATA_PATH.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if 'timestamp' in row and row['timestamp']:
                    orig_ts = row['timestamp']
                    try:
                        if dateutil:
                            row['timestamp'] = dateutil.parser.isoparse(orig_ts)
                        else:
                            ts = orig_ts
                            if isinstance(ts, str) and ts.endswith('Z'):
                                ts = ts.replace('Z', '+00:00')
                            row['timestamp'] = datetime.fromisoformat(ts)
                    except Exception as e:
                        logger.warning("Failed to parse timestamp %r: %s", orig_ts, e)
                items.append(row)
        return items

    # Save all notifications to CSV, with converted datetimes to ISO strings
    @classmethod
    def save_all(cls, notifications: List[Dict[str, Any]]) -> None:
        if not notifications:
            cls.DATA_PATH.unlink(missing_ok=True)
            return

        serializable = []
        for row in notifications:
            r = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in row.items()}
            serializable.append(r)

        fieldnames = list(notifications[0].keys())
        tmp = cls.DATA_PATH.with_suffix(".tmp")

        with tmp.open("w", encoding="latin-1", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(serializable)
        
        os.replace(tmp, cls.DATA_PATH)

    # Adds a new notification
    @classmethod
    def add_notification(cls, userid: str, notification_type: str, category: str, message: str, relatedid: str) -> Dict[str, Any]:    
        notifications = cls.load_all()
        
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
        cls.save_all(notifications)
        return new_notification

    # Gets all notifications for a user, sorted by newest timestamp
    @classmethod
    def get_notifications_by_userid(cls, userid: str) -> List[Dict[str, Any]]:
        notifications = cls.load_all()
        user_notifications = [n for n in notifications if n.get("userid") == userid]
        
        # Sort by timestamp descending
        return sorted(
            user_notifications,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )

    # Gets single notification by id
    @classmethod
    def get_notification_by_id(cls, notificationid: str) -> Optional[Dict[str, Any]]:
        notifications = cls.load_all()
        for notif in notifications:
            if notif.get("notificationid") == notificationid:
                return notif
        return None

    # Update Notification
    @classmethod
    def update_notification(cls, notificationid: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        notifications = cls.load_all()
        
        for i, notif in enumerate(notifications):
            if notif.get("notificationid") == notificationid:
                notifications[i].update(updates)
                cls.save_all(notifications)
                return notifications[i]
        
        return None
    
    # Delete Notification (True -> Deleted, False -> Otherwise)
    @classmethod
    def delete_notification(cls, notificationid: str) -> bool:
        notifications = cls.load_all()
        filtered = [n for n in notifications if n.get("notificationid") != notificationid]
        
        if len(filtered) < len(notifications):
            cls.save_all(filtered)
            return True
        
        return False

    # Delete Read Notifications and returns count
    @classmethod
    def delete_read_notifications(cls, userid: str) -> int:
        notifications = cls.load_all()
        original_count = len(notifications)
        
        # Keep only unread or non-matching-userid
        filtered = [
            n for n in notifications
            if not (n.get("userid") == userid and n.get("isread") == "true")
        ]
        
        deleted_count = original_count - len(filtered)
        if deleted_count > 0:
            cls.save_all(filtered)
        
        return deleted_count


# Module-level wrapper functions for convenience
DATA_PATH = NotificationRepository.DATA_PATH


def add_notification(userid: str, notification_type: str, category: str, message: str, relatedid: str) -> Dict[str, Any]:
    return NotificationRepository.add_notification(userid, notification_type, category, message, relatedid)


def get_notifications_by_userid(userid: str) -> List[Dict[str, Any]]:
    return NotificationRepository.get_notifications_by_userid(userid)


def get_notification_by_id(notificationid: str) -> Optional[Dict[str, Any]]:
    return NotificationRepository.get_notification_by_id(notificationid)


def update_notification(notificationid: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return NotificationRepository.update_notification(notificationid, updates)


def delete_notification(notificationid: str) -> bool:
    return NotificationRepository.delete_notification(notificationid)


def delete_read_notifications(userid: str) -> int:
    return NotificationRepository.delete_read_notifications(userid)