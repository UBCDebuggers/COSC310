from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from typing import Annotated

load_dotenv()

_SECRET_KEY = os.getenv('SECRET_KEY', 'e84d75f99d5c47b299a0de7f6920e572')
_ALGORITHM = os.getenv('ALGORITHM', "HS256")
_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 60))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

#creates an encrypted token using given data
def create_access_token(data : dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=_ACCESS_TOKEN_EXPIRE_MINUTES) 
    to_encode.update({"exp": expire}) 
    encoded_jwt = jwt.encode(to_encode, _SECRET_KEY, algorithm= _ALGORITHM)
    return encoded_jwt  

#attempts to decode the given token and returns the userid of the decoded string
def verify_access_token(token : str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, _SECRET_KEY, algorithms= [_ALGORITHM])
        userid : str = payload.get('sub') or payload.get('userid')
        is_admin : bool = bool(payload.get('admin'))
        if userid is None:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
            )
            
        return {'userid': userid, 'is_admin' : is_admin}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        )

user_dependency = Annotated[dict, Depends(verify_access_token)]