import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.services import watchlist_service, ratedBooks_service

client = TestClient(app)
USER_ID = "user1"

@pytest.fixture(autouse=True)
# Create fake data files for testing
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
        f"user_id;isbn;created_on\n{USER_ID};123;2025-01-01\n",
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
    token = create_access_token({"sub": USER_ID, "admin": "no"})
    return {"Authorization": f"Bearer {token}"}

# Tests for ratedBooks endpoints
def test_rate_book_endpoint(auth_header):
    resp = client.post("/rated-books", json={"isbn": "123", "score": 9}, headers=auth_header)
    assert resp.status_code == 201
    get_resp = client.get("/rated-books", headers=auth_header)
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert len(body) == 1
    assert body[0]["isbn"] == "123"

def test_rate_book_rejects_duplicate(auth_header):
    client.post("/rated-books", json={"isbn": "123", "score": 7}, headers=auth_header)
    resp = client.post("/rated-books", json={"isbn": "123", "score": 8}, headers=auth_header)
    assert resp.status_code == 409

def test_rate_book_rejects_out_of_range(auth_header):
    resp = client.post("/rated-books", json={"isbn": "123", "score": 11}, headers=auth_header)
    assert resp.status_code == 422
    detail = resp.json()["detail"][0]
    assert detail["type"] == "less_than_equal"