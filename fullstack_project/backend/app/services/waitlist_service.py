import logging
from app.repositories import waitlist_repo as wr
from app.repositories import notification_repo as nr
from app.services import email_service

logger = logging.getLogger(__name__)

# Notifies all users on the waitlist for a given ISBN; creates notifications and sends emails; returns the count of users notified.
def notify_waitlist(isbn: str) -> int:
    try:
        entries = wr.get_waitlist_for_isbn(isbn)
        count = 0

        for entry in entries:
            try:
                user_id = entry.get("userid")
                email = entry.get("email")

                # Create notification in database
                nr.add_notification(
                    userid=user_id,
                    notification_type="waitlist",
                    category="book_available",
                    message=f"Book with ISBN {isbn} is now available!",
                    relatedid=isbn
                )

                # Send email notification
                email_service.send_notification_email(
                    to_email=email,
                    notification_type="waitlist",
                    category="book_available",
                    message=f"The book with ISBN {isbn} is now available for checkout."
                )

                count += 1
                logger.info(f"Notified user {user_id} for ISBN {isbn}")

            except Exception as e:
                logger.error(f"Failed to notify user for ISBN {isbn}: {e}")
                continue

        # Delete waitlist entries after notifications
        wr.delete_waitlists_for_book(isbn)
        logger.info(f"Removed {count} waitlist entries for ISBN {isbn}")

        return count

    except Exception as e:
        logger.error(f"Error in notify_waitlist for ISBN {isbn}: {e}")
        return 0
