import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.main import app
from app.routers import ratings as ratings_router


# Dependency override helpers
def override_token(user_id="user-1", is_admin=False):
    return lambda: {"userid": user_id, "is_admin": is_admin}


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_services(monkeypatch):
    mocks = {
        "create_rating": MagicMock(return_value={"isbn": "ABC", "userid": "user-1", "rating": "5"}),
        "get_ratings_by_isbn": MagicMock(return_value=[{"isbn": "ABC", "userid": "user-1", "rating": "4"}]),
        "get_ratings_by_userid": MagicMock(return_value=[{"userid": "user-1", "isbn": "ABC", "rating": "3"}]),
        "update_rating": MagicMock(return_value={"isbn": "ABC", "userid": "user-1", "rating": "2"}),
        "delete_rating": MagicMock(return_value=None),
    }

    for name, mock in mocks.items():
        monkeypatch.setattr(ratings_router, name, mock)

    return mocks


def test_post_rating_uses_userid_from_token(client, mock_services):
    app.dependency_overrides[ratings_router.verify_access_token] = override_token(user_id="u123")
    payload = {"isbn": "ABC", "rating": "5", "description": "Nice"}

    resp = client.post("/ratings", json=payload)

    assert resp.status_code == status.HTTP_201_CREATED
    body = resp.json()
    assert body["isbn"] == "ABC"
    assert body["userid"] == "user-1"
    assert str(body["rating"]) == "5"
    assert "timestamp" in body
    mock_services["create_rating"].assert_called_once()
    args, kwargs = mock_services["create_rating"].call_args
    assert args[0].isbn == "ABC"
    assert args[1] == "u123"


def test_get_ratings_by_isbn_route(client, mock_services):
    resp = client.get("/ratings/isbn/XYZ")

    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body[0]["isbn"] == "ABC"
    assert str(body[0]["rating"]) == "4"
    mock_services["get_ratings_by_isbn"].assert_called_once_with("XYZ")


def test_get_ratings_by_userid_route(client, mock_services):
    resp = client.get("/ratings/userid/u999")

    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body[0]["userid"] == "user-1"
    assert str(body[0]["rating"]) == "3"
    mock_services["get_ratings_by_userid"].assert_called_once_with("u999")


def test_put_rating_uses_token_userid(client, mock_services):
    app.dependency_overrides[ratings_router.verify_access_token] = override_token(user_id="u42")
    payload = {"rating": "3", "description": "edit"}

    resp = client.put("/ratings/ABC", json=payload)

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["rating"] == 2
    mock_services["update_rating"].assert_called_once()
    args, _ = mock_services["update_rating"].call_args
    assert args[0] == "ABC"
    assert args[1] == "u42"


def test_remove_rating_admin_allows_delete_any_user(client, mock_services):
    app.dependency_overrides[ratings_router.verify_access_token] = override_token(user_id="admin", is_admin=True)

    resp = client.delete("/ratings/ABC/someuser")

    assert resp.status_code == status.HTTP_204_NO_CONTENT
    mock_services["delete_rating"].assert_called_once_with("ABC", "someuser")


def test_remove_rating_admin_forbidden_for_non_admin(client, mock_services):
    app.dependency_overrides[ratings_router.verify_access_token] = override_token(user_id="regular", is_admin=False)

    resp = client.delete("/ratings/ABC/someuser")

    assert resp.status_code == status.HTTP_403_FORBIDDEN
    mock_services["delete_rating"].assert_not_called()


def test_remove_rating_uses_token_userid_success(client, mock_services):
    app.dependency_overrides[ratings_router.verify_access_token] = override_token(user_id="u777")

    resp = client.delete("/ratings/ABC")

    assert resp.status_code == status.HTTP_204_NO_CONTENT
    mock_services["delete_rating"].assert_called_once_with("ABC", "u777")
