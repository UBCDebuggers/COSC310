from datetime import datetime

from app.repositories import analytics_repo
from app.repositories import books_repo, ratings_repo, users_repo
from app.services import ratings_service


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
