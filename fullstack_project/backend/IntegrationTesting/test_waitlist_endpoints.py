import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services import waitlist_service
import app.repositories.waitlist_repo as waitlist_repo
import app.repositories.notification_repo as notification_repo
from app.services import email_service

@pytest.fixture
def client(tmp_path, monkeypatch):
    # patch CSV paths to tmp
    monkeypatch.setattr(waitlist_repo.WaitlistRepository, "DATA_PATH", tmp_path / "waitlist.csv")
    monkeypatch.setattr(notification_repo.NotificationRepository, "DATA_PATH", tmp_path / "notification.csv")
    monkeypatch.setattr(notification_repo, "DATA_PATH", tmp_path / "notification.csv")

    # patch email to prevent real sending
    monkeypatch.setattr(email_service, "send_notification_email", lambda *a, **k: None)

    return TestClient(app)

def test_waitlist_endpoints_integration(client):
    # join waitlist
    r = client.post("/waitlist/isbn-abc/join", json={"userid": "student1", "email": "s1@example.com"})
    assert r.status_code in (200, 201)

    # mark book available
    r2 = client.post("/books/isbn-abc/available")
    assert r2.status_code == 200

    # check waitlist cleared
    r3 = client.get("/waitlist/isbn-abc")
    assert r3.status_code == 200
    data = r3.json()
    assert len(data) == 0  # should be empty after notification