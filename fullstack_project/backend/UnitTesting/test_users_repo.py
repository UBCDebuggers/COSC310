from app.repositories import users_repo

def test_users_load_empty(temp_env):
    assert users_repo.load_all() == []

def test_users_save_and_reload(temp_env):
    users = [
        {"id": "u1", "name": "Ahab"},
        {"id": "u2", "name": "Qamar"}
    ]

    users_repo.save_all(users)

    loaded = users_repo.load_all()
    assert loaded == users

def test_users_save_empty_deletes_file(temp_env):
    users_repo.save_all([])

    # File should not exist
    assert not temp_env["users"].exists()
