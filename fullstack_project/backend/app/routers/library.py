import csv
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from app.core.security import verify_access_token
from app.schemas.reservation import BookReservationCreate, BookReservation
from app.services.library_service import borrow_book, return_book
from app.services.reservation_service import build_user_reservation_report, get_reservations_by_userid, update_reservation

router = APIRouter(prefix="/library", tags=["library"], dependencies= [Depends(verify_access_token)])

@router.post("/borrow", status_code= status.HTTP_200_OK, response_model=dict)
async def borrow(reservation_id : str, payload : BookReservationCreate, current_user : dict = Depends(verify_access_token)):
    if current_user.get('is_admin'):
        return update_reservation(reservation_id, payload)
    else:
        return borrow_book(userid= current_user.get('userid'), isbn= payload.isbn, due_date= payload.expiry_date, is_admin= False)
    
@router.put("/return", status_code= status.HTTP_200_OK, response_model=dict)
async def book_return(userid : str, isbn :str, current_user : dict = Depends(verify_access_token)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "You do not have the privilege to complete this action")
    return return_book(userid, isbn)

@router.get("/userloans", status_code= status.HTTP_200_OK, response_model=List[BookReservation])
async def get_user_loans(userid : str, current_user : dict = Depends(verify_access_token)):
    if current_user.get('is_admin'):
        return get_reservations_by_userid(userid)
    return get_reservations_by_userid(current_user.get('userid'))

@router.get("/userloans/report", status_code=status.HTTP_200_OK)
async def download_user_loan_report(
    report_format: str = Query("csv", pattern="^(csv|json)$", description="Choose csv or json report"),
    userid: Optional[str] = Query(None, description="Admin-only override to download another user's report"),
    current_user: dict = Depends(verify_access_token),
):
    requested_user = userid or current_user.get("userid")

    if not current_user.get("is_admin") and userid and userid != current_user.get("userid"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot download another user's loan history.",
        )

    report_format = report_format.lower()
    report_rows = build_user_reservation_report(requested_user)

    filename = f"loan-report-{requested_user}.{report_format}"
    if report_format == "json":
        return JSONResponse(
            content=report_rows,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=report_rows[0].keys())
    writer.writeheader()
    writer.writerows(report_rows)
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
