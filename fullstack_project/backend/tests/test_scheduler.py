import pytest
from datetime import datetime, timedelta, timezone
import app.repositories.borrowings_repo as br
import app.repositories.notification_repo as nr
import app.repositories.users_repo as ur
import app.services.email_service as es
import app.services.scheduler_service as ss

# Schedule should create reminders 2 days before due date and overdue notification > 24 hours
def test_scheduler_due_and_overdue_triggers(tmp_path, monkeypatch):
    monkeypatch.setattr(br.BorrowingsRepository, "DATA_PATH", tmp_path / "borrowings.csv")
    monkeypatch.setattr(nr, "DATA_PATH", tmp_path / "notification.csv")
    monkeypatch.setattr(ur, "DATA_PATH", tmp_path / "users.csv")
    
    now = datetime.now(timezone.utc)

    # Create test users with emails
    ur.save_all([
        {"userid": "student1", "email": "student1@example.com", "hash_password": "hashed", "is_admin": "false", 
         "department": "CS", "age": "20", "username": "student1", "firstname": "Test", "lastname": "Student1"},
        {"userid": "student2", "email": "student2@example.com", "hash_password": "hashed", "is_admin": "false",
         "department": "CS", "age": "20", "username": "student2", "firstname": "Test", "lastname": "Student2"}
    ])
    
    due_in_2 = (now + timedelta(days=2)).isoformat()
    br.add_borrowing("borrow1", "student1", "isbn-111", now.isoformat(), due_in_2, "")

    sent = []
    def fake_send(to_email, notification_type, category, message):
        sent.append((to_email, notification_type, category, message))
    monkeypatch.setattr(es, "send_notification_email", fake_send)

    ss.run_due_reminders()
    assert len(sent) >= 1

    sent.clear()
    overdue_due = (now - timedelta(days=2)).isoformat()
    br.add_borrowing("borrow2", "student2", "isbn-222", (now - timedelta(days=10)).isoformat(), overdue_due, "")
    ss.run_overdue_checks()
    assert len(sent) >= 1