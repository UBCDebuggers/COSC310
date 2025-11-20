import pytest
from datetime import date
from app.services import ratedBooks_service, watchlist_service

@pytest.fixture
# Create fake data files for testing
def fake_data(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    books_path = data_dir / "books.csv"
    books_path.write_text(
        "isbn;title;author\n123;Example Book;Author\n",
        encoding="utf-8",
    )
    watchlist_path = data_dir / "watchlists.csv"
    watchlist_path.write_text(
        "user_id;isbn;created_on\nuser1;123;2025-01-01\n",
        encoding="utf-8",
    )
    rated_path = data_dir / "ratedBooks.csv"
    rated_path.write_text("user_id;isbn;score;created_on\n", encoding="utf-8")

    monkeypatch.setattr(watchlist_service, "BOOKS_PATH", str(books_path))
    monkeypatch.setattr(watchlist_service, "WATCHLIST_PATH", str(watchlist_path))
    monkeypatch.setattr(ratedBooks_service, "ratedBooks_repo",
                        __import__("app.repositories.ratedBooks_repo", fromlist=[""]))
    monkeypatch.setattr(ratedBooks_service.ratedBooks_repo, "RATED_PATH", rated_path)

    return rated_path


# Tests for ratedBooks_service
def test_rateBook_success(fake_data):
    ratedBooks_service.rateBook("user1", "123", 8)
    rows = fake_data.read_text(encoding="utf-8").strip().splitlines()
    assert len(rows) == 2
    assert rows[1].startswith("user1;123;8;")

def test_rateBook_requires_watchlist(fake_data):
    with pytest.raises(Exception) as exc:
        ratedBooks_service.rateBook("user1", "999", 5)
    assert "history" in str(exc.value.detail).lower()

def test_rateBook_prevents_duplicates(fake_data):
    ratedBooks_service.rateBook("user1", "123", 7)
    with pytest.raises(Exception) as exc:
        ratedBooks_service.rateBook("user1", "123", 9)
    assert exc.value.status_code == 409

def test_listRatedBooks_matches_watchlist(fake_data):
    ratedBooks_service.rateBook("user1", "123", 6)
    items = ratedBooks_service.listRatedBooks("user1")
    assert len(items) == 1
    assert items[0].isbn == "123"
