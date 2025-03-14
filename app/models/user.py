from pydantic import BaseModel, EmailStr, Field
from pydantic_core import SchemaValidator
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        
    @classmethod
    def validate(cls, v, i):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
        
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return SchemaValidator(
            {
                "type": "string",
                "pattern": r"^[0-9a-fA-F]{24}$"
            },
            validation_mode='strict'
        ).json_schema

class UserModel(BaseModel):
    id: PyObjectId = Field(alias="_id", default_factory=PyObjectId)
    email: EmailStr
    password_hash: str
    name: str
    photo_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc).isoformat)
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc).isoformat)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password_hash": "hashed_password",
                "name": "John Doe",
                "photo_url": "https://example.com/photo.jpg",
            }
        }


class UserCreate(BaseModel):
    email: EmailStr
    password_hash: str
    name: str
    photo_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
