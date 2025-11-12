from fastapi.testclient import TestClient
from app.main import app
from app.services.books_service import search_books
from app.schemas.filter import Filter, DateRange

client = TestClient(app)

def test_home():
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
                    publish_date_range= DateRange(min=2019, max=2022))
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