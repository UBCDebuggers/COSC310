import pytest

@pytest.fixture
def temp_env(tmp_path, monkeypatch):
    """
    Creates isolated temp CSV files and patches DATA_PATH in each repo.
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    fake_users = data_dir / "users.csv"
    fake_res = data_dir / "book_reservations.csv"
    fake_books = data_dir / "books.csv"
    fake_waitlist = data_dir / "waitlist.csv"
    fake_analytics = data_dir / "analytics.csv"

    # Import repos AFTER creating fake files
    import app.repositories.users_repo as users_repo
    import app.repositories.reservations_repo as reservation_repo
    import app.repositories.books_repo as books_repo
    import app.repositories.waitlists_repo as waitlists_repo
    import app.repositories.analytics_repo as analytics_repo

    monkeypatch.setattr(users_repo, "DATA_PATH", fake_users)
    monkeypatch.setattr(reservation_repo, "DATA_PATH", fake_res)
    monkeypatch.setattr(books_repo, "DATA_PATH", fake_books)
    monkeypatch.setattr(waitlists_repo, "DATA_PATH", fake_waitlist)
    monkeypatch.setattr(analytics_repo, "DATA_PATH", fake_analytics)

    return {
        "users": fake_users,
        "reservations": fake_res,
        "books": fake_books,
        "waitlist": fake_waitlist,     
        "analytics": fake_analytics,
    }
