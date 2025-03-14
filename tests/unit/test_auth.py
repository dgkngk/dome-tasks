from app.core.auth import create_access_token, authenticate_user
from app.services.user_service import UserService
from app.core.logger import dome_logger
from app.core.config import settings
from jose import jwt
from datetime import datetime, timedelta, timezone



def test_create_access_token():
    subject = "test_user"
    token = create_access_token(subject)
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.CRYPT_ALGO])
    assert decoded_token["sub"] == subject
    assert isinstance(decoded_token["exp"], int)

    return "Test passed successfully!"


def test_authenticate():
    user_service = UserService()
    user = user_service.get_by_email("test@example.com")
    if user:
        assert authenticate_user(user.email, user.password) is not None
    else:
        dome_logger.error("User not found for the given email.")


if __name__ == "__main__":
    dome_logger.debug(test_create_access_token())
