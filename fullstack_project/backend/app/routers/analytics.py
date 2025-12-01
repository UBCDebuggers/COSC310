from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verify_access_token
from app.services import analytics_service
from app.repositories import analytics_repo
from typing import List, Dict, Any

router = APIRouter(prefix="/analytics", tags=["analytics"], dependencies=[Depends(verify_access_token)])

#    Fetch all analytics records from analytics.csv
@router.get("", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def get_all_analytics(limit: int = 100): # i limited it to 100 , bcuz the browser (NOT FASTAPI ) was crashing with 27k records , when it read the whole analytics.csv file.
    if limit < 1:
        raise HTTPException(status_code=400, detail="limit must be >= 1")
    analytics = analytics_repo.load_all()
    print("GET reading from:", analytics_repo.DATA_PATH)
    if not analytics:
        raise HTTPException(status_code=404, detail="No analytics data found.")
    return analytics[:limit]

#  Clears all analytics data. Only admins can perform this action.
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_analytics_data(token_data: dict = Depends(verify_access_token)):
    if not token_data["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    analytics_repo.save_all([])  # overwrites with empty file
    return None
#   Getter route to get the top N rated books based on rating_count
@router.get("/top-rated", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def get_top_rated_books_endpoint(n: int = 10):
    if n < 1:
        raise HTTPException(status_code=400, detail="n must be >= 1")
    top_books = analytics_service.get_top_rated_books(n)
    return top_books

# getter route to get the trending books based on request_count 
@router.get("/trending", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def api_trending(n: int = 10, token_data: dict = Depends(verify_access_token)):
    if not token_data["is_admin"]:
        raise HTTPException(403, "Admin access required")
    return analytics_service.get_trending_books(n)

# getter route to get genre popularity analytics
@router.get("/genres")
def api_genres(token_data: dict = Depends(verify_access_token)):
    if not token_data["is_admin"]:
        raise HTTPException(403, "Admin access required")
    return analytics_service.get_genre_popularity()