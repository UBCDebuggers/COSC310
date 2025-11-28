from app.repositories import waitlists_repo

def test_waitlist_load_empty(temp_env):
    """
    load_all() should return an empty list if the waitlist.csv file does not exist.
    """
    assert waitlists_repo.load_all() == []


def test_waitlist_save_and_reload(temp_env):
    """
    save_all() should correctly write rows to the CSV file,
    and load_all() should return the same data.
    """
    rows = [
        {"user_id": "u1", "isbn": "123"},
        {"user_id": "u2", "isbn": "456"}
    ]

    waitlists_repo.save_all(rows)
    loaded = waitlists_repo.load_all()

    assert loaded == rows


def test_waitlist_delete_on_empty(temp_env):
    """
    Passing an empty list to save_all() should delete the file.
    """
    waitlists_repo.save_all([])

    # The file should be removed
    assert not temp_env["waitlist"].exists()
