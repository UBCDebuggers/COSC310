from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.authentication import LoginRequest, TokenResponse
from app.services.users_service import authenticate_user, create_user
from app.core.security import create_access_token
from app.schemas.user import UserCreate
from datetime import timedelta, datetime, timezone
from typing import Annotated
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from dotenv import load_dotenv
import os
from app.schemas.user import User
from app.schemas.authentication import TokenResponse, LoginRequest

router = APIRouter(prefix= "/auth", 
                   tags=["auth"])

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_202_ACCEPTED)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(LoginRequest(username_email = form_data.username, password = form_data.password))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.userid, "admin" : user.is_admin})
    return TokenResponse(access_token=access_token)

@router.post('/signup', status_code=status.HTTP_201_CREATED)
async def user_signup(payload: UserCreate):
    user = create_user(UserCreate(**payload))
    if not user:
        raise HTTPException(status_code=status.WS_1011_INTERNAL_ERROR, detail="Something went wrong while creating your profile please try again")
    
    access_token = create_access_token(data={"sub": user.userid, "admin" : user.is_admin})
    return TokenResponse(access_token=access_token)
        
    

