from motor.motor_asyncio import AsyncIOMotorClient
from core.config import get_settings

settings = get_settings()

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB]

def get_db():
    return db
