import pytest
from app.services import ratedBooks_service, watchlist_service


@pytest.fixture
def fake_data(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    books_path = data_dir / "books.csv"
    books_path.write_text(
        "isbn;title;author;year_of_publication;publisher;img_url_s;img_url_m;img_url_l\n"
        "123;Example Book;Author;2000;Pub;img;img;img\n",
        encoding="utf-8",
    )
    watchlist_path = data_dir / "watchlists.csv"
    watchlist_path.write_text(
        "user_id;isbn;created_on\nuser1;123;2025-01-01\nuser2;123;2025-01-02\n",
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


def _user(user_id="user1", admin=False):
    return {"userid": user_id, "is_admin": admin}


def test_rate_book_success(fake_data):
    rated = ratedBooks_service.rateBook("user1", "123", 8)
    assert rated.isbn == "123"
    assert rated.score == 8


def test_rate_book_requires_watchlist(fake_data):
    with pytest.raises(Exception):
        ratedBooks_service.rateBook("user1", "999", 5)


def test_list_rated_books(fake_data):
    ratedBooks_service.rateBook("user1", "123", 6)
    results = ratedBooks_service.listRatedBooks("user1")
    assert len(results) == 1


def test_list_by_isbn(fake_data):
    ratedBooks_service.rateBook("user1", "123", 7)
    ratedBooks_service.rateBook("user2", "123", 5)
    assert len(ratedBooks_service.listRatingsByIsbn("123")) == 2


def test_update_rating_permissions(fake_data):
    ratedBooks_service.rateBook("user1", "123", 7)
    updated = ratedBooks_service.updateRating("user1", "123", 9, requester=_user())
    assert updated.score == 9
    with pytest.raises(Exception):
        ratedBooks_service.updateRating("user1", "123", 6, requester=_user("user2"))
    admin_updated = ratedBooks_service.updateRating("user1", "123", 4, requester=_user("admin", admin=True))
    assert admin_updated.score == 4


def test_remove_rating_permissions(fake_data):
    ratedBooks_service.rateBook("user1", "123", 6)
    ratedBooks_service.removeRating("user1", "123", requester=_user())
    assert ratedBooks_service.listRatedBooks("user1") == []
    ratedBooks_service.rateBook("user1", "123", 6)
    with pytest.raises(Exception):
        ratedBooks_service.removeRating("user1", "123", requester=_user("user2"))
    ratedBooks_service.removeRatingAsAdmin("user1", "123", requester=_user("admin", admin=True))
    assert ratedBooks_service.listRatedBooks("user1") == []
