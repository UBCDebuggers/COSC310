from fastapi import FastAPI, status, HTTPException
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.services import watchlist_service, ratedBooks_service
from app.core.security import verify_access_token
from app.routers.ratedBooks import router

@pytest.fixture
def mock_rated_books_service(mocker):
    """Mocks the service used in the ratedBooks router."""
    return mocker.patch("app.routers.ratedBooks.ratedBooks_service")

@pytest.fixture
def client():
    """
    Creates a client specifically for this file with auth overridden.
    """
    def mock_verify_token():
        return {"userid": "test_user_123", "is_admin": False}

    app.dependency_overrides[verify_access_token] = mock_verify_token

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

def test_rate_book_success(client, mock_rated_books_service):
    """Test successfully rating a book (201 Created)."""
    payload = {"isbn": "123", "score": 8}
    
    response = client.post("/rated-books", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "Rating saved"}
    
    mock_rated_books_service.rateBook.assert_called_once_with("test_user_123", "123", 8)

def test_rate_book_duplicate(client, mock_rated_books_service):
    """Test handling of a duplicate rating (409 Conflict)."""
    mock_rated_books_service.rateBook.side_effect = HTTPException(
        status_code=status.HTTP_409_CONFLICT, 
        detail="Book already rated"
    )

    response = client.post("/rated-books", json={"isbn": "123", "score": 9})

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Book already rated"

def test_rate_book_score_out_of_range(client, mock_rated_books_service):
    """Test Pydantic validation (Score > 10)."""
    payload = {"isbn": "123", "score": 11}

    response = client.post("/rated-books", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    mock_rated_books_service.rateBook.assert_not_called()