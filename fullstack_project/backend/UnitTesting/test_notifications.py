import app.repositories.notification_repo as nr
from fastapi.testclient import TestClient
from app.main import app

# If you mark a notification as read, the "isread" should be updated
def test_mark_notification_as_read(tmp_path, monkeypatch):
    monkeypatch.setattr(nr, "DATA_PATH", tmp_path / "notification.csv")

    n = nr.add_notification("student9", "test", "info", "please read", "related1")

    client = TestClient(app)
    r = client.put(f"/notifications/{n['notificationid']}/read")
    assert r.status_code == 200

    r2 = client.get("/notifications/student9")
    data = r2.json()
    assert any(n2["notificationid"] == n["notificationid"] and n2.get("isread") in (True, "true", "True") for n2 in data)
