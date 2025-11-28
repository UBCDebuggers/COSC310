import pytest
import os
import time
from app.repositories import watchlist_repo


@pytest.fixture
def temp_env(tmp_path, monkeypatch):
    """Patch BOOKS_PATH and WATCHLISTS_PATH to isolated temp directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    fake_books = data_dir / "books.csv"
    fake_watchlist = data_dir / "watchlists.csv"

    monkeypatch.setattr(watchlist_repo, "BOOKS_PATH", str(fake_books))
    monkeypatch.setattr(watchlist_repo, "WATCHLISTS_PATH", str(fake_watchlist))

    return fake_books, fake_watchlist


# -------------------------
# readCsv
# -------------------------
def test_readCsv_returns_empty_if_missing(temp_env):
    books_path, _ = temp_env
    assert watchlist_repo.readCsv(str(books_path)) == []


def test_readCsv_reads_rows_correctly(temp_env):
    books_path, _ = temp_env

    books_path.write_text(
        "isbn;title\n"
        "111;Book A\n"
        "222;Book B\n",
        encoding="utf-8"
    )

    rows = watchlist_repo.readCsv(str(books_path))
    assert len(rows) == 2
    assert rows[0]["isbn"] == "111"
    assert rows[0]["title"] == "Book A"


# -------------------------
# writeCsv
# -------------------------
def test_writeCsv_creates_and_writes_file(temp_env):
    books_path, _ = temp_env

    rows = [
        {"isbn": "111", "title": "Book A"},
        {"isbn": "222", "title": "Book B"},
    ]

    watchlist_repo.writeCsv(str(books_path), ["isbn", "title"], rows)

    text = books_path.read_text(encoding="utf-8")
    assert "isbn;title" in text
    assert "111;Book A" in text
    assert "222;Book B" in text


def test_writeCsv_overwrites_existing_file(temp_env):
    books_path, _ = temp_env
    books_path.write_text("old content", encoding="utf-8")

    rows = [{"isbn": "999", "title": "New"}]
    watchlist_repo.writeCsv(str(books_path), ["isbn", "title"], rows)

    text = books_path.read_text()
    assert "999;New" in text
    assert "old content" not in text


# -------------------------
# getBooksByIsbn
# -------------------------
def test_getBooksByIsbn(temp_env):
    books_path, _ = temp_env

    books_path.write_text(
        "isbn;title;author\n"
        "111;Alpha;A1\n"
        "222;Beta;B1\n",
        encoding="utf-8",
    )

    result = watchlist_repo.getBooksByIsbn()

    assert "111" in result
    assert result["111"]["title"] == "Alpha"
    assert result["222"]["author"] == "B1"


# -------------------------
# getWatchListIsbns
# -------------------------
def test_getWatchListIsbns_filters_and_sorts(temp_env):
    _, watchlist_path = temp_env

    watchlist_path.write_text(
        "user_id;isbn;created_at\n"
        "u1;A;100\n"
        "u1;B;200\n"
        "u2;C;300\n",
        encoding="utf-8"
    )

    result = watchlist_repo.getWatchListIsbns("u1")
    assert result == ["B", "A"]  # sorted DESC by created_at


# -------------------------
# addToWatchlist (ASYNC)
# -------------------------
@pytest.mark.asyncio
async def test_addToWatchlist_adds_item(temp_env, monkeypatch):
    _, watchlist_path = temp_env

    # Freeze time so sorting is deterministic
    monkeypatch.setattr(time, "time", lambda: 1234567890)

    result = await watchlist_repo.addToWatchlist("u1", "XYZ")

    assert result == ["XYZ"]  # only item
    text = watchlist_path.read_text()
    assert "XYZ" in text
    assert "1234567890" in text


@pytest.mark.asyncio
async def test_addToWatchlist_prevents_duplicates(temp_env, monkeypatch):
    _, watchlist_path = temp_env

    watchlist_path.write_text(
        "user_id;isbn;created_at\n"
        "u1;ABC;100\n",
        encoding="utf-8"
    )

    monkeypatch.setattr(time, "time", lambda: 222)

    result = await watchlist_repo.addToWatchlist("u1", "ABC")

    # Should NOT duplicate
    assert result == ["ABC"]

    rows = watchlist_path.read_text()
    assert rows.count("ABC") == 1
