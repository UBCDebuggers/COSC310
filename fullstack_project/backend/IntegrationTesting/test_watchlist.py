from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token
from app.services import watchlist_service

client = TestClient(app)
TEST_USER_ID = "f70517e2-90eb-4013-bd43-40c799d82a79"

@pytest.fixture(autouse=True)
def isolate_csvs(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    books_path = data_dir / "books.csv"
    watchlists_path = data_dir / "watchlists.csv"

    books_path.write_text(
        "isbn;title;author;year_of_publication;publisher;img_url_s;img_url_m;img_url_l\n"
        "123;Example Book;Author A;2000;Publisher;imgS;imgM;imgL\n"
        "456;Second Book;Author B;2001;Publisher;imgS;imgM;imgL\n",
        encoding="utf-8",
    )
    watchlists_path.write_text("user_id;isbn;created_on\n", encoding="utf-8")

    monkeypatch.setattr(watchlist_service, "DATA_DIR", str(data_dir))
    monkeypatch.setattr(watchlist_service, "BOOKS_PATH", str(books_path))
    monkeypatch.setattr(watchlist_service, "WATCHLIST_PATH", str(watchlists_path))
    yield


@pytest.fixture
def auth_header():
    token = create_access_token({"sub": TEST_USER_ID, "admin": "no"})
    return {"Authorization": f"Bearer {token}"}


def test_get_watchlist_returns_seeded_rows(auth_header):
    Path(watchlist_service.WATCHLIST_PATH).write_text(
        "user_id;isbn;created_on\n"
        f"{TEST_USER_ID};123;2025-11-12\n",
        encoding="utf-8",
    )

    resp = client.get("/watchlist", headers=auth_header)

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["isbn"] == "123"
    assert body[0]["title"] == "Example Book"


def test_post_watchlist_adds_entry(auth_header):
    resp = client.post("/watchlist", json={"isbn": "456"}, headers=auth_header)

    assert resp.status_code == 201
    data = resp.json()
    assert data["isbn"] == "456"
    get_resp = client.get("/watchlist", headers=auth_header)
    assert get_resp.status_code == 200
    assert any(item["isbn"] == "456" for item in get_resp.json())


def test_delete_watchlist_removes_only_target(auth_header):
    Path(watchlist_service.WATCHLIST_PATH).write_text(
        "user_id;isbn;created_on\n"
        f"{TEST_USER_ID};123;2025-11-12\n"
        f"{TEST_USER_ID};456;2025-11-13\n",
        encoding="utf-8",
    )

    del_resp = client.delete("/watchlist/123", headers=auth_header)
    assert del_resp.status_code == 204

    remaining = client.get("/watchlist", headers=auth_header).json()
    assert len(remaining) == 1
    assert remaining[0]["isbn"] == "456"