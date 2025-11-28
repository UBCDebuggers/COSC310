from pathlib import Path
import pytest
from app.services import watchlist_service

@pytest.fixture
def fake_data_dir(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    books_path = data_dir / "books.csv"
    watchlists_path = data_dir / "watchlists.csv"

    books_path.write_text("isbn;title;author\n123;Example Book;Author\n", encoding="utf-8")
    watchlists_path.write_text("user_id;isbn;created_on\n", encoding="utf-8")

    monkeypatch.setattr(watchlist_service, "DATA_DIR", str(data_dir))
    monkeypatch.setattr(watchlist_service, "BOOKS_PATH", str(books_path))
    monkeypatch.setattr(watchlist_service, "WATCHLIST_PATH", str(watchlists_path))
    return watchlists_path

def test_list_watchlist_orders_newest_first(fake_data_dir):
    books_path = Path(watchlist_service.BOOKS_PATH)
    books_path.write_text(
        "isbn;title;author\n123;Old Book;A\n456;New Book;B\n",
        encoding="utf-8"
    )
    fake_data_dir.write_text(
        "user_id;isbn;created_on\n"
        "u1;123;2025-11-12\n"
        "u1;456;2025-11-14\n",
        encoding="utf-8"
    )

    items = watchlist_service.listWatchlist("u1")
    assert [i.isbn for i in items] == ["123", "456"]

def test_add_book_to_watchlist(fake_data_dir):
    watchlist_service.addBookToWatchlist("u1", "123")
    watchlist_service.addBookToWatchlist("u1", "123")

    rows = fake_data_dir.read_text(encoding="utf-8").strip().splitlines()[1:]
    assert len(rows) == 1

def test_removeBookFromWatchlist_filters_only_target_user(fake_data_dir):
    watchlist_service.addBookToWatchlist("u1", "123")
    watchlist_service.addBookToWatchlist("u2", "123")

    watchlist_service.removeBookFromWatchlist("u1", "123")

    rows = fake_data_dir.read_text(encoding="utf-8").strip().splitlines()[1:]
    assert len(rows) == 1
    assert rows[0].startswith("u2;123;")
