from app.db.database import get_database, connect_to_mongo, close_mongo_connection, mongo_client
from app.core.logger import dome_logger

import asyncio

async def test_connect_and_close():
    await connect_to_mongo()
    assert get_database() is not None
    await close_mongo_connection()
    assert get_database() is None
    dome_logger.info("MongoDB connection test passed!")


async def test_insert():
    await connect_to_mongo()
    db = get_database()
    collection = db["test"]
    result = await collection.insert_one({"name": "John Doe"})
    assert result.inserted_id is not None
    dome_logger.info("Insert test passed!")

if __name__ == "__main__":
    asyncio.run(test_insert())