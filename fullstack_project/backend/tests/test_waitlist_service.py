import pytest
import app.repositories.waitlist_repo as wr
import app.repositories.notification_repo as nr
import app.services.email_service as es
import app.services.waitlist_service as ws

# TDD: with two waitlist entries, notify_waitlist should create notifications and call email send
def test_notify_waitlist_creates_notifications_and_sends_emails(tmp_path, monkeypatch):
    # isolate CSV files
    monkeypatch.setattr(wr.WaitlistRepository, "DATA_PATH", tmp_path / "waitlist.csv")
    monkeypatch.setattr(nr, "DATA_PATH", tmp_path / "notification.csv")

    # add two waitlist entries
    wr.add_to_waitlist("studentA", "isbn-xyz", "a@example.com")
    wr.add_to_waitlist("studentB", "isbn-xyz", "b@example.com")

    sent = []

    def fake_send(to_email, notification_type, category, message):
        sent.append((to_email, notification_type, category, message))

    monkeypatch.setattr(es, "send_notification_email", fake_send)

    # Call the service that should notify waitlisted users
    ws.notify_waitlist("isbn-xyz")

    # Expect two emails sent and two notifications created
    assert len(sent) == 2
    notifs = nr.get_notifications_by_userid("studentA") + nr.get_notifications_by_userid("studentB")
    assert len(notifs) >= 2
