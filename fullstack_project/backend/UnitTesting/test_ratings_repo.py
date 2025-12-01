import pytest
from pathlib import Path
from app.repositories import ratings_repo


@pytest.fixture
def fake_ratings_file(tmp_path, monkeypatch):
    """Create isolated temporary ratings.csv and patch DATA_PATH."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    fake_csv = data_dir / "ratings.csv"
    monkeypatch.setattr(ratings_repo, "DATA_PATH", fake_csv)

    return fake_csv


# -------------------------
# load_all()
# -------------------------
def test_load_all_returns_empty_when_missing(fake_ratings_file):
    assert ratings_repo.load_all() == []


def test_load_all_reads_rows_correctly(fake_ratings_file):
    fake_ratings_file.write_text(
        "userid;isbn;score\n"
        "u1;111;5\n"
        "u2;222;3\n",
        encoding="utf-8",
    )

    rows = ratings_repo.load_all()

    assert len(rows) == 2
    assert rows[0]["userid"] == "u1"
    assert rows[0]["isbn"] == "111"
    assert rows[0]["score"] == "5"


# -------------------------
# save_all()
# -------------------------
def test_save_all_writes_valid_csv(fake_ratings_file):
    items = [
        {"userid": "u1", "isbn": "111", "score": "4"},
        {"userid": "u2", "isbn": "222", "score": "5"},
    ]

    ratings_repo.save_all(items)

    # Verify by reading manually
    text = fake_ratings_file.read_text(encoding="utf-8")
    assert "userid;isbn;score" in text
    assert "u1;111;4" in text
    assert "u2;222;5" in text


def test_save_all_deletes_file_if_empty(fake_ratings_file):
    # create file first
    fake_ratings_file.write_text("dummy content", encoding="utf-8")

    ratings_repo.save_all([])

    assert not fake_ratings_file.exists()


def test_save_all_preserves_field_order(fake_ratings_file):
    items = [
        {"userid": "u1", "isbn": "789", "score": "2"}
    ]

    ratings_repo.save_all(items)

    written = fake_ratings_file.read_text(encoding="utf-8").splitlines()[0]
    assert written == "userid;isbn;score"
