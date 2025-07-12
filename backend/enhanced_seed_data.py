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
packages_collection = db.travel_packages

# Enhanced destinations with categorization
enhanced_destinations = [
    # TROPICAL DESTINATIONS
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Maldives Paradise Resort",
        "country": "Maldives",
        "city": "Malé",
        "category": "Tropical",
        "description": "Experience ultimate luxury in overwater bungalows with crystal-clear turquoise waters. Features world-class spa, underwater restaurant, and private beach access.",
        "price_range": "$500 - $1,500 per night",
        "activities": ["Snorkeling", "Scuba Diving", "Spa", "Fine Dining", "Water Sports", "Sunset Cruise"],
        "best_time_to_visit": "November to April",
        "images": [
            "https://images.unsplash.com/photo-1512100356356-de1b84283e18?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwzfHxsdXh1cnklMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NTk3fDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1551918120-9739cb430c6d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwyfHxsdXh1cnklMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NTk3fDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1544945582-052b29cd29e4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwyfHx0cm9waWNhbCUyMHBhcmFkaXNlfGVufDB8fHx8MTc1MjM0NDYwNnww&ixlib=rb-4.1.0&q=85"
        ],
        "coordinates": {"lat": 3.2028, "lng": 73.2207},
        "rating": 4.9,
        "reviews_count": 284,
        "virtual_tour_url": "https://example.com/virtual-tour/maldives",
        "featured": True,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Bali Spiritual Retreat",
        "country": "Indonesia",
        "city": "Ubud",
        "category": "Tropical",
        "description": "Tropical paradise with lush rice terraces, ancient temples, and wellness retreats. Perfect for spiritual rejuvenation and cultural immersion.",
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
        "reviews_count": 192,
        "virtual_tour_url": "https://example.com/virtual-tour/bali",
        "featured": False,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Seychelles Luxury Resort",
        "country": "Seychelles",
        "city": "Victoria",
        "category": "Tropical",
        "description": "Pristine beaches with granite boulders, rare wildlife, and exclusive resorts. An untouched paradise for discerning travelers.",
        "price_range": "$400 - $1,200 per night",
        "activities": ["Beach Relaxation", "Snorkeling", "Nature Walks", "Bird Watching", "Sailing", "Spa"],
        "best_time_to_visit": "April to May, October to November",
        "images": [
            "https://images.unsplash.com/photo-1544945582-052b29cd29e4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwyfHx0cm9waWNhbCUyMHBhcmFkaXNlfGVufDB8fHx8MTc1MjM0NDYwNnww&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1551918120-9739cb430c6d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwyfHxsdXh1cnklMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NTk3fDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1512100356356-de1b84283e18?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwzfHxsdXh1cnklMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NTk3fDA&ixlib=rb-4.1.0&q=85"
        ],
        "coordinates": {"lat": -4.6796, "lng": 55.4920},
        "rating": 4.8,
        "reviews_count": 156,
        "virtual_tour_url": "https://example.com/virtual-tour/seychelles",
        "featured": False,
        "created_at": datetime.utcnow()
    },

    # MOUNTAIN DESTINATIONS  
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Swiss Alps Adventure",
        "country": "Switzerland",
        "city": "Zermatt",
        "category": "Mountain",
        "description": "Breathtaking mountain views, world-class skiing, and charming alpine villages. Perfect for adventure seekers and nature lovers.",
        "price_range": "$300 - $800 per night",
        "activities": ["Skiing", "Hiking", "Mountain Climbing", "Cable Car", "Photography", "Alpine Dining"],
        "best_time_to_visit": "December to March (Winter), June to September (Summer)",
        "images": [
            "https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwyfHxtb3VudGFpbiUyMHJlc29ydHxlbnwwfHx8fDE3NTIzNDQ2NTB8MA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwzfHxtb3VudGFpbiUyMHJlc29ydHxlbnwwfHx8fDE3NTIzNDQ2NTB8MA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1528543606781-2f6e6857f318?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwxfHxhZHZlbnR1cmUlMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NjYxfDA&ixlib=rb-4.1.0&q=85"
        ],
        "coordinates": {"lat": 46.0207, "lng": 7.7491},
        "rating": 4.8,
        "reviews_count": 367,
        "virtual_tour_url": "https://example.com/virtual-tour/swiss-alps",
        "featured": True,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Aspen Luxury Lodge",
        "country": "USA",
        "city": "Aspen",
        "category": "Mountain",
        "description": "World-renowned ski resort with luxury accommodations, gourmet dining, and exclusive mountain experiences in the Colorado Rockies.",
        "price_range": "$400 - $1,000 per night",
        "activities": ["Skiing", "Snowboarding", "Mountain Biking", "Hiking", "Luxury Shopping", "Fine Dining"],
        "best_time_to_visit": "December to April (Winter), June to September (Summer)",
        "images": [
            "https://images.unsplash.com/photo-1706794543262-a013701e070c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwxfHxtb3VudGFpbiUyMHJlc29ydHxlbnwwfHx8fDE3NTIzNDQ2NTB8MA&ixlib=rb-4.1.0&q=85",
            "https://images.pexels.com/photos/32948745/pexels-photo-32948745.jpeg",
            "https://images.pexels.com/photos/32935515/pexels-photo-32935515.jpeg"
        ],
        "coordinates": {"lat": 39.1911, "lng": -106.8175},
        "rating": 4.7,
        "reviews_count": 243,
        "virtual_tour_url": "https://example.com/virtual-tour/aspen",
        "featured": False,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Banff National Park",
        "country": "Canada",
        "city": "Banff",
        "category": "Mountain",
        "description": "Stunning Canadian Rockies with pristine lakes, glaciers, and wildlife. A UNESCO World Heritage site perfect for nature enthusiasts.",
        "price_range": "$200 - $500 per night",
        "activities": ["Hiking", "Canoeing", "Wildlife Viewing", "Photography", "Hot Springs", "Scenic Drives"],
        "best_time_to_visit": "June to August (Summer), December to March (Winter)",
        "images": [
            "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwzfHxtb3VudGFpbiUyMHJlc29ydHxlbnwwfHx8fDE3NTIzNDQ2NTB8MA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1707584145698-7a0b425a79e1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwyfHxhZHZlbnR1cmUlMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NjYxfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1715312889999-1898f3f8fbbc?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwzfHxhZHZlbnR1cmUlMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NjYxfDA&ixlib=rb-4.1.0&q=85"
        ],
        "coordinates": {"lat": 51.4968, "lng": -115.9281},
        "rating": 4.9,
        "reviews_count": 425,
        "virtual_tour_url": "https://example.com/virtual-tour/banff",
        "featured": False,
        "created_at": datetime.utcnow()
    },

    # CITY DESTINATIONS
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Tokyo Futuristic Experience",
        "country": "Japan",
        "city": "Tokyo",
        "category": "City",
        "description": "Immerse yourself in the perfect blend of traditional culture and cutting-edge technology. From ancient temples to neon-lit streets.",
        "price_range": "$150 - $400 per night",
        "activities": ["Temple Visits", "Sushi Making", "Tech Museums", "Shopping", "Nightlife", "Cultural Shows"],
        "best_time_to_visit": "March to May, September to November",
        "images": [
            "https://images.unsplash.com/photo-1493134799591-2c9eed26201a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxjaXR5JTIwc2t5bGluZXxlbnwwfHx8fDE3NTIzNDQ2NTV8MA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1541423408854-5df732b6f6d1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxjaXR5JTIwc2t5bGluZXxlbnwwfHx8fDE3NTIzNDQ2NTV8MA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1534298261662-f8fdd25317db?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwzfHxjaXR5JTIwc2t5bGluZXxlbnwwfHx8fDE3NTIzNDQ2NTV8MA&ixlib=rb-4.1.0&q=85"
        ],
        "coordinates": {"lat": 35.6762, "lng": 139.6503},
        "rating": 4.7,
        "reviews_count": 512,
        "virtual_tour_url": "https://example.com/virtual-tour/tokyo",
        "featured": True,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "New York Metropolitan",
        "country": "USA",
        "city": "New York",
        "category": "City",
        "description": "The city that never sleeps. Experience Broadway shows, world-class museums, iconic landmarks, and diverse culinary scenes.",
        "price_range": "$200 - $800 per night",
        "activities": ["Broadway Shows", "Museums", "Central Park", "Shopping", "Fine Dining", "Architecture Tours"],
        "best_time_to_visit": "April to June, September to November",
        "images": [
            "https://images.unsplash.com/photo-1534298261662-f8fdd25317db?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwzfHxjaXR5JTIwc2t5bGluZXxlbnwwfHx8fDE3NTIzNDQ2NTV8MA&ixlib=rb-4.1.0&q=85",
            "https://images.pexels.com/photos/7613/pexels-photo.jpg",
            "https://images.pexels.com/photos/290595/pexels-photo-290595.jpeg"
        ],
        "coordinates": {"lat": 40.7128, "lng": -74.0060},
        "rating": 4.6,
        "reviews_count": 689,
        "virtual_tour_url": "https://example.com/virtual-tour/nyc",
        "featured": False,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Dubai Luxury Experience",
        "country": "UAE",
        "city": "Dubai",
        "category": "City",
        "description": "Ultra-modern city with luxury shopping, innovative architecture, and world-class entertainment. Where tradition meets the future.",
        "price_range": "$250 - $1,000 per night",
        "activities": ["Burj Khalifa", "Desert Safari", "Luxury Shopping", "Fine Dining", "Water Parks", "Helicopter Tours"],
        "best_time_to_visit": "November to March",
        "images": [
            "https://images.unsplash.com/photo-1541423408854-5df732b6f6d1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxjaXR5JTIwc2t5bGluZXxlbnwwfHx8fDE3NTIzNDQ2NTV8MA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1493134799591-2c9eed26201a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxjaXR5JTIwc2t5bGluZXxlbnwwfHx8fDE3NTIzNDQ2NTV8MA&ixlib=rb-4.1.0&q=85",
            "https://images.pexels.com/photos/290595/pexels-photo-290595.jpeg"
        ],
        "coordinates": {"lat": 25.2048, "lng": 55.2708},
        "rating": 4.6,
        "reviews_count": 378,
        "virtual_tour_url": "https://example.com/virtual-tour/dubai",
        "featured": False,
        "created_at": datetime.utcnow()
    },

    # ADVENTURE DESTINATIONS
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Machu Picchu Adventure",
        "country": "Peru",
        "city": "Cusco",
        "category": "Adventure",
        "description": "Ancient Incan citadel perched high in the Andes. A UNESCO World Heritage site offering incredible history and breathtaking views.",
        "price_range": "$150 - $400 per night",
        "activities": ["Inca Trail", "Historical Tours", "Mountain Hiking", "Cultural Experiences", "Photography", "Local Cuisine"],
        "best_time_to_visit": "May to September",
        "images": [
            "https://images.unsplash.com/photo-1528543606781-2f6e6857f318?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwxfHxhZHZlbnR1cmUlMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NjYxfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1707584145698-7a0b425a79e1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwyfHxhZHZlbnR1cmUlMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NjYxfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1715312889999-1898f3f8fbbc?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwzfHxhZHZlbnR1cmUlMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NjYxfDA&ixlib=rb-4.1.0&q=85"
        ],
        "coordinates": {"lat": -13.1631, "lng": -72.5450},
        "rating": 4.8,
        "reviews_count": 456,
        "virtual_tour_url": "https://example.com/virtual-tour/machu-picchu",
        "featured": True,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Northern Lights Iceland",
        "country": "Iceland",
        "city": "Reykjavik",
        "category": "Adventure",
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
        "reviews_count": 334,
        "virtual_tour_url": "https://example.com/virtual-tour/iceland",
        "featured": False,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Patagonia Expedition",
        "country": "Chile/Argentina",
        "city": "Torres del Paine",
        "category": "Adventure",
        "description": "Rugged wilderness with glaciers, mountains, and unique wildlife. Perfect for serious adventurers and nature photographers.",
        "price_range": "$180 - $450 per night",
        "activities": ["Trekking", "Glacier Tours", "Wildlife Photography", "Kayaking", "Camping", "Rock Climbing"],
        "best_time_to_visit": "December to March",
        "images": [
            "https://images.unsplash.com/photo-1715312889999-1898f3f8fbbc?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwzfHxhZHZlbnR1cmUlMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NjYxfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1707584145698-7a0b425a79e1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwyfHxhZHZlbnR1cmUlMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NjYxfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1528543606781-2f6e6857f318?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwxfHxhZHZlbnR1cmUlMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NjYxfDA&ixlib=rb-4.1.0&q=85"
        ],
        "coordinates": {"lat": -50.9423, "lng": -73.4068},
        "rating": 4.7,
        "reviews_count": 198,
        "virtual_tour_url": "https://example.com/virtual-tour/patagonia",
        "featured": False,
        "created_at": datetime.utcnow()
    },

    # CULTURAL DESTINATIONS
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Santorini Sunset Villa",
        "country": "Greece",
        "city": "Santorini",
        "category": "Cultural",
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
        "reviews_count": 423,
        "virtual_tour_url": "https://example.com/virtual-tour/santorini",
        "featured": True,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Morocco Imperial Cities",
        "country": "Morocco",
        "city": "Marrakech",
        "category": "Cultural",
        "description": "Experience the magic of ancient medinas, vibrant souks, and stunning Islamic architecture. A journey through time and tradition.",
        "price_range": "$100 - $350 per night",
        "activities": ["Medina Tours", "Souk Shopping", "Desert Safari", "Cooking Classes", "Architecture Tours", "Hammam Spa"],
        "best_time_to_visit": "October to April",
        "images": [
            "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1573790387438-4da905039392?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=800&h=600&fit=crop"
        ],
        "coordinates": {"lat": 31.6295, "lng": -7.9811},
        "rating": 4.6,
        "reviews_count": 287,
        "virtual_tour_url": "https://example.com/virtual-tour/morocco",
        "featured": False,
        "created_at": datetime.utcnow()
    },
    {
        "destination_id": str(uuid.uuid4()),
        "name": "Kyoto Temple Experience",
        "country": "Japan",
        "city": "Kyoto",
        "category": "Cultural",
        "description": "Ancient capital with thousands of temples, traditional gardens, and preserved geisha districts. The heart of Japanese culture.",
        "price_range": "$120 - $400 per night",
        "activities": ["Temple Visits", "Tea Ceremony", "Garden Tours", "Geisha District", "Traditional Crafts", "Kaiseki Dining"],
        "best_time_to_visit": "March to May, September to November",
        "images": [
            "https://images.unsplash.com/photo-1493134799591-2c9eed26201a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxjaXR5JTIwc2t5bGluZXxlbnwwfHx8fDE3NTIzNDQ2NTV8MA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1541423408854-5df732b6f6d1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxjaXR5JTIwc2t5bGluZXxlbnwwfHx8fDE3NTIzNDQ2NTV8MA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1534298261662-f8fdd25317db?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwzfHxjaXR5JTIwc2t5bGluZXxlbnwwfHx8fDE3NTIzNDQ2NTV8MA&ixlib=rb-4.1.0&q=85"
        ],
        "coordinates": {"lat": 35.0116, "lng": 135.7681},
        "rating": 4.8,
        "reviews_count": 356,
        "virtual_tour_url": "https://example.com/virtual-tour/kyoto",
        "featured": False,
        "created_at": datetime.utcnow()
    }
]

# Travel Packages Data
travel_packages = [
    {
        "package_id": str(uuid.uuid4()),
        "name": "Tropical Paradise Combo",
        "description": "Experience the best tropical destinations with this luxury package including Maldives and Seychelles.",
        "destinations": ["Maldives Paradise Resort", "Seychelles Luxury Resort"],
        "duration": "10 days",
        "price": 4999,
        "original_price": 6000,
        "savings": 1001,
        "includes": ["Flights", "Luxury Accommodation", "Meals", "Activities", "Transfers"],
        "image": "https://images.unsplash.com/photo-1551918120-9739cb430c6d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwyfHxsdXh1cnklMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NTk3fDA&ixlib=rb-4.1.0&q=85",
        "featured": True,
        "available": True,
        "max_group_size": 4,
        "difficulty": "Easy",
        "created_at": datetime.utcnow()
    },
    {
        "package_id": str(uuid.uuid4()),
        "name": "Adventure Explorer",
        "description": "Thrilling adventure package combining Machu Picchu hiking and Patagonia expedition for ultimate adventurers.",
        "destinations": ["Machu Picchu Adventure", "Patagonia Expedition"],
        "duration": "14 days",
        "price": 3799,
        "original_price": 4500,
        "savings": 701,
        "includes": ["Flights", "Adventure Lodging", "Guided Tours", "Equipment", "Meals"],
        "image": "https://images.unsplash.com/photo-1528543606781-2f6e6857f318?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwxfHxhZHZlbnR1cmUlMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMzQ0NjYxfDA&ixlib=rb-4.1.0&q=85",
        "featured": True,
        "available": True,
        "max_group_size": 8,
        "difficulty": "Challenging",
        "created_at": datetime.utcnow()
    },
    {
        "package_id": str(uuid.uuid4()),
        "name": "Cultural Heritage Journey",
        "description": "Immerse yourself in rich cultures visiting Japan's ancient temples and Morocco's imperial cities.",
        "destinations": ["Kyoto Temple Experience", "Morocco Imperial Cities"],
        "duration": "12 days",
        "price": 2999,
        "original_price": 3600,
        "savings": 601,
        "includes": ["Flights", "Cultural Accommodation", "Guided Tours", "Cultural Activities", "Local Cuisine"],
        "image": "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&h=600&fit=crop",
        "featured": False,
        "available": True,
        "max_group_size": 6,
        "difficulty": "Moderate",
        "created_at": datetime.utcnow()
    },
    {
        "package_id": str(uuid.uuid4()),
        "name": "Alpine & City Experience",
        "description": "Perfect blend of mountain adventure and urban sophistication with Swiss Alps and Tokyo.",
        "destinations": ["Swiss Alps Adventure", "Tokyo Futuristic Experience"],
        "duration": "8 days",
        "price": 2599,
        "original_price": 3200,
        "savings": 601,
        "includes": ["Flights", "Premium Hotels", "City Tours", "Mountain Activities", "Transportation"],
        "image": "https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwyfHxtb3VudGFpbiUyMHJlc29ydHxlbnwwfHx8fDE3NTIzNDQ2NTB8MA&ixlib=rb-4.1.0&q=85",
        "featured": False,
        "available": True,
        "max_group_size": 4,
        "difficulty": "Moderate",
        "created_at": datetime.utcnow()
    }
]

# Enhanced reviews with more variety
enhanced_reviews = [
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
    },
    {
        "review_id": str(uuid.uuid4()),
        "user_id": "demo-user-3",
        "username": "CityExplorer",
        "rating": 5,
        "comment": "Tokyo exceeded all expectations! The perfect blend of traditional and modern. The hotel was in a great location and the tech amenities were impressive.",
        "images": [],
        "helpful_count": 31,
        "categories": {"Service": 5, "Value": 4, "Location": 5, "Cleanliness": 5},
        "verified_stay": True,
        "created_at": datetime.utcnow()
    },
    {
        "review_id": str(uuid.uuid4()),
        "user_id": "demo-user-4",
        "username": "CultureBuff",
        "rating": 4,
        "comment": "Santorini is magical! The sunset views are unreal and the Greek hospitality is wonderful. The wine tasting tour was a highlight.",
        "images": [],
        "helpful_count": 15,
        "categories": {"Service": 4, "Value": 3, "Location": 5, "Cleanliness": 4},
        "verified_stay": True,
        "created_at": datetime.utcnow()
    }
]

async def seed_enhanced_database():
    try:
        # Clear existing data
        await destinations_collection.delete_many({})
        await reviews_collection.delete_many({})
        await packages_collection.delete_many({})
        
        # Insert enhanced destinations
        await destinations_collection.insert_many(enhanced_destinations)
        print(f"Inserted {len(enhanced_destinations)} enhanced destinations")
        
        # Insert travel packages
        await packages_collection.insert_many(travel_packages)
        print(f"Inserted {len(travel_packages)} travel packages")
        
        # Add destination_id to reviews
        destinations = await destinations_collection.find({}).to_list(length=None)
        for i, review in enumerate(enhanced_reviews):
            if i < len(destinations):
                review["destination_id"] = destinations[i]["destination_id"]
        
        # Insert enhanced reviews
        await reviews_collection.insert_many(enhanced_reviews)
        print(f"Inserted {len(enhanced_reviews)} enhanced reviews")
        
        print("Enhanced database seeded successfully!")
        print(f"Total destinations: {len(enhanced_destinations)}")
        print("Categories: Tropical, Mountain, City, Adventure, Cultural")
        print("Featured travel packages created!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_enhanced_database())