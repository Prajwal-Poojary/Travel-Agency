import asyncio
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/advanced_travel_db")
client = AsyncIOMotorClient(MONGO_URL)
db = client.advanced_travel_db

# Collections
destinations_collection = db.destinations
users_collection = db.users
reviews_collection = db.reviews

# Sample destinations data
sample_destinations = [
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Maldives Paradise Resort",
        "country": "Maldives",
        "city": "Malé",
        "description": "Experience ultimate luxury in overwater bungalows with crystal-clear turquoise waters. Features world-class spa, underwater restaurant, and private beach access.",
        "price_range": "$500 - $1,500 per night",
        "activities": ["Snorkeling", "Scuba Diving", "Spa", "Fine Dining", "Water Sports", "Sunset Cruise"],
        "best_time_to_visit": "November to April",
        "images": [
            "https://images.unsplash.com/photo-1512100356356-de1b84283e18?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1551918120-9739cb430c6d?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1573790387438-4da905039392?w=800&h=600&fit=crop"
        ],
        "coordinates": {"lat": 3.2028, "lng": 73.2207},
        "rating": 4.9,
        "virtual_tour_url": "https://example.com/virtual-tour/maldives",
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Swiss Alps Adventure",
        "country": "Switzerland",
        "city": "Zermatt",
        "description": "Breathtaking mountain views, world-class skiing, and charming alpine villages. Perfect for adventure seekers and nature lovers.",
        "price_range": "$300 - $800 per night",
        "activities": ["Skiing", "Hiking", "Mountain Climbing", "Cable Car", "Photography", "Alpine Dining"],
        "best_time_to_visit": "December to March (Winter), June to September (Summer)",
        "images": [
            "https://images.unsplash.com/photo-1486912500284-6f2462ba07ea?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1528543606781-2f6e6857f318?w=800&h=600&fit=crop"
        ],
        "coordinates": {"lat": 46.0207, "lng": 7.7491},
        "rating": 4.8,
        "virtual_tour_url": "https://example.com/virtual-tour/swiss-alps",
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Tokyo Futuristic Experience",
        "country": "Japan",
        "city": "Tokyo",
        "description": "Immerse yourself in the perfect blend of traditional culture and cutting-edge technology. From ancient temples to neon-lit streets.",
        "price_range": "$150 - $400 per night",
        "activities": ["Temple Visits", "Sushi Making", "Tech Museums", "Shopping", "Nightlife", "Cultural Shows"],
        "best_time_to_visit": "March to May, September to November",
        "images": [
            "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1551986782-d0169b3f8fa7?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1554797589-7241bb691973?w=800&h=600&fit=crop"
        ],
        "coordinates": {"lat": 35.6762, "lng": 139.6503},
        "rating": 4.7,
        "virtual_tour_url": "https://example.com/virtual-tour/tokyo",
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Santorini Sunset Villa",
        "country": "Greece",
        "city": "Santorini",
        "description": "White-washed buildings, blue-domed churches, and the most spectacular sunsets in the world. Perfect romantic getaway.",
        "price_range": "$200 - $600 per night",
        "activities": ["Wine Tasting", "Boat Tours", "Photography", "Beach Relaxation", "Historical Sites", "Fine Dining"],
        "best_time_to_visit": "April to October",
        "images": [
            "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1573790387438-4da905039392?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=800&h=600&fit=crop"
        ],
        "coordinates": {"lat": 36.3932, "lng": 25.4615},
        "rating": 4.8,
        "virtual_tour_url": "https://example.com/virtual-tour/santorini",
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Dubai Luxury Experience",
        "country": "UAE",
        "city": "Dubai",
        "description": "Ultra-modern city with luxury shopping, innovative architecture, and world-class entertainment. Where tradition meets the future.",
        "price_range": "$250 - $1,000 per night",
        "activities": ["Burj Khalifa", "Desert Safari", "Luxury Shopping", "Fine Dining", "Water Parks", "Helicopter Tours"],
        "best_time_to_visit": "November to March",
        "images": [
            "https://images.unsplash.com/photo-1518684079-3c830dcef090?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1523731407965-2430cd12f5e4?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1580302828925-e5ec8de7da63?w=800&h=600&fit=crop"
        ],
        "coordinates": {"lat": 25.2048, "lng": 55.2708},
        "rating": 4.6,
        "virtual_tour_url": "https://example.com/virtual-tour/dubai",
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Bali Spiritual Retreat",
        "country": "Indonesia",
        "city": "Ubud",
        "description": "Tropical paradise with lush rice terraces, ancient temples, and wellness retreats. Perfect for spiritual rejuvenation.",
        "price_range": "$80 - $300 per night",
        "activities": ["Yoga", "Temple Visits", "Rice Terrace Tours", "Spa Treatments", "Cooking Classes", "Art Workshops"],
        "best_time_to_visit": "April to October",
        "images": [
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1573790387438-4da905039392?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=800&h=600&fit=crop"
        ],
        "coordinates": {"lat": -8.5069, "lng": 115.2624},
        "rating": 4.7,
        "virtual_tour_url": "https://example.com/virtual-tour/bali",
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Northern Lights Iceland",
        "country": "Iceland",
        "city": "Reykjavik",
        "description": "Witness the magical Aurora Borealis, explore ice caves, and relax in natural hot springs. An otherworldly experience.",
        "price_range": "$200 - $500 per night",
        "activities": ["Northern Lights", "Ice Caves", "Hot Springs", "Glacier Hiking", "Whale Watching", "Photography"],
        "best_time_to_visit": "September to March (Northern Lights), June to August (Midnight Sun)",
        "images": [
            "https://images.unsplash.com/photo-1473667109755-af9e1224e2f4?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1531391344158-6d4b81c4e0b5?w=800&h=600&fit=crop"
        ],
        "coordinates": {"lat": 64.1466, "lng": -21.9426},
        "rating": 4.9,
        "virtual_tour_url": "https://example.com/virtual-tour/iceland",
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Machu Picchu Adventure",
        "country": "Peru",
        "city": "Cusco",
        "description": "Ancient Incan citadel perched high in the Andes. A UNESCO World Heritage site offering incredible history and breathtaking views.",
        "price_range": "$150 - $400 per night",
        "activities": ["Inca Trail", "Historical Tours", "Mountain Hiking", "Cultural Experiences", "Photography", "Local Cuisine"],
        "best_time_to_visit": "May to September",
        "images": [
            "https://images.unsplash.com/photo-1486912500284-6f2462ba07ea?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=800&h=600&fit=crop"
        ],
        "coordinates": {"lat": -13.1631, "lng": -72.5450},
        "rating": 4.8,
        "virtual_tour_url": "https://example.com/virtual-tour/machu-picchu",
        "created_at": datetime.utcnow()
    }
]

# Sample reviews
sample_reviews = [
    {
        "review_id": str(uuid.uuid4()),
        "user_id": "demo-user-1",
        "username": "TravelLover",
        "rating": 5,
        "comment": "Absolutely stunning destination! The overwater bungalows were perfect and the service was exceptional. Highly recommend for a luxury getaway.",
        "images": [],
        "created_at": datetime.utcnow()
    },
    {
        "review_id": str(uuid.uuid4()),
        "user_id": "demo-user-2",
        "username": "AdventureSeeker",
        "rating": 4,
        "comment": "Amazing mountain views and great skiing conditions. The cable car rides were breathtaking. Perfect for winter sports enthusiasts.",
        "images": [],
        "created_at": datetime.utcnow()
    }
]

async def seed_database():
    try:
        # Clear existing data
        await destinations_collection.delete_many({})
        await reviews_collection.delete_many({})
        
        # Insert sample destinations
        await destinations_collection.insert_many(sample_destinations)
        print(f"Inserted {len(sample_destinations)} destinations")
        
        # Add destination_id to reviews
        destinations = await destinations_collection.find({}).to_list(length=None)
        for i, review in enumerate(sample_reviews):
            if i < len(destinations):
                review["destination_id"] = destinations[i]["destination_id"]
        
        # Insert sample reviews
        await reviews_collection.insert_many(sample_reviews)
        print(f"Inserted {len(sample_reviews)} reviews")
        
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())