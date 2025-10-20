import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from schemas.book import Book, BookCreate, BookUpdate
from repositories.books_repo import load_all, save_all

def list_books() -> List[Book]:
    return [Book(**attributes) for attributes in load_all()]

def create_book(newBook: BookCreate) -> Book:
    books = load_all()
    if any(book.get("ISBN") == newBook.isbn for book in books):
        raise HTTPException(status_code=409, detail="ISBN collision; retry.")
    
    new_record = Book(isbn = newBook.isbn.strip(),
                      title = newBook.title.strip(),
                      author = newBook.author.strip(),
                      year_of_publication = newBook.year_of_publication.strip(),
                      publisher = newBook.publisher.strip(),
                      img_url_s = newBook.img_url_s.strip(),
                      img_url_m = newBook.img_url_m.strip(),
                      img_url_l = newBook.img_url_l.strip()
                      )
    books.append(new_record.model_dump())
    save_all(books)
    return new_record

def get_book_by_isbn(book_isbn: str) -> Book:
    books = load_all()
    for book in books:
        if book.get("ISBN") == book_isbn:
            return Book(**book)
    raise HTTPException(status_code=404, detail=f"Book '{book_isbn}' not found")

def update_book(book_isbn: str, bookUpdate : BookUpdate) -> Book:
    books = load_all()
    for id, book in enumerate(books):
        if book.get("ISBN") == book_isbn:
            updated = Book(isbn = bookUpdate.isbn.strip(),
                      title = bookUpdate.title.strip(),
                      author = bookUpdate.author.strip(),
                      year_of_publication = bookUpdate.year_of_publication.strip(),
                      publisher = bookUpdate.publisher.strip(),
                      img_url_s = bookUpdate.img_url_s.strip(),
                      img_url_m = bookUpdate.img_url_m.strip(),
                      img_url_l = bookUpdate.img_url_l.strip()
                      )
            books[id] = updated.model_dump()
            save_all(books)
            return updated
    raise HTTPException(status_code=404, detail=f"Book '{book_isbn}' not found")

def delete_book(book_isbn: str) -> None:
    books = load_all()
    new_books = [book for book in books if book.get("ISBN") != book_isbn]
    if len(new_books) == len(books):
        HTTPException(status_code=404, detail=f"Book '{book_isbn}' not found")
    save_all(new_books)
        
            
    