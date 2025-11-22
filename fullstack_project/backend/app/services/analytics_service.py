from datetime import datetime
from typing import List

from app.repositories import analytics_repo, books_repo, ratings_repo, users_repo
from app.services.ratings_service import get_ratings_summary, get_unique_users_by_isbn


def rebuild_analytics():
    """
    Regenerate analytics.csv using current books and ratings data.
    """
    books = books_repo.load_all()
    ratings_repo.load_all()  # no-op read; keeps parity with previous behavior
    users_repo.load_all()    # likewise

    rating_summary = get_ratings_summary()
    unique_users = get_unique_users_by_isbn()

    records = []
    today = datetime.now().strftime("%Y-%m-%d")

    for book in books:
        isbn = book.get("isbn")
        r = rating_summary.get(isbn, {"count": 0, "avg": 0})
        user_list = unique_users.get(isbn, [])

        records.append(
            {
                "date": today,
                "book_id": isbn,
                "title": book.get("title", "Unknown"),
                "request_count": "0",
                "rating_count": str(r["count"]),
                "avg_rating": str(r["avg"]),
                "unique_users": str(len(user_list)),
            }
        )

    analytics_repo.save_all(records)


def get_top_rated_books(n: int) -> List[dict]:
    rating_summary = get_ratings_summary()
    sorted_books = sorted(
        rating_summary.items(), key=lambda x: x[1]["count"], reverse=True
    )
    top_books = sorted_books[:n]

    result = []
    for isbn, data in top_books:
        result.append(
            {"isbn": isbn, "rating_count": data["count"], "avg_rating": data["avg"]}
        )
    return result


def get_trending_books(n: int) -> List[dict]:
    analytics = analytics_repo.load_all()
    book_trends = {}
    for record in analytics:
        book_id = record["book_id"]
        request_count = int(record["request_count"])
        if book_id not in book_trends:
            book_trends[book_id] = 0
        book_trends[book_id] += request_count

    sorted_trends = sorted(book_trends.items(), key=lambda x: x[1], reverse=True)
    top_trending = sorted_trends[:n]

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
        result.append(
            {
                "book_id": book_id,
                "total_requests": total_requests,
                "delta_requests": delta,
            }
        )

    result.sort(key=lambda x: x["delta_requests"], reverse=True)
    return result[:n]


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

    genre_list = [
        {"genre": genre, "total_rating_count": count}
        for genre, count in genre_counts.items()
    ]
    genre_list.sort(key=lambda x: x["total_rating_count"], reverse=True)

    return genre_list
