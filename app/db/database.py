from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.logger import dome_logger

# MongoDB client
mongo_client = None
db = None

async def connect_to_mongo():
    global mongo_client, db
    mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
    db = mongo_client[settings.MONGO_DB]
    dome_logger.info("Connected to MongoDB!")

async def close_mongo_connection():
    global mongo_client
    global db
    if mongo_client is not None:
        mongo_client.close()
        db = None
        dome_logger.info("Disconnected from MongoDB!")

def get_database():
    return db