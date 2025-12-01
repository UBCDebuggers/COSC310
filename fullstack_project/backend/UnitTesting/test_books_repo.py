from app.repositories import books_repo

def test_books_empty(temp_env):
    books_repo.load_all.cache_clear()
    assert books_repo.load_all() == []

def test_books_write_and_load(temp_env):
    rows = [
        {"isbn": "123", "title": "Dune"},
        {"isbn": "456", "title": "1984"},
    ]

    books_repo.save_all(rows)
    loaded = books_repo.load_all()

    assert loaded == rows

def test_books_delete_file_on_empty(temp_env):
    books_repo.save_all([])

    assert not temp_env["books"].exists()
