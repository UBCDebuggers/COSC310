from app.repositories import reservations_repo

def test_reservations_empty(temp_env):
    assert reservations_repo.load_all() == []

def test_reservation_write_and_load(temp_env):
    rows = [
        {"res_id": "1", "user": "u1", "isbn": "111"},
        {"res_id": "2", "user": "u2", "isbn": "222"},
    ]

    reservations_repo.save_all(rows)
    loaded = reservations_repo.load_all()

    assert loaded == rows

def test_reservations_delete_on_empty(temp_env):
    reservations_repo.save_all([])
    assert not temp_env["reservations"].exists()
