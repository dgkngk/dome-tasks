from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class SessionData(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
