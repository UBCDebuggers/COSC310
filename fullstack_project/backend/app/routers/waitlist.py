"""Router for waitlist endpoints."""
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator

from app.services import waitlist_service as ws
from app.repositories import waitlist_repo as wr

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/waitlist", tags=["waitlist"])


class JoinWaitlistRequest(BaseModel):
    """Request schema for joining a waitlist.
    
    Uses Pydantic validation for email format (requires python-multipart or email-validator).
    If email validation fails, you can remove EmailStr and use str instead.
    """
    userid: str
    email: str
    
    @field_validator('userid')
    @classmethod
    def userid_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('userid cannot be empty')
        return v.strip()
    
    @field_validator('email')
    @classmethod
    def email_format(cls, v):
        if not v or '@' not in v:
            raise ValueError('email must be valid')
        return v.strip().lower()


@router.post("/{isbn}/join", status_code=201)
def join_waitlist(isbn: str, req: JoinWaitlistRequest):
    """Add a user to a book's waitlist.
    
    Args:
        isbn: Book ISBN
        req: JoinWaitlistRequest with userid and email
    
    Returns:
        Created waitlist entry
    
    Raises:
        HTTPException 400 if isbn is empty
        HTTPException 500 if persistence fails
    """
    if not isbn or not isbn.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ISBN cannot be empty"
        )
    
    try:
        entry = wr.add_to_waitlist(req.userid, isbn.strip(), req.email)
        logger.info(f"User {req.userid} added to waitlist for ISBN {isbn}")
        return entry
    except Exception as e:
        logger.error(f"Error adding to waitlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add to waitlist: {str(e)}"
        )


@router.post("/{isbn}/available", status_code=200)
def mark_book_available(isbn: str):
    """Trigger notifications for all users on a book's waitlist.
    
    This endpoint is typically called by admin or library staff when a book
    becomes available. It creates notifications and sends emails to all
    waitlisted users (in the background or synchronously per config).
    
    Args:
        isbn: Book ISBN
    
    Returns:
        Dict with count of users notified
    
    Raises:
        HTTPException 400 if isbn is empty
        HTTPException 500 if notification creation fails
    """
    if not isbn or not isbn.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ISBN cannot be empty"
        )
    
    try:
        notified_count = ws.notify_waitlist(isbn.strip())
        logger.info(f"Notified {notified_count} users for available ISBN {isbn}")
        return {
            "isbn": isbn,
            "notified_count": notified_count,
            "message": f"Notified {notified_count} users"
        }
    except Exception as e:
        logger.error(f"Error notifying waitlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to notify waitlist: {str(e)}"
        )


@router.get("/{isbn}", status_code=200)
def get_waitlist(isbn: str):
    """Get all users on a book's waitlist.
    
    Args:
        isbn: Book ISBN
    
    Returns:
        List of waitlist entries for the book
    """
    if not isbn or not isbn.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ISBN cannot be empty"
        )
    
    try:
        entries = wr.get_waitlist_for_isbn(isbn.strip())
        logger.info(f"Retrieved {len(entries)} waitlist entries for ISBN {isbn}")
        return entries
    except Exception as e:
        logger.error(f"Error retrieving waitlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve waitlist: {str(e)}"
        )