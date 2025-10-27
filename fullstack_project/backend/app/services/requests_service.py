import uuid
from datetime import datetime
from typing import List
from fastapi import HTTPException
from app.schemas.requests import Request, RequestCreate
from app.repositories.requests_repo import load_all, save_all

def list_list_requests() -> List[Request]:
    return [Request(**attributes) for attributes in load_all()]

def create_request(newRequest: RequestCreate) -> Request:
    requests = load_all()
    new_id = str(uuid.uuid4())
    current_datetime = datetime.now()
    if any(request.get("requestid") == new_id for request in requests):
        raise HTTPException(status_code=409, detail="Rating collision; retry.")
    
    new_record = Request(requestid = new_id,
                         userid= newRequest.userid,
                         timestamp = current_datetime,
                         request_type = newRequest.request_type.strip(),
                         details = newRequest.details.strip(),
                         error_code= newRequest.error_code
                         )
    requests.append(new_record.model_dump())
    save_all(requests)
    return new_record

def get_request_by_userid(requestid: str) -> Request:
    requests = load_all()
    found = []
    for request in requests:
        if request.get('requestid') == requestid:
            found.append(Request(**request))
    if not found:
        raise HTTPException(status_code=404, detail=f"Rating for ISBN '{requestid}' not found")
    return found

def get_request_by_id(requestid: str) -> Request:
    found = []
    requests = load_all()
    for request in requests:
        if requests.get('requestid') == requestid:
            found.append(Request(**request))
    if not found:
        raise HTTPException(status_code=404, detail=f"Rating for User-ID '{requestid}' not found")
    return found

def delete_request(requestid: str) -> None:
    requests = load_all()
    new_list_requests = [request for request in requests if request.get("requestid") != requestid]
    if len(new_list_requests) == len(requests):
        HTTPException(status_code=404, detail=f"Request '{requestid}' not found")
    save_all(new_list_requests)
        
            
    