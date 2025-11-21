from datetime import datetime
from app.repositories import analytics_repo
from app.repositories import books_repo, ratings_repo, users_repo
from app.services import ratings_service



def rebuild_analytics():
    print("🔄 Rebuilding analytics.csv...")
    print("Writing to:", analytics_repo.DATA_PATH)

    # Load all core data
    books = books_repo.load_all()
    ratings = ratings_repo.load_all()
    users = users_repo.load_all()

    # Rating summaries (avg + count)
    rating_summary = ratings_service.get_ratings_summary()
    unique_users = ratings_service.get_unique_users_by_isbn()

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