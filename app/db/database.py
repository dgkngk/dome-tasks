from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.logger import dome_logger
from typing import Dict, Any, List, Optional
import time
from bson import ObjectId
from datetime import datetime

class ConnectionError(Exception):
    """Raised when database connection fails"""

class NotFoundError(Exception):
    """Raised when a document isn't found"""

class MongoDBConnector:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self._max_retries = 3
        self._retry_delay = 0.5

    async def connect(self):
        """Connect with retry logic"""
        attempts = 0
        while attempts < self._max_retries:
            try:
                self.client = AsyncIOMotorClient(
                    settings.MONGO_URI,
                    maxPoolSize=100,
                    minPoolSize=10,
                    serverSelectionTimeoutMS=5000
                )
                self.db = self.client[settings.MONGO_DB]
                await self.client.server_info()
                dome_logger.info("Connected to MongoDB!")
                return
            except Exception as e:
                attempts += 1
                dome_logger.warning(f"Connection attempt {attempts} failed: {str(e)}")
                if attempts == self._max_retries:
                    raise ConnectionError(f"Failed to connect after {self._max_retries} attempts") from e
                time.sleep(self._retry_delay)

    async def close(self):
        """Close connection gracefully"""
        if self.client:
            self.client.close()
            self.db = None
            dome_logger.info("Disconnected from MongoDB")

    def _handle_connection_error(self):
        """Raise standardized connection error"""
        raise ConnectionError("Database connection not established")

    def _serialize(self, document: Dict) -> Dict:
        """Convert Pydantic models and special types to MongoDB format"""
        for key, value in document.items():
            if isinstance(value, ObjectId):
                document[key] = str(value)
            elif isinstance(value, datetime):
                document[key] = value.isoformat()
        return document

    def _deserialize(self, document: Dict) -> Dict:
        """Convert MongoDB formats to Python types"""
        if document:
            document['_id'] = str(document['_id'])
            if 'created_at' in document:
                document['created_at'] = datetime.fromisoformat(document['created_at'])
            if 'updated_at' in document:
                document['updated_at'] = datetime.fromisoformat(document['updated_at'])
        return document

    async def create(self, collection: str, document: Dict) -> str:
        """Insert document with retry logic"""
        if not self.db:
            self._handle_connection_error()
        
        doc = self._serialize(document)
        try:
            result = await self.db[collection].insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            dome_logger.error(f"Create operation failed: {str(e)}")
            raise

    async def find(self, collection: str, document_id: str) -> Optional[Dict]:
        """Find document by ID"""
        if not self.db:
            self._handle_connection_error()
        
        try:
            doc = await self.db[collection].find_one({"_id": ObjectId(document_id)})
            return self._deserialize(doc) if doc else None
        except Exception as e:
            dome_logger.error(f"Find operation failed: {str(e)}")
            raise NotFoundError(f"Document {document_id} not found") from e

    async def find_all(self, collection: str, query: Dict = None) -> List[Dict]:
        """Find all documents matching query"""
        if not self.db:
            self._handle_connection_error()
        
        try:
            cursor = self.db[collection].find(query or {})
            return [self._deserialize(doc) async for doc in cursor]
        except Exception as e:
            dome_logger.error(f"Find all operation failed: {str(e)}")
            raise

    async def update(self, collection: str, document_id: str, update_data: Dict) -> bool:
        """Update document with atomic operations"""
        if not self.db:
            self._handle_connection_error()
        
        try:
            result = await self.db[collection].update_one(
                {"_id": ObjectId(document_id)},
                {"$set": self._serialize(update_data)}
            )
            if result.matched_count == 0:
                raise NotFoundError(f"Document {document_id} not found")
            return result.modified_count > 0
        except Exception as e:
            dome_logger.error(f"Update operation failed: {str(e)}")
            raise

    async def delete(self, collection: str, document_id: str) -> bool:
        """Delete document by ID"""
        if not self.db:
            self._handle_connection_error()
        
        try:
            result = await self.db[collection].delete_one({"_id": ObjectId(document_id)})
            if result.deleted_count == 0:
                raise NotFoundError(f"Document {document_id} not found")
            return result.deleted_count > 0
        except Exception as e:
            dome_logger.error(f"Delete operation failed: {str(e)}")
            raise

# Initialize connector instance
db_connector = MongoDBConnector()

async def connect_to_mongo():
    """Initialize connection wrapper"""
    await db_connector.connect()

async def close_mongo_connection():
    """Close connection wrapper"""
    await db_connector.close()

def get_database():
    """Legacy accessor - prefer injecting MongoDBConnector"""
    return db_connector

