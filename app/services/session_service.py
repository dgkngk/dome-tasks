import uuid
import json
from datetime import datetime, timedelta
from typing import Optional
from app.models.session import SessionData
from app.db.redis import redis_interface
from app.core.config import settings
from app.core.logger import dome_logger

class SessionService:
    @staticmethod
    def create(user_id: str, metadata: dict = None) -> str:
        """Create a new session with specified metadata"""
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=settings.SESSION_TTL)
        
        session_data = SessionData(
            user_id=user_id,
            session_id=session_id,
            created_at=now,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        try:
            # Store session in Redis with expiration
            serialized_data = session_data.json()
            redis_interface.setex(
                f"session:{session_id}",
                settings.SESSION_TTL,
                serialized_data
            )
            return session_id
        except Exception as e:
            dome_logger.exception(f"Session creation failed: {e}")
            raise Exception("Session creation failed") from e

    @staticmethod
    def validate(session_id: str) -> bool:
        """Check if session exists and hasn't expired"""
        if not session_id:
            return False
            
        try:
            return redis_interface.exists(f"session:{session_id}")
        except Exception as e:
            dome_logger.exception(f"Session validation error: {e}")
            return False

    @staticmethod
    def refresh(session_id: str):
        """Extend session lifetime"""
        if not session_id:
            return False
            
        try:
            # Get current expiration
            ttl = redis_interface.client.ttl(f"session:{session_id}")
            if ttl > 0:
                # Reset TTL to full value
                redis_interface.client.expire(
                    f"session:{session_id}",
                    settings.SESSION_TTL
                )
                return True
            return False
        except Exception as e:
            dome_logger.exception(f"Session refresh failed: {e}")
            return False

    @staticmethod
    def invalidate(session_id: str):
        """Immediately terminate a session"""
        if not session_id:
            return
            
        try:
            redis_interface.delete(f"session:{session_id}")
        except Exception as e:
            dome_logger.exception(f"Session invalidation failed: {e}")

    @staticmethod
    def get_session_data(session_id: str) -> Optional[SessionData]:
        """Retrieve session data if exists"""
        if not session_id:
            return None
            
        try:
            data = redis_interface.get(f"session:{session_id}")
            if data:
                return SessionData.parse_raw(data)
            return None
        except Exception as e:
            dome_logger.exception(f"Session data retrieval failed: {e}")
            return None
