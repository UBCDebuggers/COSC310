import re
from collections import Counter
from typing import List
from fastapi import HTTPException
from app.schemas.book import Book, BookCreate, BookUpdate
from app.repositories.books_repo import load_all, save_all

#Searches for a book by its title given a string. Returns the top 10 books that have the most matches by characters and words
def search_books(tokens : str) -> List[Book]:
    books = load_all()
    results_list = []
    for book in books:
        title = book.get('title')
        
        title = title.lower()
        tokens = tokens.lower()
        
        char_hits = search_by_char(title, tokens)
        word_hits = search_by_string(title, tokens)
        
        results_list.append({"char_hits" : char_hits, 
                             "word_hits": word_hits, 
                             "isbn": book.get('isbn'), 
                             "title" : title})
        
    results_list = sorted( results_list, key=lambda item: (
        -item["word_hits"],  
        -item["char_hits"],  
        item["title"]        
        ))
    results_list = results_list[:10]
    results_list = [get_book_by_isbn(book.get("isbn")) for book in results_list]
    
    return results_list
        
#Checks for how many letters from each string match each other
def search_by_char(string : str, compare : str) -> int:
    total_hits = 0
    string_counts = Counter(string)
    for char_compare in set(compare):
        if char_compare in string_counts:
            total_hits += string_counts[char_compare]
            
    return total_hits

#Checks for how many words from each string match a word in the other string
def search_by_string(string : str, compare :str) -> int:
    total_hits = 0
    words = re.split(r"[ .,/?;()]", compare)
    clean_words = [word for word in words if word]
    for word in clean_words:
        if word in string:
            total_hits += 1
    return total_hits
            

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
        if book.get('isbn') == book_isbn:
            return Book(**book)
    raise HTTPException(status_code=404, detail=f"Book '{book_isbn}' not found")

def update_book(book_isbn: str, bookUpdate : BookUpdate) -> Book:
    books = load_all()
    for id, book in enumerate(books):
        if book.get("isbn") == book_isbn:
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
    new_books = [book for book in books if book.get("isbn") != book_isbn]
    if len(new_books) == len(books):
        HTTPException(status_code=404, detail=f"Book '{book_isbn}' not found")
    save_all(new_books)
        
            
    