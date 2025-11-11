from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os

_SECRET_KEY = os.getenv('SECRET_KEY')
_ALGORITHM = os.getenv('ALGORITHM')
_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data : dict):
    to_encode = data.copy() #returns the data as is
    expire = datetime.now(timezone.utc) + timedelta(minutes=_ACCESS_TOKEN_EXPIRE_MINUTES) 
    to_encode.update({"exp": expire}) #adds a field for the expiration datetime of the access token
    encoded_jwt = jwt.encode(to_encode, _SECRET_KEY, algorithm= _ALGORITHM)
    return encoded_jwt #returns an encoded token that cannot be hacked unless key exposed 

#attempts to decode the given token and returns the userid of the decoded string
def verify_access_token(token : str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, _SECRET_KEY, algorithms= [_ALGORITHM])
        userid : str = payload.get('userid')
        if userid:
            return userid
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        )