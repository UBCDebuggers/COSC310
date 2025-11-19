from datetime import datetime
from collections import defaultdict
from app.repositories import analytics_repo
from app.repositories import books_repo, ratings_repo, users_repo
from app.services import ratings_service
from statistics import mean

def _load_analytics():
    return analytics_repo.load_all()
#    Returns the top N books ranked by average rating. This directly supports my FR-05.1 and User story number 8.
def get_top_rated_books(limit: int = 10):

    analytics = _load_analytics()
    results = []

    for row in analytics:
        try:
            avg_rating = float(row.get("avg_rating", 0))
        except ValueError:
            avg_rating = 0

        results.append({
            "isbn": row.get("book_id"),
            "title": row.get("title", "Unknown"),
            "avg_rating": avg_rating,
            "rating_count": int(row.get("rating_count", 0)),
        })

    # Sort by avg_rating (desc), then by rating_count
    results.sort(key=lambda x: (x["avg_rating"], x["rating_count"]), reverse=True)
    return results[:limit]

def get_trending_books(limit: int = 10):
    """
    Defines 'trending' simply as: high rating_count + high unique_users.
    (A simple but effective trend signal for assignment scoring)
    """
    analytics = _load_analytics()
    results = []

    for row in analytics:
        try:
            rating_count = int(row.get("rating_count", 0))
            unique_users = int(row.get("unique_users", 0))
        except ValueError:
            rating_count, unique_users = 0, 0

        trend_score = rating_count + unique_users  # simple metric

        results.append({
            "isbn": row.get("book_id"),
            "title": row.get("title", "Unknown"),
            "trend_score": trend_score,
            "rating_count": rating_count,
            "unique_users": unique_users,
        })

    # sort by trend_score desc
    results.sort(key=lambda x: x["trend_score"], reverse=True)
    return results[:limit]



# Small helper that bundles rating summary + unique users for a given ISBN.
# This keeps the main rebuild loop cleaner and avoids repeating lookups.
# Extracting this also makes it easier to test in isolation.

def _get_rating_metadata(isbn, rating_summary, unique_users):
    rating_info = rating_summary.get(isbn, {"count": 0, "avg": 0})
    user_list = unique_users.get(isbn, [])

    return rating_info, user_list


# Helper that converts the raw data into the final analytics CSV record.
# Extracting this makes it easier to read and avoids having a huge loop body.
def _build_analytics_record(book, today, rating_info, user_list):
    isbn = book.get("isbn")

    return {
        "date": today,
        "book_id": isbn,
        # Preserve behavior: fallback to "Unknown" if title missing.
        "title": book.get("title", "Unknown"),
        "request_count": "0",                   # intentionally always zero for M3
        "rating_count": str(rating_info["count"]),
        "avg_rating": str(rating_info["avg"]),
        "unique_users": str(len(user_list))
    }


def rebuild_analytics():
    print("🔄 Rebuilding analytics.csv...")
    print("Writing to:", analytics_repo.DATA_PATH)

    # here we are going to get the data we need from the various repos
    books = books_repo.load_all()
    ratings = ratings_repo.load_all()
    users = users_repo.load_all()

    # Summaries derived from ratings
    rating_summary = ratings_service.get_ratings_summary()
    unique_users = ratings_service.get_unique_users_by_isbn()

    today = datetime.now().strftime("%Y-%m-%d")
    records = []

    for book in books:
        isbn = book.get("isbn")
        rating_info, user_list = _get_rating_metadata(isbn, rating_summary, unique_users)
        record = _build_analytics_record(book, today, rating_info, user_list)
        records.append(record)

    analytics_repo.save_all(records)

    print("✅ Finished rebuilding analytics.csv")
