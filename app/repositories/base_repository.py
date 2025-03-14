from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, TypeVar, Dict, Any
from bson.objectid import ObjectId
from app.db.database import get_database, connect_to_mongo

class BaseRepository:
    DocumentType = TypeVar('DocumentType', Dict[str, Any], str)
    def __init__(self, collection_name: str):
        self.db = get_database()
        self.collection: AsyncIOMotorCollection = self.db[collection_name]
        
    async def create(self, document_data: dict) -> str:
        result = await self.collection.insert_one(document_data)
        return str(result.inserted_id)
    
    async def find_by_id(self, user_id: str) -> dict:
        return await self.collection.find_one({"_id": ObjectId(user_id)})
    
    async def find_all(self) -> List[DocumentType]:
        cursor = self.collection.find()
        documents = [document async for document in cursor]
        return documents
    
    async def update(self, document_id: str, update_data: dict) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def delete(self, document_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0

