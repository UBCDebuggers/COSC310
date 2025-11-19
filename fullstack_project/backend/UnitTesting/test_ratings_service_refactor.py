from app.services import ratings_service
from app.repositories import ratings_repo
from pathlib import Path


def test_list_ratings_returns_objects(monkeypatch, tmp_path):
    temp_file = tmp_path / "ratings.csv"
    monkeypatch.setattr(ratings_repo, "DATA_PATH", temp_file)

    temp_file.write_text(
        "id,isbn,rating\n1,ABC,5\n2,XYZ,4\n",
        encoding="utf-8"
    )

    ratings = ratings_service.list_ratings()
    assert len(ratings) == 2
    assert ratings[0].isbn == "ABC"
