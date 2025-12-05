import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.main import app
from app.routers import auth as auth_router
from app.schemas.user import User


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_auth(monkeypatch):
    fake_user = User(
        userid="user-1",
        email="user@example.com",
        hash_password="hashed",
        is_admin=False,
        department="dept",
        age=30,
        username="tester",
        firstname="Test",
        lastname="User",
    )

    mocks = {
        "authenticate_user": MagicMock(return_value=fake_user),
        "create_user": MagicMock(return_value=fake_user),
        "create_access_token": MagicMock(return_value="fake-token"),
    }

    for name, mock in mocks.items():
        monkeypatch.setattr(auth_router, name, mock)

    return mocks


def test_login_success_returns_token(client, mock_auth):
    resp = client.post("/auth/login", data={"username": "tester", "password": "secret"})

    assert resp.status_code == status.HTTP_202_ACCEPTED
    body = resp.json()
    assert body["access_token"] == "fake-token"
    assert body["token_type"] == "bearer"
    mock_auth["authenticate_user"].assert_called_once()
    args, _ = mock_auth["authenticate_user"].call_args
    assert args[0].email == "tester"
    assert args[0].password == "secret"
    mock_auth["create_access_token"].assert_called_once()
    _, kwargs = mock_auth["create_access_token"].call_args
    assert kwargs["data"] == {"sub": "user-1", "admin": False, 'email': 'user@example.com', 'username': 'tester'}


def test_login_invalid_credentials_returns_unauthorized(client, mock_auth):
    mock_auth["authenticate_user"].return_value = None

    resp = client.post("/auth/login", data={"username": "tester", "password": "wrong"})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json()["detail"] == "Invalid credentials"
    mock_auth["create_access_token"].assert_not_called()

def test_signup_success_returns_token(client, mock_auth):
    payload = {
        "email": "user@example.com",
        "password": "secret",
        "is_admin": False,
        "department": "dept",
        "age": 30,
        "username": "tester",
        "firstname": "Test",
        "lastname": "User",
    }

    resp = client.post("/auth/signup", json=payload)

    assert resp.status_code == status.HTTP_201_CREATED
    body = resp.json()
    assert body["access_token"] == "fake-token"
    mock_auth["create_user"].assert_called_once()
    mock_auth["create_access_token"].assert_called_once_with(data={"sub": "user-1", "admin" : False, "username" : "tester", "email" : "user@example.com"})
