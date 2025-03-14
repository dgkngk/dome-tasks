# app/tests/test_user_operations.py
from app.services.user_service import UserService
from app.db.database import connect_to_mongo
from app.core.logger import dome_logger
import asyncio


async def user_crud_test():
    await connect_to_mongo()
    user_service = UserService()
    
    # Create a new user
    user_data = {
        "email": "testuser4@example.com",
        "password": "securepassword123",
        "name": "Test User"
    }
    user_id = await user_service.create(user_data)
    dome_logger.info(f"User created with ID: {user_id}")
    
    # Get the created user by ID
    created_user = await user_service.get_by_id(user_id)
    if created_user: 
        dome_logger.info(f"Retrieved user: {created_user}")
    else:
        dome_logger.error("Failed to retrieve created user")
    
    # Update the user's name
    update_data = {
        "name": "Updated Test User"
    }
    updated = await user_service.update(user_id, update_data)
    if updated:
        dome_logger.info(f"User updated: {user_id}")
    else:
        dome_logger.error("Failed to update user")
    
    # Get the updated user by ID
    updated_user = await user_service.get_by_id(user_id)
    if updated_user:
        dome_logger.info(f"Updated user: {updated_user}")
    else:
        dome_logger.error("Failed to retrieve updated user")

    # Get the updated user by mail
    updated_user = await user_service.get_by_email("testuser@example.com")
    if updated_user:
        dome_logger.info(f"Updated user: {updated_user}")
    else:
        dome_logger.error("Failed to retrieve updated user")    
    
    # Delete the user
    deleted = await user_service.delete(user_id)
    if deleted:
        dome_logger.info(f"User deleted: {user_id}")
    else:
        dome_logger.error("Failed to delete user")


if __name__ == "__main__":
    asyncio.run(user_crud_test())
