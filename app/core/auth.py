from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from pydantic import BaseModel

from app.core.logger import dome_logger
from app.core.config import settings
from app.services.user_service import UserService
from app.core.security import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class AuthCookie(BaseModel):
    DomeToken: Optional[str] = None

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.CRYPT_ALGO)
    return encoded_jwt

async def get_auth_token_from_cookie(auth_cookie: Annotated[AuthCookie, Cookie()]):
    if not auth_cookie:
        return None
    return auth_cookie.DomeToken

async def get_current_user(token: str = Depends(get_auth_token_from_cookie)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if not token:
            raise credentials_exception
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.CRYPT_ALGO])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token has been expired")
    except JWTError as e:
        dome_logger.exception(f"Token error:{e}")
        raise credentials_exception
   
    
    user = await UserService().get_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user

async def authenticate_user(email: str, password: str):
        user = await UserService().get_by_email(email)
        if not user or not verify_password(password, user["password_hash"]):
            return None
        
        return user
