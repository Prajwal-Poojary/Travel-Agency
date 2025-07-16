#!/usr/bin/env python3
"""
Seed script to populate the database with sample travel data
"""
import asyncio
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample destinations data
SAMPLE_DESTINATIONS = [
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Maldives Paradise Resort",
        "country": "Maldives",
        "city": "Malé",
        "category": "Luxury Beach Resort",
        "description": "Experience ultimate luxury in overwater bungalows with crystal-clear turquoise waters. Features world-class spa, underwater restaurant, and private beach access.",
        "price_range": "$500 - $1,500 per night",
        "activities": ["Snorkeling", "Scuba Diving", "Spa", "Fine Dining", "Water Sports", "Sunset Cruise"],
        "best_time_to_visit": "November to April",
        "images": [
            "https://images.unsplash.com/photo-1512100356356-de1b84283e18?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwzfHxsdXh1cnklMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NTk3fDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1551918120-9739cb430c6d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwyfHxsdXh1cnklMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NTk3fDA&ixlib=rb-4.1.0&q=85"
        ],
        "coordinates": {"lat": 3.2028, "lng": 73.2207},
        "rating": 4.9,
        "featured": True,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Swiss Alps Adventure",
        "country": "Switzerland",
        "city": "Zermatt",
        "category": "Mountain Adventure",
        "description": "Breathtaking mountain views, world-class skiing, and charming alpine villages. Perfect for adventure seekers and nature lovers.",
        "price_range": "$300 - $800 per night",
        "activities": ["Skiing", "Hiking", "Mountain Climbing", "Cable Car", "Photography", "Alpine Dining"],
        "best_time_to_visit": "December to March (Winter), June to September (Summer)",
        "images": [
            "https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwyfHxtb3VudGFpbiUyMHJlc29ydHxlbnwwfHx8fDE3NTIzNDQ2NTB8MA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwzfHxtb3VudGFpbiUyMHJlc29ydHxlbnwwfHx8fDE3NTIzNDQ2NTB8MA&ixlib=rb-4.1.0&q=85"
        ],
        "coordinates": {"lat": 46.0207, "lng": 7.7491},
        "rating": 4.8,
        "featured": True,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Tokyo Futuristic Experience",
        "country": "Japan",
        "city": "Tokyo",
        "category": "City & Culture",
        "description": "Immerse yourself in the perfect blend of traditional culture and cutting-edge technology. From ancient temples to neon-lit streets.",
        "price_range": "$150 - $400 per night",
        "activities": ["Temple Visits", "Sushi Making", "Tech Museums", "Shopping", "Nightlife", "Cultural Shows"],
        "best_time_to_visit": "March to May, September to November",
        "images": [
            "https://images.unsplash.com/photo-1493134799591-2c9eed26201a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxjaXR5JTIwc2t5bGluZXxlbnwwfHx8fDE3NTIzNDQ2NTV8MA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1541423408854-5df732b6f6d1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxjaXR5JTIwc2t5bGluZXxlbnwwfHx8fDE3NTIzNDQ2NTV8MA&ixlib=rb-4.1.0&q=85"
        ],
        "coordinates": {"lat": 35.6762, "lng": 139.6503},
        "rating": 4.7,
        "featured": True,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Santorini Sunset Villa",
        "country": "Greece",
        "city": "Santorini",
        "category": "Romance & Culture",
        "description": "White-washed buildings, blue-domed churches, and the most spectacular sunsets in the world. Perfect romantic getaway.",
        "price_range": "$200 - $600 per night",
        "activities": ["Wine Tasting", "Boat Tours", "Photography", "Beach Relaxation", "Historical Sites", "Fine Dining"],
        "best_time_to_visit": "April to October",
        "images": [
            "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1573790387438-4da905039392?w=800&h=600&fit=crop"
        ],
        "coordinates": {"lat": 36.3932, "lng": 25.4615},
        "rating": 4.8,
        "featured": True,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Dubai Luxury Experience",
        "country": "UAE",
        "city": "Dubai",
        "category": "Luxury & Shopping",
        "description": "Ultra-modern city with luxury shopping, innovative architecture, and world-class entertainment. Where tradition meets the future.",
        "price_range": "$250 - $1,000 per night",
        "activities": ["Burj Khalifa", "Desert Safari", "Luxury Shopping", "Fine Dining", "Water Parks", "Helicopter Tours"],
        "best_time_to_visit": "November to March",
        "images": [
            "https://images.unsplash.com/photo-1541423408854-5df732b6f6d1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxjaXR5JTIwc2t5bGluZXxlbnwwfHx8fDE3NTIzNDQ2NTV8MA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1493134799591-2c9eed26201a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxjaXR5JTIwc2t5bGluZXxlbnwwfHx8fDE3NTIzNDQ2NTV8MA&ixlib=rb-4.1.0&q=85"
        ],
        "coordinates": {"lat": 25.2048, "lng": 55.2708},
        "rating": 4.6,
        "featured": True,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Bali Spiritual Retreat",
        "country": "Indonesia",
        "city": "Ubud",
        "category": "Culture & Nature",
        "description": "Tropical paradise with lush rice terraces, ancient temples, and wellness retreats. Perfect for spiritual rejuvenation and cultural immersion.",
        "price_range": "$80 - $300 per night",
        "activities": ["Yoga", "Temple Visits", "Rice Terrace Tours", "Spa Treatments", "Cooking Classes", "Art Workshops"],
        "best_time_to_visit": "April to October",
        "images": [
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1573790387438-4da905039392?w=800&h=600&fit=crop"
        ],
        "coordinates": {"lat": -8.5069, "lng": 115.2624},
        "rating": 4.7,
        "featured": False,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Northern Lights Iceland",
        "country": "Iceland",
        "city": "Reykjavik",
        "category": "Adventure & Nature",
        "description": "Witness the magical Aurora Borealis, explore ice caves, and relax in natural hot springs. An otherworldly experience.",
        "price_range": "$200 - $500 per night",
        "activities": ["Northern Lights", "Ice Caves", "Hot Springs", "Glacier Hiking", "Whale Watching", "Photography"],
        "best_time_to_visit": "September to March (Northern Lights), June to August (Midnight Sun)",
        "images": [
            "https://images.unsplash.com/photo-1473667109755-af9e1224e2f4?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop"
        ],
        "coordinates": {"lat": 64.1466, "lng": -21.9426},
        "rating": 4.9,
        "featured": False,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Machu Picchu Adventure",
        "country": "Peru",
        "city": "Cusco",
        "category": "Historical & Adventure",
        "description": "Ancient Incan citadel perched high in the Andes Mountains, one of the most iconic archaeological sites in the world.",
        "price_range": "$150 - $400 per night",
        "activities": ["Inca Trail", "Historical Tours", "Mountain Hiking", "Cultural Experiences", "Photography", "Local Cuisine"],
        "best_time_to_visit": "May to September",
        "images": [
            "https://images.unsplash.com/photo-1528543606781-2f6e6857f318?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwxfHxhZHZlbnR1cmUlMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NjYxfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1707584145698-7a0b425a79e1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwyfHxhZHZlbnR1cmUlMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NjYxfDA&ixlib=rb-4.1.0&q=85"
        ],
        "coordinates": {"lat": -13.1631, "lng": -72.5450},
        "rating": 4.8,
        "featured": True,
        "created_at": datetime.utcnow()
    }
]

# Sample reviews data
SAMPLE_REVIEWS = [
    {
        "review_id": str(uuid.uuid4()),
        "user_id": "demo-user-1",
        "username": "TravelLover",
        "rating": 5,
        "comment": "Absolutely stunning destination! The overwater bungalows were perfect and the service was exceptional. The underwater restaurant was a unique experience I'll never forget.",
        "images": [],
        "helpful_count": 24,
        "categories": {"Service": 5, "Value": 4, "Location": 5, "Cleanliness": 5},
        "verified_stay": True,
        "created_at": datetime.utcnow()
    },
    {
        "review_id": str(uuid.uuid4()),
        "user_id": "demo-user-2",
        "username": "AdventureSeeker",
        "rating": 4,
        "comment": "Amazing mountain views and great skiing conditions. The cable car rides were breathtaking. Staff was friendly and the food was excellent.",
        "images": [],
        "helpful_count": 18,
        "categories": {"Service": 4, "Value": 4, "Location": 5, "Cleanliness": 4},
        "verified_stay": True,
        "created_at": datetime.utcnow()
    }
]

async def seed_database():
    """Seed the database with sample data"""
    try:
        # Connect to database
        client = AsyncIOMotorClient(settings.mongo_url)
        db = client[settings.database_name]
        
        # Test connection
        await client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Clear existing data
        await db.destinations.delete_many({})
        await db.reviews.delete_many({})
        logger.info("Cleared existing data")
        
        # Insert destinations
        await db.destinations.insert_many(SAMPLE_DESTINATIONS)
        logger.info(f"Inserted {len(SAMPLE_DESTINATIONS)} destinations")
        
        # Add destination_id to reviews
        destinations = await db.destinations.find({}).to_list(length=None)
        for i, review in enumerate(SAMPLE_REVIEWS):
            if i < len(destinations):
                review["destination_id"] = destinations[i]["destination_id"]
        
        # Insert reviews
        await db.reviews.insert_many(SAMPLE_REVIEWS)
        logger.info(f"Inserted {len(SAMPLE_REVIEWS)} reviews")
        
        logger.info("Database seeded successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())