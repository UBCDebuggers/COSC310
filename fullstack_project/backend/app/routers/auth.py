from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.authentication import LoginRequest, TokenResponse
from app.schemas.penalties import DEACTIVATED, PERMANENT_BAN, TEMPORARY_BAN
from app.services.penalties_service import get_penalties_for_user
from app.services.users_service import authenticate_user, create_user
from app.core.security import create_access_token, verify_access_token
from app.schemas.user import UserCreate
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.authentication import TokenResponse, LoginRequest

router = APIRouter(prefix= "/auth", tags=["auth"])

#Handles user logins
@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_202_ACCEPTED)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(LoginRequest(email = form_data.username, password = form_data.password))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    past_restrictions = None
    try:
        past_restrictions = get_penalties_for_user(user.userid)
    except HTTPException:
        pass
    restrictions =  min(past_restrictions, key=lambda r: abs(r.timestamp - datetime.now(timezone.utc))) if past_restrictions else None
    if restrictions and restrictions.active and restrictions.penalty_type in [PERMANENT_BAN, DEACTIVATED, TEMPORARY_BAN]:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= f"Your account has been suspended")
    access_token = create_access_token(data={"sub": user.userid, "admin" : user.is_admin, "username" : user.username, "email" : user.email})
    return TokenResponse(access_token=access_token)

#Creates a new user
@router.post('/signup', status_code=status.HTTP_201_CREATED)
async def user_signup(payload: UserCreate):
    user = create_user(payload)
    if not user:
        raise HTTPException(status_code=status.WS_1011_INTERNAL_ERROR, detail="Something went wrong while creating your profile please try again")
    
    access_token = create_access_token(data={"sub": user.userid, "admin" : user.is_admin, "username" : user.username, "email" : user.email})
    return TokenResponse(access_token=access_token)

#Verifies access token
@router.get("/verifytoken/{token}", status_code=status.HTTP_200_OK, response_model=dict, summary="Used by the frontend to validate a session") 
async def verify_token(token : str):
    verify_access_token(token)
    return {"message": "Token is valid"}
        
    

