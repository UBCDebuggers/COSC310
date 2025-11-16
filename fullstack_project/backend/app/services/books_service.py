import re
from collections import Counter
from typing import List
from fastapi import HTTPException
from app.schemas.book import Book, BookCreate, BookUpdate
from app.schemas.filter import Filter
from app.repositories.books_repo import load_all, save_all
    
#Searches for a book by its title given a string. Returns the top 10 books that have the most matches by characters and words
def search_books(tokens : str, filter_data : Filter) -> List[Book]:
    books = load_all()
    results_list = []
    filtered_books = filter(filter_data, books)
    
    tokens = tokens.lower()
    token_words = [w for w in re.split(r"[ .,/?;()]", tokens) if w]
    token_word_set = set(token_words)
    
    for book in filtered_books:
        title = book.get('title')
        title = title.lower()
        title_word_set = set(title.split())
        
        char_hits = sum(Counter(title)[ch] for ch in set(tokens) if ch in title)
        word_hits = len(token_word_set & title_word_set)
        
        results_list.append({"char_hits" : char_hits, 
                             "word_hits": word_hits, 
                             **book})
    
    results_list = sorted( results_list, key=lambda item: (
        -item["word_hits"],  
        -item["char_hits"],  
        item["title"]        
        ))
    results_list = results_list[:10]
    results_list = [Book(**{k: v for k, v in book.items() if k not in ("word_hits", "char_hits")}) for book in results_list]
    
    return results_list

# Filters the book based on author, year of publication, publisher
def filter(filter_data : Filter, books : List) -> List[Book]:
    if filter_data is None:
        return books
    filter_author = filter_data.author.lower() if filter_data.author else None
    filter_publisher = filter_data.publisher.lower() if filter_data.publisher else None
    date_range = filter_data.publish_date_range

    results = [
        book for book in books
        if ((filter_author is None or book.get("author").lower() == filter_author) 
            and (filter_publisher is None or book.get('publisher').lower() == filter_publisher) 
            and (date_range is None or (
                (date_range.min is None or int(book["year_of_publication"]) >= date_range.min)
                and (date_range.max is None or int(book["year_of_publication"]) <= date_range.max)
            )
            )
        )
    ]

    return results

#Creates a book
def create_book(newBook: BookCreate) -> Book:
    books = load_all()
    if any(book.get("isbn") == newBook.isbn for book in books):
        raise HTTPException(status_code=409, detail="ISBN collision; retry.")
    
    new_record = Book(isbn = newBook.isbn.strip(),
                      title = newBook.title.strip(),
                      author = newBook.author.strip(),
                      year_of_publication = newBook.year_of_publication,
                      publisher = newBook.publisher.strip(),
                      img_url_s = newBook.img_url_s.strip(),
                      img_url_m = newBook.img_url_m.strip(),
                      img_url_l = newBook.img_url_l.strip()
                      )
    books.append(new_record.model_dump())
    save_all(books)
    return new_record

#Returns a book using ISBN
def get_book_by_isbn(book_isbn: str) -> Book:
    books = load_all()
    for book in books:
        if book.get('isbn') == book_isbn:
            return Book(**book)
    raise HTTPException(status_code=404, detail=f"Book '{book_isbn}' not found")

#Updates a book
def update_book(book_isbn: str, bookUpdate : BookUpdate) -> Book:
    books = load_all()
    for id, book in enumerate(books):
        if book.get("isbn") == book_isbn:
            updated = Book(isbn = bookUpdate.isbn.strip(),
                      title = bookUpdate.title.strip(),
                      author = bookUpdate.author.strip(),
                      year_of_publication = bookUpdate.year_of_publication,
                      publisher = bookUpdate.publisher.strip(),
                      img_url_s = bookUpdate.img_url_s.strip(),
                      img_url_m = bookUpdate.img_url_m.strip(),
                      img_url_l = bookUpdate.img_url_l.strip()
                      )
            books[id] = updated.model_dump()
            save_all(books)
            return updated
    raise HTTPException(status_code=404, detail=f"Book '{book_isbn}' not found")

#Deletes a book using an ISBN
def delete_book(book_isbn: str) -> None:
    books = load_all()
    new_books = [book for book in books if book.get("isbn") != book_isbn]
    if len(new_books) == len(books):
        raise HTTPException(status_code=404, detail=f"Book '{book_isbn}' not found")
    save_all(new_books)
        
            
    