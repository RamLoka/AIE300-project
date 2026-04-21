import os
from motor.motor_asyncio import AsyncIOMotorClient

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017/itemsdb")

client = AsyncIOMotorClient(DATABASE_URL)
db = client.get_default_database()

collection = db["items"]