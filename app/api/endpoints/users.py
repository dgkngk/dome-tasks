from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.logger import dome_logger
from app.services.user_service import UserService
from app.models.user import UserModel

router = APIRouter()

@router.get("/me", response_model=UserModel)
async def read_users_me(current_user: Annotated[UserModel, Depends(get_current_user)]):
    return current_user