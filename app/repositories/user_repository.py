from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime, timezone
from app.repositories.base_repository import BaseRepository
from app.core.security import get_password_hash
from bson.objectid import ObjectId
from typing import Dict, Any


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__("users")
        self.collection.create_index([("email", 1)], unique=True)
    
    async def create_user(self, user_data: dict) -> str:
        return await super().create(user_data)
    
    async def find_by_email(self, email: str) -> dict:
        return await self.find_by_query({"email": email})
    
    async def find_by_query(self, query: Dict[str, Any]) -> dict:
        return await self.collection.find_one(query)
    