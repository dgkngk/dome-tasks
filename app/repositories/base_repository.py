from typing import Type, TypeVar, Generic, List, Optional, Dict, Any
from pydantic import BaseModel
from bson import ObjectId
from app.db.database import db_connector
from app.core.logger import dome_logger

DocumentType = TypeVar('DocumentType', bound=BaseModel)

class BaseRepository(Generic[DocumentType]):
    def __init__(self, document_type: Type[DocumentType], collection_name: str):
        if not db_connector.db:
            raise RuntimeError("Database not connected. Call connect_to_mongo() first")
            
        self.document_type = document_type
        self.collection_name = collection_name

    async def create(self, entity: DocumentType) -> str:
        document = entity.model_dump()
        return await db_connector.create(self.collection_name, document)

    async def find_by_id(self, entity_id: str) -> Optional[DocumentType]:
        document = await db_connector.find(self.collection_name, entity_id)
        return self._validate_document(document) if document else None

    async def find_all(self, filters: Optional[Dict[str, Any]] = None) -> List[DocumentType]:
        documents = await db_connector.find_all(self.collection_name, filters)
        return [self._validate_document(doc) for doc in documents]

    async def find_by_criteria(self, criteria: Dict[str, Any]) -> List[DocumentType]:
        documents = await db_connector.find_all(self.collection_name, criteria)
        return [self._validate_document(doc) for doc in documents]

    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> bool:
        return await db_connector.update(self.collection_name, entity_id, update_data)

    async def delete(self, entity_id: str) -> bool:
        return await db_connector.delete(self.collection_name, entity_id)

    def _validate_document(self, document: Dict[str, Any]) -> DocumentType:
        try:
            return self.document_type(**document)
        except Exception as e:
            dome_logger.error(f"Document validation failed for {self.collection_name}: {str(e)}")
            raise ValueError(f"Invalid document structure for {self.document_type.__name__}") from e

    def _apply_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        if not filters:
            return {}
            
        # Convert string IDs to ObjectId for MongoDB queries
        if '_id' in filters:
            filters['_id'] = ObjectId(filters['_id'])
            
        # Remove None values from filters
        return {k: v for k, v in filters.items() if v is not None}
