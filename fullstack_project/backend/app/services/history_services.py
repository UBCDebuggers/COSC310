from app.repositories.history_repo import load_all

# Checks if a student has opened a book before (using history.csv)
def User_opening_book(user_id: str, book_isbn: str) -> bool:
    try:
        lines = load_all()
        for line in lines[1:]:  # Skip header
            record = line.strip().split('; ')
            if len(record) >= 2:
                record_user_id, record_isbn = record[0], record[1]
                if record_user_id == user_id and record_isbn == book_isbn:
                    return True
    except FileNotFoundError:
        pass
    return False