from app.repositories.user_repository import UserRepository
from app.models.user import UserModel, UserCreate
from app.core.security import get_password_hash, verify_password
from app.core.logger import dome_logger

from typing import Optional
from datetime import datetime, timezone


class UserService:
    def __init__(self):
        self.repository = UserRepository()
    
    async def create(self, user_data: dict) -> str:
        try:
            hashed_password = get_password_hash(user_data.pop("password"))
            user_create = UserCreate(
                email=user_data.pop('email'),
                password_hash=hashed_password,
                name=user_data.pop('name'),
                photo_url=user_data.pop('photo_url', None)
                )
            
            user_id = await self.repository.create_user(user_create.model_dump())
            return str(user_id)
        except Exception as e:
            dome_logger.error(f"Error creating user: {e}")
            return None
    
    async def get_by_id(self, user_id: str) -> Optional[UserModel]:
        try:
            user_document = await self.repository.find_by_id(user_id)
            if user_document:
                return UserModel(**user_document).model_dump()
            return None
        except Exception as e:
            dome_logger.error(f"Error getting user by ID: {e}")
            return None
    
    async def get_by_email(self, email: str) -> Optional[UserModel]:
        try:
            user_document = await self.repository.find_by_email(email)
            if user_document:
                return UserModel(**user_document).model_dump()
            return None
        except Exception as e:
            dome_logger.error(f"Error getting user by email: {e}")
            return None
    
    async def update(self, user_id: str, update_data: dict) -> bool:
        try:
            user_document = await self.repository.find_by_id(user_id)
            if not user_document:
                return False
            
            update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            updated_data = user_document | update_data
            
            result = await self.repository.update(
                user_id, UserModel(**updated_data).model_dump()
                )
            return result
        except Exception as e:
            dome_logger.error(f"Error updating user: {e}")
            return False
    
    async def delete(self, user_id: str) -> bool:
        try:
            return await self.repository.delete(user_id)
        except Exception as e:
            dome_logger.error(f"Error deleting user: {e}")
            return False