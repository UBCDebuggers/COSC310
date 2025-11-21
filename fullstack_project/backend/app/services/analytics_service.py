from datetime import datetime
from app.repositories import analytics_repo
from app.repositories import books_repo, ratings_repo, users_repo
from app.services import ratings_service
from typing import List
from app.services.ratings_service import get_ratings_summary, get_unique_users_by_isbn


        
def rebuild_analytics():
    print("🔄 Rebuilding analytics.csv...")
    print("Writing to:", analytics_repo.DATA_PATH)

    # Load all core data
    books = books_repo.load_all()
    ratings = ratings_repo.load_all()
    users = users_repo.load_all()

    # Rating summaries (avg + count)
    rating_summary = get_ratings_summary()
    unique_users = get_unique_users_by_isbn()

    records = []
    today = datetime.now().strftime("%Y-%m-%d")

    for book in books:
        isbn = book.get("isbn")

        # Existing rating data
        r = rating_summary.get(isbn, {"count": 0, "avg": 0})
        user_list = unique_users.get(isbn, [])

        record = {
            "date": today,
            "book_id": isbn,
            "title": book.get("title", "Unknown"),
            "request_count": "0",                      # fixed: string
            "rating_count": str(r["count"]),           # fixed: ensure string
            "avg_rating": str(r["avg"]),               # fixed: correct name
            "unique_users": str(len(user_list))        # fixed: ensure string
        }


        records.append(record)

    analytics_repo.save_all(records)
    print("✅ Finished rebuilding analytics.csv")


# Sort books by rating_count (descending). Return top N.
def get_top_rated_books(n: int) -> List[dict]:
    rating_summary = get_ratings_summary()
    sorted_books = sorted(rating_summary.items(), key=lambda x: x[1]['count'], reverse=True)
    top_books = sorted_books[:n]
    
    result = []
    for isbn, data in top_books:
        result.append({
            "isbn": isbn,
            "rating_count": data['count'],
            "avg_rating": data['avg']
        })
    return result


def get_trending_books(n: int) -> List[dict]:
    analytics = analytics_repo.load_all()
    #group by book_id 
    book_trends = {}
    for record in analytics:
        book_id = record["book_id"]
        request_count = int(record["request_count"])
        if book_id not in book_trends:
            book_trends[book_id] = 0
        book_trends[book_id] += request_count

    #sort rows for each book by date
    sorted_trends = sorted(book_trends.items(), key=lambda x: x[1], reverse=True)
    top_trending = sorted_trends[:n]    
    #take last 2 records for each book and compute delta
    result = []
    for book_id, total_requests in top_trending:
        book_records = [r for r in analytics if r["book_id"] == book_id]
        book_records.sort(key=lambda x: x["date"], reverse=True)
        if len(book_records) >= 2:
            latest_count = int(book_records[0]["request_count"])
            previous_count = int(book_records[1]["request_count"])
            delta = latest_count - previous_count
        else:
            delta = 0
        result.append({
            "book_id": book_id,
            "total_requests": total_requests,
            "delta_requests": delta
        })
    #Sort books by delta (descending). Return top N.
    result.sort(key=lambda x: x["delta_requests"], reverse=True)
    return result[:n]


     
#genre most viewed → based on sum of rating_counts grouped by genre

def get_genre_popularity() -> List[dict]:
    records = analytics_repo.load_all()
    books = books_repo.load_all()
    
    genre_counts = {}
    
    isbn_to_genres = {}
    for book in books:
        isbn = book.get("isbn")
        genres = book.get("genres", [])
        isbn_to_genres[isbn] = genres
    
    for record in records:
        isbn = record["book_id"]
        rating_count = int(record["rating_count"])
        genres = isbn_to_genres.get(isbn, [])
        
        for genre in genres:
            if genre not in genre_counts:
                genre_counts[genre] = 0
            genre_counts[genre] += rating_count
    

    genre_list = [{"genre": genre, "total_rating_count": count} for genre, count in genre_counts.items()]
    genre_list.sort(key=lambda x: x["total_rating_count"], reverse=True)
    
    return genre_list

