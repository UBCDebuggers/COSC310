import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.services import watchlist_service, ratedBooks_service

client = TestClient(app)
USER_ID = "user1"


@pytest.fixture(autouse=True)
def isolate_data(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    books = data_dir / "books.csv"
    books.write_text(
        "isbn;title;author;year_of_publication;publisher;img_url_s;img_url_m;img_url_l\n"
        "123;Example Book;Author;2001;Pub;img;img;img\n",
        encoding="utf-8",
    )
    watchlists = data_dir / "watchlists.csv"
    watchlists.write_text(
        "user_id;isbn;created_on\n"
        f"{USER_ID};123;2025-01-01\n"
        "other;123;2025-01-02\n",
        encoding="utf-8",
    )
    rated = data_dir / "ratedBooks.csv"
    rated.write_text("user_id;isbn;score;created_on\n", encoding="utf-8")

    monkeypatch.setattr(watchlist_service, "BOOKS_PATH", str(books))
    monkeypatch.setattr(watchlist_service, "WATCHLIST_PATH", str(watchlists))
    monkeypatch.setattr(ratedBooks_service, "ratedBooks_repo",
                        __import__("app.repositories.ratedBooks_repo", fromlist=[""]))
    monkeypatch.setattr(ratedBooks_service.ratedBooks_repo, "RATED_PATH", rated)


@pytest.fixture
def auth_header():
    token = create_access_token({"sub": USER_ID, "admin": False})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_header():
    token = create_access_token({"sub": "admin", "admin": True})
    return {"Authorization": f"Bearer {token}"}


def test_get_rateable_options(auth_header):
    resp = client.get("/rated-books/options", headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()[0]["isbn"] == "123"


def test_rate_update_and_delete(auth_header, admin_header):
    resp = client.post("/rated-books", json={"isbn": "123", "score": 9}, headers=auth_header)
    assert resp.status_code == 201
    put_resp = client.put("/rated-books/123", json={"score": 5}, headers=auth_header)
    assert put_resp.status_code == 200
    assert put_resp.json()["score"] == 5
    del_resp = client.delete("/rated-books/123", headers=auth_header)
    assert del_resp.status_code == 204
    client.post("/rated-books", json={"isbn": "123", "score": 7}, headers=auth_header)
    admin_del = client.delete("/rated-books/users/user1/123", headers=admin_header)
    assert admin_del.status_code == 204


def test_permissions_enforced(auth_header):
    client.post("/rated-books", json={"isbn": "123", "score": 7}, headers=auth_header)
    other_token = create_access_token({"sub": "other", "admin": False})
    other_headers = {"Authorization": f"Bearer {other_token}"}
    resp = client.put("/rated-books/123?user_id=user1", json={"score": 4}, headers=other_headers)
    assert resp.status_code == 403
    resp = client.delete("/rated-books/123?user_id=user1", headers=other_headers)
    assert resp.status_code == 403
