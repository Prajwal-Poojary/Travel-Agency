import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging
from config import settings

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

database = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        database.client = AsyncIOMotorClient(settings.mongo_url)
        database.database = database.client[settings.database_name]
        
        # Test the connection
        await database.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        logger.info("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Users collection indexes
        await database.database.users.create_index("email", unique=True)
        await database.database.users.create_index("username", unique=True)
        
        # Destinations collection indexes
        await database.database.destinations.create_index("destination_id", unique=True)
        await database.database.destinations.create_index("country")
        await database.database.destinations.create_index("city")
        await database.database.destinations.create_index("name")
        
        # Reviews collection indexes
        await database.database.reviews.create_index("destination_id")
        await database.database.reviews.create_index("user_id")
        
        # Bookings collection indexes
        await database.database.bookings.create_index("user_id")
        await database.database.bookings.create_index("destination_id")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def get_database():
    return database.database