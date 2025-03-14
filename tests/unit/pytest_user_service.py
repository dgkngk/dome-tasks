import pytest
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.models.user import UserCreate, UserModel
from app.core.config import settings
from app.db.database import connect_to_mongo, get_database, close_mongo_connection

# Fixture to initialize MongoDB connection and clean up after tests

@pytest.fixture(scope="session")
async def mongo_test_client():
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Yield the database for testing
    yield get_database()
    
    # Close the MongoDB connection after tests are done
    await close_mongo_connection()

# Example test function using the fixture
@pytest.mark.asyncio
async def test_user_creation(mongo_test_client):
    user_collection = mongo_test_client["users"]
    user_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password_hash": "hashed_password"
    }
    
    # Create a new user
    user_id = await user_collection.insert_one(user_data).inserted_id
    
    # Retrieve the user to verify it was created
    user = await user_collection.find_one({"_id": user_id})
    assert user is not None

# # Test cases for UserService CRUD operations
# class TestUserService:
#     @pytest.mark.asyncio
#     async def test_create_user(self, mongo_test_client):
#         user_service = UserService()
#         user_data = {
#             "email": "test@example.com",
#             "password": "securepassword123",
#             "name": "Test User"
#         }
        
#         user_id = await user_service.create(user_data)
#         assert isinstance(user_id, str)
        
#         # Verify the user is created in the database
#         user_document = await user_service.find_by_id(user_id)
#         assert user_document is not None
#         assert user_document["email"] == "test@example.com"
#         assert user_document["name"] == "Test User"

#     @pytest.mark.asyncio
#     async def test_get_user_by_id(self, mongo_test_client):
#         user_service = UserService()
#         user_data = {
#             "email": "getuser@example.com",
#             "password": "securepassword123",
#             "name": "Get User"
#         }
        
#         # Create a user first
#         user_id = await user_service.create(user_data)
        
#         # Retrieve the user by ID
#         retrieved_user = await user_service.get_by_id(user_id)
#         assert retrieved_user is not None
#         assert retrieved_user["email"] == "getuser@example.com"
#         assert retrieved_user["name"] == "Get User"

#     @pytest.mark.asyncio
#     async def test_update_user(self, mongo_test_client):
#         user_service = UserService()
#         user_data = {
#             "email": "updateuser@example.com",
#             "password": "securepassword123",
#             "name": "Update User"
#         }
        
#         # Create a user first
#         user_id = await user_service.create(user_data)
        
#         # Update the user's name
#         update_data = {"name": "Updated User"}
#         updated_result = await user_service.update(user_id, update_data)
#         assert updated_result is True
        
#         # Verify the user is updated in the database
#         updated_user_document = await user_service.find_by_id(user_id)
#         assert updated_user_document["name"] == "Updated User"

#     @pytest.mark.asyncio
#     async def test_delete_user(self, mongo_test_client):
#         user_service = UserService()
#         user_data = {
#             "email": "deleteuser@example.com",
#             "password": "securepassword123",
#             "name": "Delete User"
#         }
        
#         # Create a user first
#         user_id = await user_service.create(user_data)
        
#         # Delete the user
#         delete_result = await user_service.delete(user_id)
#         assert delete_result is True
        
#         # Verify the user is deleted from the database
#         deleted_user_document = await user_service.find_by_id(user_id)
#         assert deleted_user_document is None

# # This test file includes tests for creating, retrieving, updating, and deleting users using the UserService.