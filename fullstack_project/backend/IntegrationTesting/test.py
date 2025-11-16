import csv
import io
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.services.books_service import search_books
from app.routers.books import router, verify_access_token
from app.schemas.filter import Filter
from fastapi import status
from app.schemas.book import BookCreate, BookUpdate

@pytest.fixture
def client():
    """Fixture to provide a reusable TestClient for FastAPI app."""
    with TestClient(app) as c:
        yield c

def test_home(client):
    r = client.get("/")
    assert r.status_code == 404
    assert r.json() ==  {"detail":"Not Found"}
    
def test_search_books():
    test = "Classical Mythology"
    book = search_books(test, None)
    
    assert test.lower() in book[9].title.lower()
    
def test_search_books_filter_date():
    test = "Classical Mythology"
    query = Filter(author=None,
                    publisher=None,
                    publish_date_min= 2019,
                    publish_date_max= 2022)
    books = search_books(test, query)
    
    assert all(int(book.year_of_publication) <= 2022 for book in books)
    assert all(int(book.year_of_publication) >= 2019 for book in books)
    
def test_search_books_filter_author():
    test = "Classical Mythology"
    query = Filter(author="Jayne Ann Krentz",
                    publisher=None,
                    publish_date_range= None)
    books = search_books(test, query)
    
    assert all(book.author == "Jayne Ann Krentz" for book in books)
    
def test_search_books_filter_publisher():
    test = "Classical Mythology"
    query = Filter(author=None,
                    publisher="Pocket",
                    publish_date_range= None)
    books = search_books(test, query)
    
    assert all(book.publisher == "Pocket" for book in books)
    

# MOCK DATA
MOCK_ISBN = "978-0321765723"
MOCK_BOOK = {
    "isbn": "978-0321765723",
    "title": "Mock Book Title",
    "author": "Mock Author",
    "year_of_publication": 2023,
    "publisher": "Mock Publisher",
    "img_url_s": "s.jpg",
    "img_url_m": "m.jpg",
    "img_url_l": "l.jpg"
}
MOCK_UPDATE_PAYLOAD = {"isbn": "978-0321765723",
    "title": "Updated Title",
    "author": "Mock Author",
    "year_of_publication": 2023,
    "publisher": "Mock Publisher", 
    "img_url_s": "s.jpg", 
    "img_url_m": "m.jpg", 
    "img_url_l": "l.jpg"}
MOCK_FILTER = {"publish_date_min": 2000,
               "publish_date_max": 2024}

EXPECTED_FILTER_OBJ = Filter(
    publish_date_min= 2000,
    publish_date_max= 2024
)

# DEPENDENCY OVERRIDES (Authentication Mocks) 

def override_verify_access_token_admin():
    """Mock dependency returning an admin user payload."""
    return {"user_id": 1, "is_admin": True}

def override_verify_access_token_non_admin():
    """Mock dependency returning a non-admin user payload."""
    return {"user_id": 2, "is_admin": False}

def setup_auth(is_admin: bool):
    """Sets the dependency override based on the admin flag."""
    if is_admin:
        app.dependency_overrides[verify_access_token] = override_verify_access_token_admin
    else:
        app.dependency_overrides[verify_access_token] = override_verify_access_token_non_admin

def cleanup_auth():
    """Clears all dependency overrides."""
    app.dependency_overrides.clear()

# SERVICE MOCKS FIXTURE

@pytest.fixture
def mock_services(monkeypatch):
    """Mocks all service functions used by the books router."""
    mocks = {
        "search_books": MagicMock(return_value=[MOCK_BOOK]),
        "get_book_by_isbn": MagicMock(return_value=MOCK_BOOK),
        "create_book": MagicMock(side_effect=lambda payload: {**MOCK_BOOK, **payload.model_dump()}),
        "delete_book": MagicMock(return_value=None),
        "update_book": MagicMock(return_value={**MOCK_BOOK, **MOCK_UPDATE_PAYLOAD}),
    }
    
    # Patch the functions in the router's scope
    monkeypatch.setattr("app.routers.books.search_books", mocks["search_books"])
    monkeypatch.setattr("app.routers.books.get_book_by_isbn", mocks["get_book_by_isbn"])
    monkeypatch.setattr("app.routers.books.create_book", mocks["create_book"])
    monkeypatch.setattr("app.routers.books.delete_book", mocks["delete_book"])
    monkeypatch.setattr("app.routers.books.update_book", mocks["update_book"])
    
    return mocks

## 1. Search Endpoint Test: GET /books/search/{title}
def test_search_book_success(client: TestClient, mock_services):
    """Test searching for books by title, including the Filter query parameter."""
    response = client.get("/books/search/mock_title", params=MOCK_FILTER)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [MOCK_BOOK]
    
    mock_services["search_books"].return_value = [MOCK_BOOK]

    mock_services["search_books"].assert_called_once()
    called_args, called_kwargs = mock_services["search_books"].call_args
    assert called_kwargs["filter_data"].model_dump() == EXPECTED_FILTER_OBJ.model_dump()
    assert called_args[0] == "mock_title"
    
## 2. Get Book Endpoint Test: GET /books/{isbn}
def test_get_book_success(client: TestClient, mock_services):
    """Test getting a single book by ISBN."""
    response = client.get(f"/books/{MOCK_ISBN}")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == MOCK_BOOK
    mock_services["get_book_by_isbn"].assert_called_once_with(MOCK_ISBN)

## 3. Create Endpoint Test: POST /books/create
@pytest.mark.parametrize("is_admin, expected_status", [
    (True, status.HTTP_201_CREATED),
    (False, status.HTTP_403_FORBIDDEN),
])
def test_post_book_permissions(client: TestClient, mock_services, is_admin, expected_status):
    """Test book creation permissions."""
    setup_auth(is_admin)
    
    response = client.post("/books/create", json=MOCK_BOOK)
    
    assert response.status_code == expected_status
    if is_admin:
        assert response.json()["isbn"] == MOCK_ISBN
        mock_services["create_book"].assert_called_once()
    else:
        mock_services["create_book"].assert_not_called()
    
    cleanup_auth()

## 4. Update Endpoint Test: PUT /books/update/{isbn}
@pytest.mark.parametrize("is_admin, expected_status", [
    (True, status.HTTP_200_OK),
    (False, status.HTTP_403_FORBIDDEN),
])
def test_put_book_permissions(client: TestClient, mock_services, is_admin, expected_status):
    """Test book update permissions."""
    setup_auth(is_admin)
    
    response = client.put(f"/books/update/{MOCK_ISBN}", json=MOCK_UPDATE_PAYLOAD)
    
    assert response.status_code == expected_status
    if is_admin:
        assert response.json()["title"] == MOCK_UPDATE_PAYLOAD["title"]
        mock_services["update_book"].assert_called_once()
    else:
        mock_services["update_book"].assert_not_called()
    
    cleanup_auth()

## 5. Delete Endpoint Test: DELETE /books/delete/{isbn}
@pytest.mark.parametrize("is_admin, expected_status", [
    (True, status.HTTP_204_NO_CONTENT),
    (False, status.HTTP_403_FORBIDDEN),
])
def test_remove_book_permissions(client: TestClient, mock_services, is_admin, expected_status):
    """Test book deletion permissions."""
    setup_auth(is_admin)
    
    response = client.delete(f"/books/delete/{MOCK_ISBN}")
    
    assert response.status_code == expected_status
    if is_admin:
        assert response.content == b'' 
        mock_services["delete_book"].assert_called_once_with(MOCK_ISBN)
    else:
        mock_services["delete_book"].assert_not_called()
    
    cleanup_auth()

# CSV Helper
def get_mock_csv(data: list[dict]):
    """Create in-memory CSV data."""
    csv_file = io.StringIO()
    fieldnames = list(data[0].keys()) if data else []
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return csv_file.getvalue().encode('latin-1')

# 6. CSV Upload Tests
def test_upload_csv_success(client: TestClient, mock_services):
    """Test successful CSV upload of multiple books by an admin."""
    setup_auth(True)
    
    mock_books = [{"isbn": "9780000000111", "title": "T1", "author": "A1", "year_of_publication": 2023,
     "publisher": "Mock Publisher", "img_url_s": "s.jpg", "img_url_m": "m.jpg", "img_url_l": "l.jpg"},
    {"isbn": "9780000000222", "title": "T2", "author": "A2", "year_of_publication": 2002,
     "publisher": "Mock Publisher", "img_url_s": "m.jpg", "img_url_m": "m.jpg", "img_url_l": "l.jpg"},
]
    csv_content = get_mock_csv(mock_books)
    files = {'file': ('books.csv', csv_content, 'text/csv')}
    
    response = client.post("/books/upload", files=files)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert "Successfully created 2 books" in response.json()["message"]
    assert mock_services["create_book"].call_count == 2
    cleanup_auth()

# 7. Test uploading a CSV with an invalid entry
def test_upload_csv_invalid_data_skip(client: TestClient, mock_services):
    """Test that invalid rows are skipped and valid ones processed."""
    setup_auth(True)
    
    mock_books = [
    {"isbn": "9780000003333", "title": "Valid Book", "author": "V1", "year_of_publication": 2003,
     "publisher": "V_Pub", "img_url_s": "v_s.jpg", "img_url_m": "v_m.jpg", "img_url_l": "v_l.jpg"}, 
    {"isbn": "", "title": "Invalid Book", "author": "I1", "year_of_publication": 2004,
     "publisher": "I_Pub", "img_url_s": "i_s.jpg", "img_url_m": "i_m.jpg", "img_url_l": "i_l.jpg"},
]
    csv_content = get_mock_csv(mock_books)
    files = {'file': ('books.csv', csv_content, 'text/csv')}
    
    response = client.post("/books/upload", files=files)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert "Successfully created 1 books" in response.json()["message"]
    assert mock_services["create_book"].call_count == 1
    cleanup_auth()

# Test uploading a CSV with all entries invalid 
def test_upload_csv_all_invalid_data(client: TestClient, mock_services):
    """Test that if all rows are invalid, an error is returned."""
    setup_auth(True)
    
    mock_books = [
        {"title": "No ISBN 1", "author": "A1"},
        {"title": "No ISBN 2", "author": "A2"},
    ]
    csv_content = get_mock_csv(mock_books)
    files = {'file': ('books.csv', csv_content, 'text/csv')}
    
    response = client.post("/books/upload", files=files)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "No valid books could be created" in response.json()["detail"]
    assert mock_services["create_book"].call_count == 0
    cleanup_auth()

# Test uploading an empty CSV 
def test_upload_csv_empty_file(client: TestClient, mock_services):
    """Test uploading an empty CSV file."""
    setup_auth(True)
    
    csv_content = b'' 
    files = {'file': ('empty.csv', csv_content, 'text/csv')}
    
    response = client.post("/books/upload", files=files)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "No valid books could be created" in response.json()["detail"]
    assert mock_services["create_book"].call_count == 0
    cleanup_auth()
    
# Test for error messages
def test_upload_books_csv_partial_errors(client : TestClient, mock_services):
    setup_auth(True)
    
    mock_books = [
    {"isbn": "9780000003333", "title": "Valid Book", "author": "V1", "year_of_publication": 2003,
     "publisher": "V_Pub", "img_url_s": "v_s.jpg", "img_url_m": "v_m.jpg", "img_url_l": "v_l.jpg"}, 
    {"isbn": "", "title": "Invalid Book", "author": "I1", "year_of_publication": 2004,
     "publisher": "I_Pub", "img_url_s": "i_s.jpg", "img_url_m": "i_m.jpg", "img_url_l": "i_l.jpg"},
]
    csv_file = get_mock_csv(mock_books)

    response = client.post("/books/upload", files={"file": ("books.csv", csv_file, "text/csv")})
       
    assert response.status_code == 201 
    
    data = response.json()
    
    assert mock_services["create_book"].call_count == 1
    assert "Successfully created 1 books." in data["message"]
    assert "Error processing row" in data["errors"]
    assert "Error processing row {'isbn': '', 'title': 'Invalid Book', 'author': 'I1', 'year_of_publication': '2004', 'publisher': 'I_Pub', 'img_url_s': 'i_s.jpg', 'img_url_m': 'i_m.jpg', 'img_url_l': 'i_l.jpg'}: 1 validation error for BookCreate\nisbn\n  String should have at least 10 characters [type=string_too_short, input_value='', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.12/v/string_too_short\n" in data["errors"]