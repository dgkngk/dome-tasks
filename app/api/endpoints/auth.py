from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from datetime import timedelta

from app.core.auth import create_access_token, authenticate_user
from app.core.config import settings
from app.core.logger import dome_logger
from app.services.user_service import UserService

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user["id"], expires_delta=access_token_expires
    )
    response = RedirectResponse("/",status_code=status.HTTP_202_ACCEPTED)
    response.set_cookie(
        key="DomeToken", 
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        samesite="lax"
    )
    
    return response

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    name: Annotated[str, Form()],
    password: Annotated[str, Form()],
    email: Annotated[str, Form()],
    photo_url: Annotated[Optional[str], Form()] = None,
    ):
    # Check if user already exists
    existing_user = await UserService().get_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    user_id = await UserService().create(
        {
            "name": name,
            "password": password,
            "email": email,
            "photo_url": photo_url
        }
    )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user due to internal error"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user_id, expires_delta=access_token_expires
    )
    
    return {"message": "User created successfully", "user_id": user_id, "access_token": access_token, "token_type": "bearer"}
    