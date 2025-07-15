#!/usr/bin/env python3
"""
Seed script to populate the cloud MongoDB with sample travel data
"""
import asyncio
import os
import uuid
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Database connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/advanced_travel_db")
client = AsyncIOMotorClient(MONGO_URL)
db = client.advanced_travel_db

# Collections
destinations_collection = db.destinations
reviews_collection = db.reviews
packages_collection = db.travel_packages
users_collection = db.users

async def seed_destinations():
    """Seed destinations data"""
    print("🌍 Seeding destinations...")
    
    destinations = [
        {
            "destination_id": str(uuid.uuid4()),
            "name": "Santorini",
            "country": "Greece",
            "city": "Santorini",
            "category": "Beach & Romance",
            "description": "Experience the most beautiful sunsets in the world on this Greek island paradise with its iconic white-washed buildings and azure waters.",
            "price_range": "$200-400/night",
            "activities": ["Sunset watching", "Wine tasting", "Beach relaxation", "Photography", "Sailing"],
            "best_time_to_visit": "April to October",
            "images": [
                "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2069&q=80",
                "https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"
            ],
            "coordinates": {"lat": 36.3932, "lng": 25.4615},
            "rating": 4.8,
            "featured": True,
            "virtual_tour_url": "https://www.youtube.com/watch?v=santorini-360",
            "created_at": datetime.utcnow()
        },
        {
            "destination_id": str(uuid.uuid4()),
            "name": "Maldives",
            "country": "Maldives",
            "city": "Malé",
            "category": "Luxury Beach Resort",
            "description": "Pristine white sand beaches, crystal clear turquoise waters, and overwater bungalows create the ultimate tropical paradise.",
            "price_range": "$500-2000/night",
            "activities": ["Snorkeling", "Diving", "Spa treatments", "Water sports", "Romantic dinners"],
            "best_time_to_visit": "November to April",
            "images": [
                "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
                "https://images.unsplash.com/photo-1439066615861-d1af74d74000?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"
            ],
            "coordinates": {"lat": 3.2028, "lng": 73.2207},
            "rating": 4.9,
            "featured": True,
            "virtual_tour_url": "https://www.youtube.com/watch?v=maldives-360",
            "created_at": datetime.utcnow()
        },
        {
            "destination_id": str(uuid.uuid4()),
            "name": "Tokyo",
            "country": "Japan",
            "city": "Tokyo",
            "category": "Culture & City",
            "description": "A fascinating blend of ancient traditions and cutting-edge technology, Tokyo offers endless adventures from temples to skyscrapers.",
            "price_range": "$100-300/night",
            "activities": ["Temple visits", "Sushi experiences", "Shopping", "Nightlife", "Cherry blossom viewing"],
            "best_time_to_visit": "March to May, September to November",
            "images": [
                "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2088&q=80",
                "https://images.unsplash.com/photo-1513407030348-c983a97b98d8?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"
            ],
            "coordinates": {"lat": 35.6762, "lng": 139.6503},
            "rating": 4.7,
            "featured": True,
            "virtual_tour_url": "https://www.youtube.com/watch?v=tokyo-360",
            "created_at": datetime.utcnow()
        },
        {
            "destination_id": str(uuid.uuid4()),
            "name": "Swiss Alps",
            "country": "Switzerland",
            "city": "Interlaken",
            "category": "Mountain Adventure",
            "description": "Breathtaking mountain landscapes, pristine lakes, and world-class skiing make the Swiss Alps an outdoor enthusiast's paradise.",
            "price_range": "$300-600/night",
            "activities": ["Skiing", "Hiking", "Mountain climbing", "Scenic train rides", "Photography"],
            "best_time_to_visit": "December to March, June to September",
            "images": [
                "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
                "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"
            ],
            "coordinates": {"lat": 46.6863, "lng": 7.8632},
            "rating": 4.6,
            "featured": True,
            "virtual_tour_url": "https://www.youtube.com/watch?v=swiss-alps-360",
            "created_at": datetime.utcnow()
        },
        {
            "destination_id": str(uuid.uuid4()),
            "name": "Dubai",
            "country": "UAE",
            "city": "Dubai",
            "category": "Luxury & Shopping",
            "description": "A modern metropolis where luxury meets innovation, featuring the world's tallest building, artificial islands, and incredible shopping.",
            "price_range": "$200-800/night",
            "activities": ["Luxury shopping", "Desert safari", "Burj Khalifa visit", "Fine dining", "Water parks"],
            "best_time_to_visit": "October to March",
            "images": [
                "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
                "https://images.unsplash.com/photo-1518684079-3c830dcef090?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"
            ],
            "coordinates": {"lat": 25.2048, "lng": 55.2708},
            "rating": 4.5,
            "featured": True,
            "virtual_tour_url": "https://www.youtube.com/watch?v=dubai-360",
            "created_at": datetime.utcnow()
        },
        {
            "destination_id": str(uuid.uuid4()),
            "name": "Bali",
            "country": "Indonesia",
            "city": "Ubud",
            "category": "Culture & Nature",
            "description": "A tropical paradise combining beautiful beaches, ancient temples, lush rice terraces, and rich cultural traditions.",
            "price_range": "$50-200/night",
            "activities": ["Temple visits", "Rice terrace tours", "Yoga retreats", "Surfing", "Balinese cooking classes"],
            "best_time_to_visit": "April to October",
            "images": [
                "https://images.unsplash.com/photo-1537953773345-d172ccf13cf1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
                "https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"
            ],
            "coordinates": {"lat": -8.5069, "lng": 115.2625},
            "rating": 4.7,
            "featured": True,
            "virtual_tour_url": "https://www.youtube.com/watch?v=bali-360",
            "created_at": datetime.utcnow()
        },
        {
            "destination_id": str(uuid.uuid4()),
            "name": "Iceland",
            "country": "Iceland",
            "city": "Reykjavik",
            "category": "Adventure & Nature",
            "description": "Land of fire and ice with stunning glaciers, geysers, northern lights, and dramatic volcanic landscapes.",
            "price_range": "$250-500/night",
            "activities": ["Northern lights viewing", "Glacier hiking", "Hot springs", "Whale watching", "Photography"],
            "best_time_to_visit": "September to March (Northern Lights), June to August (Hiking)",
            "images": [
                "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
                "https://images.unsplash.com/photo-1551524164-687a55dd1126?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"
            ],
            "coordinates": {"lat": 64.1466, "lng": -21.9426},
            "rating": 4.8,
            "featured": True,
            "virtual_tour_url": "https://www.youtube.com/watch?v=iceland-360",
            "created_at": datetime.utcnow()
        },
        {
            "destination_id": str(uuid.uuid4()),
            "name": "Machu Picchu",
            "country": "Peru",
            "city": "Cusco",
            "category": "Historical & Adventure",
            "description": "The ancient Incan citadel perched high in the Andes Mountains, one of the most iconic archaeological sites in the world.",
            "price_range": "$100-300/night",
            "activities": ["Inca Trail hiking", "Historical exploration", "Mountain climbing", "Photography", "Cultural tours"],
            "best_time_to_visit": "May to September",
            "images": [
                "https://images.unsplash.com/photo-1587595431973-160d0d94add1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2076&q=80",
                "https://images.unsplash.com/photo-1526392060635-9d6019884377?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"
            ],
            "coordinates": {"lat": -13.1631, "lng": -72.5450},
            "rating": 4.9,
            "featured": True,
            "virtual_tour_url": "https://www.youtube.com/watch?v=machu-picchu-360",
            "created_at": datetime.utcnow()
        },
        {
            "destination_id": str(uuid.uuid4()),
            "name": "Paris",
            "country": "France",
            "city": "Paris",
            "category": "Culture & Romance",
            "description": "The City of Light with iconic landmarks, world-class museums, charming cafes, and romantic atmosphere.",
            "price_range": "$150-400/night",
            "activities": ["Museum visits", "Café culture", "River cruises", "Shopping", "Fine dining"],
            "best_time_to_visit": "April to June, September to November",
            "images": [
                "https://images.unsplash.com/photo-1502602898536-47ad22581b52?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2073&q=80",
                "https://images.unsplash.com/photo-1549144511-f099e773c147?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"
            ],
            "coordinates": {"lat": 48.8566, "lng": 2.3522},
            "rating": 4.6,
            "featured": False,
            "virtual_tour_url": "https://www.youtube.com/watch?v=paris-360",
            "created_at": datetime.utcnow()
        },
        {
            "destination_id": str(uuid.uuid4()),
            "name": "New York City",
            "country": "USA",
            "city": "New York",
            "category": "City & Culture",
            "description": "The Big Apple with iconic skyscrapers, world-class Broadway shows, diverse neighborhoods, and vibrant energy.",
            "price_range": "$200-600/night",
            "activities": ["Broadway shows", "Museum visits", "Central Park", "Shopping", "Fine dining"],
            "best_time_to_visit": "April to June, September to November",
            "images": [
                "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
                "https://images.unsplash.com/photo-1522083165195-3424ed129620?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"
            ],
            "coordinates": {"lat": 40.7128, "lng": -74.0060},
            "rating": 4.4,
            "featured": False,
            "virtual_tour_url": "https://www.youtube.com/watch?v=nyc-360",
            "created_at": datetime.utcnow()
        },
        {
            "destination_id": str(uuid.uuid4()),
            "name": "Great Wall of China",
            "country": "China",
            "city": "Beijing",
            "category": "Historical & Adventure",
            "description": "One of the world's greatest wonders, this ancient fortification stretches across northern China with stunning mountain views.",
            "price_range": "$80-200/night",
            "activities": ["Wall hiking", "Historical tours", "Photography", "Cultural experiences", "Museum visits"],
            "best_time_to_visit": "March to May, September to November",
            "images": [
                "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
                "https://images.unsplash.com/photo-1547036967-23d11aacaee0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"
            ],
            "coordinates": {"lat": 40.4319, "lng": 116.5704},
            "rating": 4.7,
            "featured": False,
            "virtual_tour_url": "https://www.youtube.com/watch?v=great-wall-360",
            "created_at": datetime.utcnow()
        },
        {
            "destination_id": str(uuid.uuid4()),
            "name": "Amazon Rainforest",
            "country": "Brazil",
            "city": "Manaus",
            "category": "Nature & Adventure",
            "description": "The world's largest tropical rainforest with incredible biodiversity, indigenous cultures, and unparalleled natural beauty.",
            "price_range": "$100-300/night",
            "activities": ["Wildlife spotting", "Jungle trekking", "River cruises", "Indigenous culture tours", "Photography"],
            "best_time_to_visit": "June to November",
            "images": [
                "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
                "https://images.unsplash.com/photo-1504052434569-70ad5836ab65?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"
            ],
            "coordinates": {"lat": -3.4653, "lng": -62.2159},
            "rating": 4.8,
            "featured": False,
            "virtual_tour_url": "https://www.youtube.com/watch?v=amazon-360",
            "created_at": datetime.utcnow()
        }
    ]
    
    # Clear existing destinations
    await destinations_collection.delete_many({})
    
    # Insert new destinations
    result = await destinations_collection.insert_many(destinations)
    print(f"✅ Inserted {len(result.inserted_ids)} destinations")
    
    return destinations

async def seed_reviews():
    """Seed reviews data"""
    print("⭐ Seeding reviews...")
    
    # Get some destinations to create reviews for
    destinations = await destinations_collection.find().limit(8).to_list(length=8)
    
    if not destinations:
        print("❌ No destinations found to create reviews for")
        return
    
    reviews = []
    for dest in destinations:
        # Create 2-3 reviews per destination
        for i in range(2):
            review = {
                "review_id": str(uuid.uuid4()),
                "destination_id": dest["destination_id"],
                "user_id": str(uuid.uuid4()),
                "username": f"traveler_{i+1}",
                "rating": 4 + (i * 0.5),  # Ratings between 4-5
                "comment": f"Amazing experience at {dest['name']}! The {dest['activities'][0].lower()} was incredible. Highly recommend this destination for anyone looking for {dest['category'].lower()}.",
                "images": [],
                "categories": {
                    "location": 5,
                    "service": 4,
                    "value": 4,
                    "cleanliness": 5
                },
                "verified_stay": True,
                "helpful_count": i + 1,
                "created_at": datetime.utcnow() - timedelta(days=i*10)
            }
            reviews.append(review)
    
    # Clear existing reviews
    await reviews_collection.delete_many({})
    
    # Insert new reviews
    result = await reviews_collection.insert_many(reviews)
    print(f"✅ Inserted {len(result.inserted_ids)} reviews")

async def seed_packages():
    """Seed travel packages data"""
    print("📦 Seeding travel packages...")
    
    packages = [
        {
            "package_id": str(uuid.uuid4()),
            "name": "Greek Islands Paradise",
            "description": "7-day island hopping adventure through Santorini, Mykonos, and Crete",
            "destinations": ["Santorini", "Mykonos", "Crete"],
            "duration": "7 days",
            "price": 2499.99,
            "original_price": 3299.99,
            "savings": 800.00,
            "includes": ["Flights", "Hotels", "Ferry transfers", "Breakfast", "Guided tours"],
            "image": "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2069&q=80",
            "featured": True,
            "available": True,
            "max_group_size": 8,
            "difficulty": "Easy",
            "created_at": datetime.utcnow()
        },
        {
            "package_id": str(uuid.uuid4()),
            "name": "Japan Cultural Journey",
            "description": "10-day cultural immersion through Tokyo, Kyoto, and Osaka",
            "destinations": ["Tokyo", "Kyoto", "Osaka"],
            "duration": "10 days",
            "price": 3599.99,
            "original_price": 4199.99,
            "savings": 600.00,
            "includes": ["Flights", "Hotels", "JR Pass", "Meals", "Cultural experiences"],
            "image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2088&q=80",
            "featured": True,
            "available": True,
            "max_group_size": 6,
            "difficulty": "Moderate",
            "created_at": datetime.utcnow()
        },
        {
            "package_id": str(uuid.uuid4()),
            "name": "Maldives Luxury Retreat",
            "description": "5-day luxury overwater villa experience with spa treatments",
            "destinations": ["Maldives"],
            "duration": "5 days",
            "price": 4999.99,
            "original_price": 6499.99,
            "savings": 1500.00,
            "includes": ["Flights", "Overwater villa", "All meals", "Spa treatments", "Water activities"],
            "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
            "featured": True,
            "available": True,
            "max_group_size": 2,
            "difficulty": "Easy",
            "created_at": datetime.utcnow()
        }
    ]
    
    # Clear existing packages
    await packages_collection.delete_many({})
    
    # Insert new packages
    result = await packages_collection.insert_many(packages)
    print(f"✅ Inserted {len(result.inserted_ids)} travel packages")

async def seed_sample_user():
    """Seed a sample user for testing"""
    print("👤 Seeding sample user...")
    
    # Password hash for "password123"
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    sample_user = {
        "user_id": str(uuid.uuid4()),
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "hashed_password": pwd_context.hash("password123"),
        "created_at": datetime.utcnow(),
        "preferences": {
            "favorite_categories": ["Beach & Romance", "Adventure & Nature"],
            "budget_range": "200-500",
            "travel_style": "Luxury"
        },
        "avatar": None
    }
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": sample_user["email"]})
    if existing_user:
        print("✅ Sample user already exists")
        return
    
    # Insert sample user
    result = await users_collection.insert_one(sample_user)
    print(f"✅ Inserted sample user: {sample_user['email']}")

async def main():
    """Main seeding function"""
    print("🚀 Starting database seeding...")
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
        # Seed all data
        await seed_destinations()
        await seed_reviews()
        await seed_packages()
        await seed_sample_user()
        
        print("\n🎉 Database seeding completed successfully!")
        print("\nTest credentials:")
        print("Email: test@example.com")
        print("Password: password123")
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        raise
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())