# For sending due and overdue notifications."""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Callable
from app.repositories import borrowings_repo as br
from app.repositories import notification_repo as nr
from app.repositories import users_repo as ur
from app.services import email_service as es

logger = logging.getLogger(__name__)

# Converts string/datetime to datetime object (reduces code duplication)
def _ensure_datetime(value: any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except Exception as e:
            logger.warning(f"Failed to parse datetime {value}: {e}")
            return None
    return None

# Create a notification and attempts sending email (True -> Successful, False -> Otherwise)
def _create_and_notify(userid: str, notif_type: str, category: str, message: str, relatedid: str, user_email: str) -> bool:
    try:
        nr.add_notification(userid, notif_type, category, message, relatedid)
        es.send_notification_email(user_email, notif_type, category, message)
        return True
    except Exception as e:
        logger.error(f"Failed to create notification for {userid}: {e}")
        return False

# Find borrowings due in ~2 days, create/send reminders, and returns number of reminders
def run_due_reminders() -> int:
    now = datetime.now(timezone.utc)
    target_start = now + timedelta(days=1.5)
    target_end = now + timedelta(days=2.5)
    
    count = 0
    for b in br.get_all_borrowings():
        due = _ensure_datetime(b.get('due_at'))
        returned = _ensure_datetime(b.get('returned_at'))
    
        if not due or returned:
            continue
        
        if target_start <= due <= target_end:
            userid = b.get('userid')
            borrowid = b.get('borrowid')
            isbn = b.get('isbn')
            message = f"Reminder: your borrowed book (ISBN: {isbn}) is due on {due.isoformat()}"
            
            user = ur.get_user_by_id(userid)
            user_email = user.get('email') if user else None
            if user_email and _create_and_notify(userid, 'due_reminder', 'borrow', message, borrowid, user_email):
                count += 1
            elif not user_email:
                logger.warning(f"Could not send reminder for user {userid}: email not found")
    
    logger.info(f"run_due_reminders: created {count} reminders")
    return count

# Find borrowings overdue > 24 hours and notify users (returns no. of overdue notifications)
def run_overdue_checks() -> int:
    now = datetime.now(timezone.utc)
    count = 0
    
    for b in br.get_all_borrowings():
        due = _ensure_datetime(b.get('due_at'))
        returned = _ensure_datetime(b.get('returned_at'))

        if not due or returned:
            continue
        
        overdue_delta = now - due
        if overdue_delta > timedelta(hours=24):
            userid = b.get('userid')
            borrowid = b.get('borrowid')
            isbn = b.get('isbn')
            message = f"Overdue: your borrowed book (ISBN: {isbn}) was due on {due.isoformat()}. Please return it immediately."
            
            user = ur.get_user_by_id(userid)
            user_email = user.get('email') if user else None
            if user_email and _create_and_notify(userid, 'overdue', 'borrow', message, borrowid, user_email):
                count += 1
            elif not user_email:
                logger.warning(f"Could not send overdue notification for user {userid}: email not found")
    
    logger.info(f"run_overdue_checks: created {count} overdue notifications")
    return count