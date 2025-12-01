from fastapi.testclient import TestClient
from app.main import app
from app.core.security import verify_access_token
from app.services import analytics_service
from app.repositories import analytics_repo

def override_admin():
    return {"userid": "admin", "is_admin": True}

def override_user():
    return {"userid": "u1", "is_admin": False}


# GET /analytics
def test_get_all_analytics_success(temp_env, monkeypatch):
    app.dependency_overrides[verify_access_token] = override_admin

    monkeypatch.setattr(analytics_repo, "load_all", lambda: [{"id": "1"}])

    client = TestClient(app)
    res = client.get("/analytics")

    assert res.status_code == 200
    assert res.json() == [{"id": "1"}]

    app.dependency_overrides = {}


def test_get_all_analytics_empty(temp_env, monkeypatch):
    app.dependency_overrides[verify_access_token] = override_admin
    monkeypatch.setattr(analytics_repo, "load_all", lambda: [])

    client = TestClient(app)
    res = client.get("/analytics")

    assert res.status_code == 404
    app.dependency_overrides = {}

# DELETE /analytics
def test_delete_analytics_success(monkeypatch):
    app.dependency_overrides[verify_access_token] = override_admin
    monkeypatch.setattr(analytics_repo, "save_all", lambda x: None)

    client = TestClient(app)
    res = client.delete("/analytics")

    assert res.status_code == 204

    app.dependency_overrides = {}


# GET /analytics/top-rated
def test_top_rated_books(monkeypatch):
    app.dependency_overrides[verify_access_token] = override_admin
    monkeypatch.setattr(analytics_service.get_top_rated_books, "__call__", lambda n: [{"isbn": "111"}])

    monkeypatch.setattr(analytics_service, "get_top_rated_books", lambda n: [{"isbn": "111"}])

    client = TestClient(app)
    res = client.get("/analytics/top-rated?n=5")

    assert res.status_code == 200
    assert res.json() == [{"isbn": "111"}]

    app.dependency_overrides = {}


# GET /analytics/trending
def test_trending_requires_admin():
    app.dependency_overrides[verify_access_token] = override_user

    client = TestClient(app)
    res = client.get("/analytics/trending")

    assert res.status_code == 403

    app.dependency_overrides = {}


def test_trending_success(monkeypatch):
    app.dependency_overrides[verify_access_token] = override_admin
    monkeypatch.setattr(analytics_service, "get_trending_books", lambda n: [{"isbn": "123"}])

    client = TestClient(app)
    res = client.get("/analytics/trending?n=3")

    assert res.status_code == 200
    assert res.json() == [{"isbn": "123"}]

    app.dependency_overrides = {}


# GET /analytics/genres
def test_genres_success(monkeypatch):
    app.dependency_overrides[verify_access_token] = override_admin
    monkeypatch.setattr(analytics_service, "get_genre_popularity", lambda: {"fantasy": 100})

    client = TestClient(app)
    res = client.get("/analytics/genres")

    assert res.status_code == 200
    assert res.json() == {"fantasy": 100}

    app.dependency_overrides = {}
