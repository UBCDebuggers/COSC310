from datetime import datetime
from typing import List

from fastapi import HTTPException

from app.repositories import analytics_repo, books_repo, ratings_repo, users_repo
from app.services.ratings_service import get_ratings_summary, get_unique_users_by_isbn
from app.services.reservation_service import get_reservations_by_isbn

#Refactor method for rebuild_analytics : Loads all foundational datasets required for analytics.
def load_foundational_data():
    books = books_repo.load_all()
    ratings = ratings_repo.load_all()
    users = users_repo.load_all()
    return books, ratings, users

#Refactor method for rebuild_analytics  : Creates a normalized analytics record for CSV storage.
def make_analytics_record(book: dict, rating_summary: dict, unique_users: list , today: str) -> dict:
    book_id = book.get('isbn')
    requests = None
    try:
        requests = len(get_reservations_by_isbn(book_id))
    except HTTPException:
        requests = 0
    return{
        "date": today,
        "book_id": book_id,
        "title": book.get("title", "Unknown"),
        "request_count": requests,                     
        "rating_count": str(rating_summary.get("count", 0)),           
        "avg_rating": str(rating_summary.get("avg", 0)),            
        "unique_users": str(len(unique_users))
    }

# Rebuilds the analytics dataset by aggregating ratings, books,
# and user activity. Produces a fresh analytics.csv file.
# core_data[0] is books,core_data[1] is ratings, core_data[2] is users . refactoring done in load_foundational_data
def rebuild_analytics():
    print("🔄 Rebuilding analytics.csv...")
    print("Writing to:", analytics_repo.DATA_PATH)

    core_data = load_foundational_data()
    rating_summary = get_ratings_summary()
    unique_users = get_unique_users_by_isbn()

    records = []
    today = datetime.now().strftime("%Y-%m-%d")

    for book in core_data[0]:  
        isbn = book.get("isbn")
        r = rating_summary.get(isbn, {"count": 0, "avg": 0})
        user_list = unique_users.get(isbn, [])

        record = make_analytics_record(
            book = book,
            rating_summary = r,
            unique_users = user_list,
            today = today
            )
        
        records.append(record)

    analytics_repo.save_all(records)
    print("✅ Finished rebuilding analytics.csv")


#Refactor method for get_trending_books : Aggregates request_count per book across all analytics entries
def _compute_request_counts(records):
    total_requests = {}
    for record in records:
        book_id = record["book_id"]
        request_count = int(record["request_count"])
        if book_id not in total_requests:
            total_requests[book_id] = 0
        total_requests[book_id] += request_count
    return total_requests

#Refactor method for get_trending_books : Computes request delta between the two most recent records.
def _compute_delta_requests(records, book_id):
    book_records = [r for r in records if r["book_id"] == book_id]
    book_records.sort(key=lambda x: x["date"], reverse=True)
    if len(book_records) >= 2:
        latest_count = int(book_records[0]["request_count"])
        previous_count = int(book_records[1]["request_count"])
        delta = latest_count - previous_count
    else:
        delta = 0
    return delta


# Sort books by rating_count (descending). Return top N.
def get_top_rated_books(n: int) -> List[dict]:
    rating_summary = get_ratings_summary()
    sorted_books = sorted(rating_summary.items(), key=lambda x: x[1]['count'], reverse=True)
    top_rated = sorted_books[:n]
    
    result = []
    for isbn, data in top_rated:
        result.append({
            "isbn": isbn,
            "rating_count": data['count'],
            "avg_rating": data['avg']
        })
    return result

#    Identifies books trending upward based on request count deltas.
def get_trending_books(n: int) -> List[dict]:
    analytics = analytics_repo.load_all()
    total_requests = _compute_request_counts(analytics)
    sorted_totals = sorted(total_requests.items(), key=lambda x: x[1], reverse=True)
    top_trending = sorted_totals[:n]
    result = []
    #take last 2 records for each book and compute delta

    for book_id, total_requests in top_trending:
        delta = _compute_delta_requests(analytics, book_id)
        result.append({
            "book_id": book_id,
            "total_requests": total_requests,
            "delta_requests": delta
        })
    #Sort books by delta (descending). Return top N.
    result.sort(key=lambda x: x["delta_requests"], reverse=True)
    return result[:n]


#Refactor method for get_genre_popularity: Creates a dictionary mapping each ISBN to its genres
def _map_isbn_to_genres(books) -> dict:
    isbn_to_genres = {}
    for book in books:
        isbn = book.get("isbn")
        genres = book.get("genres", [])
        isbn_to_genres[isbn] = genres
    return isbn_to_genres     

##Refactor method for get_genre_popularity : Aggregates rating_count per genre across all analytics records
def _aggregate_genre_counts(records, isbn_to_genres) -> dict:
    genre_counts = {}
    for record in records:
        isbn = record["book_id"]
        rating_count = int(record["rating_count"])
        genres = isbn_to_genres.get(isbn, [])

        for genre in genres:
            if genre not in genre_counts:
                genre_counts[genre] = 0
            genre_counts[genre] += rating_count
    return genre_counts

#genre most viewed → based on sum of rating_counts grouped by genre, refactored using the 2 helper functions above
def get_genre_popularity() -> List[dict]:
    records = analytics_repo.load_all()
    books = books_repo.load_all()

    isbn_to_genres = _map_isbn_to_genres(books)
    genre_counts = _aggregate_genre_counts(records, isbn_to_genres)

    genre_list = [{"genre": genre, "total_rating_count": count} for genre, count in genre_counts.items()]
    genre_list.sort(key=lambda x: x["total_rating_count"], reverse=True)

    return genre_list
