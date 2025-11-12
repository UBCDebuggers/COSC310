from app.repositories import analytics_repo
from app.services import books_service, ratings_service
from datetime import datetime

def rebuild_analytics():
    print("🔄 Rebuilding analytics.csv...")

    # Load rating summaries (avg + count)
    rating_summary = ratings_service.get_ratings_summary()
    unique_users_map = ratings_service.get_unique_users_by_isbn()

    records = []
    date_today = datetime.now().strftime("%Y-%m-%d")

    # Go through all books
    for book in books_service.BOOKS:
        isbn = book.get("isbn")

        # Get metrics if they exist
        rating_data = rating_summary.get(isbn, {"count": 0, "avg": 0})
        users = unique_users_map.get(isbn, [])

        record = {
            "date": date_today,
            "book_id": isbn,
            "title": book.get("title", "Unknown"),
            "request_count": 0,  # optional if you don't have requests yet
            "rating_count": rating_data["count"],
            "avg_rating": rating_data["avg"],
            "unique_users": len(users)
        }
        records.append(record)

    analytics_repo.save_all(records)
    print(f"✅ analytics.csv updated with {len(records)} records.")

if __name__ == "__main__":
    rebuild_analytics()
