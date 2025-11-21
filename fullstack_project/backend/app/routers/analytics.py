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


#   Rebuild the analytics.csv file. Only admins can rebuild analytics since it regenerates all records.
@router.post("/rebuild", status_code=status.HTTP_200_OK)
def rebuild_analytics_endpoint(token_data: dict = Depends(verify_access_token)):
    if not token_data["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    analytics_service.rebuild_analytics()
    return {"message": "✅ Analytics successfully rebuilt."}

#  Clears all analytics data. Only admins can perform this action.
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_analytics_data(token_data: dict = Depends(verify_access_token)):
    if not token_data["is_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    analytics_repo.save_all([])  # overwrites with empty file
    return None