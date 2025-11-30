import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

def make_client():
    from app.main import app
    return TestClient(app)

@patch("app.routers.recommend.get_best_rated_books")
def test_get_top_rated_endpoint(mock_best):
    mock_best.return_value = [
        {"book_id": "B001", "score": 4.8},
        {"book_id": "B002", "score": 4.5},
    ]

    client = make_client()
    resp = client.get("/recommend/toprated/2")

    assert resp.status_code == 200
    assert resp.json() == mock_best.return_value
    mock_best.assert_called_once_with(2)

@patch("app.routers.recommend.get_books_by_engagement")
def test_top_engagement_endpoint(mock_eng):
    mock_eng.return_value = [
        {"book_id": "B010", "engagement": 300},
        {"book_id": "B003", "engagement": 250},
    ]

    client = make_client()
    resp = client.get("/recommend/topengagement/2")

    assert resp.status_code == 200
    assert resp.json() == mock_eng.return_value
    mock_eng.assert_called_once_with(2)

@patch("app.routers.recommend.get_popular_books")
def test_top_popular_books_endpoint(mock_pop):
    mock_pop.return_value = [
        {"book_id": "B001", "pop": 99},
        {"book_id": "B007", "pop": 70},
    ]

    client = make_client()
    resp = client.get("/recommend/popular/2")

    assert resp.status_code == 200
    assert resp.json() == mock_pop.return_value
    mock_pop.assert_called_once_with(2)
    

def make_client(override=None):
    from app.main import app

    if override:
        app.dependency_overrides.update(override)

    return TestClient(app)


@pytest.fixture
def mock_verify():
    def fake_user():
        return {"userid": "U01"}
    return fake_user

@patch("app.routers.recommend.recommend_for_user")
def test_recommend_for_user_endpoint(mock_rec, mock_verify):
    mock_rec.return_value = [1, 2, 3]

    client = make_client({
        __import__("app.routers.recommend").routers.recommend.verify_access_token: 
            lambda: mock_verify()
    })
    resp = client.get("/recommend")

    assert resp.status_code == 200
    assert resp.json() == [1, 2, 3]

    mock_rec.assert_called_once_with("U01")

