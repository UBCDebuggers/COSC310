import csv
from pathlib import Path
from app.services import analytics_service
from app.repositories import analytics_repo
import pytest

@pytest.fixture
def analytics_csv(tmp_path, monkeypatch):
    temp = tmp_path / "analytics.csv"
    monkeypatch.setattr(analytics_repo, "DATA_PATH", temp)
    return temp

def test_top_rated_basic(analytics_csv):
    rows = [
        {"date":"2025-01-01","book_id":"A","title":"Alpha","rating_count":"10","avg_rating":"9.5","unique_users":"4"},
        {"date":"2025-01-01","book_id":"B","title":"Beta","rating_count":"3","avg_rating":"7.1","unique_users":"2"},
    ]

    with analytics_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    result = analytics_service.get_top_rated_books()
    assert result[0]["isbn"] == "A"
    assert result[0]["avg_rating"] == 9.5

def test_trending_basic(analytics_csv):
    rows = [
        {"date":"2025-01-01","book_id":"A","title":"Alpha","rating_count":"5","avg_rating":"8.0","unique_users":"10"},
        {"date":"2025-01-01","book_id":"B","title":"Beta","rating_count":"9","avg_rating":"8.1","unique_users":"1"},
    ]

    with analytics_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    result = analytics_service.get_trending_books()
    assert result[0]["isbn"] == "A"   # 5+10 = 15 (higher trend score)
