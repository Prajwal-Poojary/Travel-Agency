from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
import uuid
import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
import logging

# Import our enhanced services
from enhanced_ai_service import ai_service
from virtual_tours_service import virtual_tours_service
from weather_service import weather_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Advanced Travel Platform API",
    description="Complete travel platform with AI, virtual tours, and weather integration",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/advanced_travel_db")
client = AsyncIOMotorClient(MONGO_URL)
db = client.advanced_travel_db

# Collections
users_collection = db.users
destinations_collection = db.destinations
bookings_collection = db.bookings
reviews_collection = db.reviews
chat_sessions_collection = db.chat_sessions
packages_collection = db.travel_packages

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class AIRecommendationRequest(BaseModel):
    budget: Optional[str] = "moderate"
    activities: Optional[List[str]] = []
    travel_style: Optional[str] = "leisure"
    duration: Optional[str] = "1 week"
    group_size: Optional[int] = 2
    interests: Optional[List[str]] = []

class BookingCreate(BaseModel):
    destination_id: str
    check_in_date: datetime
    check_out_date: datetime
    guests: int
    special_requests: Optional[str] = None

class ReviewCreate(BaseModel):
    destination_id: str
    rating: int
    comment: str
    images: Optional[List[str]] = []
    categories: Optional[Dict[str, int]] = {}

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Utility functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await users_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

# API Routes

@app.get("/")
async def root():
    return {
        "message": "Advanced Travel Platform API v2.0",
        "features": [
            "AI-powered recommendations",
            "Virtual tours with 360° videos",
            "Real-time weather integration",
            "Complete booking system",
            "User reviews and ratings"
        ],
        "status": "operational"
    }

# Authentication Routes
@app.post("/api/auth/register")
async def register(user: UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    user_data = {
        "user_id": str(uuid.uuid4()),
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "preferences": {},
        "avatar": None
    }
    
    await users_collection.insert_one(user_data)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": user.username}

@app.post("/api/auth/login")
async def login(user: UserLogin):
    db_user = await users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": db_user["username"]}

@app.get("/api/auth/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "avatar": current_user.get("avatar"),
        "preferences": current_user.get("preferences", {}),
        "created_at": current_user["created_at"]
    }

# Enhanced Destinations Routes
@app.get("/api/destinations")
async def get_destinations(
    search: Optional[str] = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    activity: Optional[str] = None,
    featured_only: Optional[bool] = False,
    limit: Optional[int] = 100
):
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"city": {"$regex": search, "$options": "i"}},
            {"country": {"$regex": search, "$options": "i"}}
        ]
    
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    
    if activity:
        query["activities"] = {"$in": [activity]}
    
    if featured_only:
        query["featured"] = True
    
    destinations = await destinations_collection.find(query).limit(limit).to_list(length=limit)
    
    # Add enhanced data for each destination
    for destination in destinations:
        destination["_id"] = str(destination["_id"])
        
        # Add weather data
        weather_data = await weather_service.get_current_weather(
            destination["city"], 
            destination["country"]
        )
        destination["weather"] = weather_data
        
        # Add virtual tour info if available
        virtual_tour = virtual_tours_service.get_tour_by_destination(destination["name"])
        if virtual_tour:
            destination["virtual_tour"] = {
                "available": True,
                "duration": virtual_tour["duration"],
                "type": virtual_tour["tour_type"],
                "features": virtual_tour["features"]
            }
        else:
            destination["virtual_tour"] = {"available": False}
    
    return destinations

@app.get("/api/destinations/{destination_id}")
async def get_destination(destination_id: str):
    destination = await destinations_collection.find_one({"destination_id": destination_id})
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    destination["_id"] = str(destination["_id"])
    
    # Add enhanced weather data
    weather_data = await weather_service.get_travel_weather_advice(
        destination["city"], 
        destination["country"]
    )
    destination["weather"] = weather_data
    
    # Add virtual tour data
    virtual_tour = virtual_tours_service.get_tour_by_destination(destination["name"])
    if virtual_tour:
        destination["virtual_tour"] = virtual_tour
    
    return destination

@app.get("/api/destinations/countries")
async def get_countries():
    countries = await destinations_collection.distinct("country")
    return countries

@app.get("/api/destinations/activities")
async def get_activities():
    activities = await destinations_collection.distinct("activities")
    return activities

# Enhanced AI Routes
@app.post("/api/ai/recommendations")
async def get_ai_recommendations(
    request: AIRecommendationRequest,
    current_user: dict = Depends(get_current_user)
):
    user_preferences = {
        "budget": request.budget,
        "activities": request.activities,
        "travel_style": request.travel_style,
        "duration": request.duration,
        "group_size": request.group_size,
        "interests": request.interests
    }
    
    context = f"User: {current_user['username']}, Email: {current_user['email']}"
    recommendations = await ai_service.get_travel_recommendations(user_preferences, context)
    
    return recommendations

@app.post("/api/chat")
async def chat_with_ai(message: ChatMessage):
    try:
        session_id = message.session_id or str(uuid.uuid4())
        
        # Get chat history
        chat_session = await chat_sessions_collection.find_one({"session_id": session_id})
        chat_history = chat_session.get("messages", []) if chat_session else []
        
        # Get AI response
        response = await ai_service.chat_with_assistant(
            message.message, 
            session_id, 
            chat_history
        )
        
        # Update chat session
        new_messages = chat_history + [
            {"role": "user", "content": message.message, "timestamp": datetime.utcnow()},
            {"role": "assistant", "content": response["response"], "timestamp": datetime.utcnow()}
        ]
        
        await chat_sessions_collection.replace_one(
            {"session_id": session_id},
            {
                "session_id": session_id,
                "messages": new_messages,
                "updated_at": datetime.utcnow()
            },
            upsert=True
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat service temporarily unavailable")

# Virtual Tours Routes
@app.get("/api/virtual-tours")
async def get_virtual_tours(
    search: Optional[str] = None,
    limit: Optional[int] = 20
):
    if search:
        tours = virtual_tours_service.search_tours(search)
    else:
        tours = virtual_tours_service.get_all_tours()
    
    return tours[:limit]

@app.get("/api/virtual-tours/featured")
async def get_featured_virtual_tours(limit: Optional[int] = 6):
    return virtual_tours_service.get_featured_tours(limit)

@app.get("/api/virtual-tours/{tour_id}")
async def get_virtual_tour(tour_id: str):
    tour = virtual_tours_service.get_tour_by_id(tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail="Virtual tour not found")
    
    return tour

@app.get("/api/virtual-tours/{tour_id}/analytics")
async def get_tour_analytics(tour_id: str):
    analytics = virtual_tours_service.get_tour_analytics(tour_id)
    if "error" in analytics:
        raise HTTPException(status_code=404, detail=analytics["error"])
    
    return analytics

# Weather Routes
@app.get("/api/weather/{city}")
async def get_weather(city: str, country: Optional[str] = None):
    weather_data = await weather_service.get_current_weather(city, country)
    return weather_data

@app.get("/api/weather/{city}/forecast")
async def get_weather_forecast(
    city: str, 
    country: Optional[str] = None, 
    days: Optional[int] = 5
):
    forecast_data = await weather_service.get_weather_forecast(city, country, days)
    return forecast_data

@app.get("/api/weather/{city}/travel-advice")
async def get_travel_weather_advice(city: str, country: Optional[str] = None):
    advice = await weather_service.get_travel_weather_advice(city, country)
    return advice

# Enhanced Bookings Routes
@app.post("/api/bookings")
async def create_booking(booking: BookingCreate, current_user: dict = Depends(get_current_user)):
    # Validate destination exists
    destination = await destinations_collection.find_one({"destination_id": booking.destination_id})
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    booking_data = {
        "booking_id": str(uuid.uuid4()),
        "user_id": current_user["user_id"],
        "destination_id": booking.destination_id,
        "destination_name": destination["name"],
        "check_in_date": booking.check_in_date,
        "check_out_date": booking.check_out_date,
        "guests": booking.guests,
        "special_requests": booking.special_requests,
        "status": "pending",
        "total_amount": 0,  # Calculate based on destination pricing
        "created_at": datetime.utcnow()
    }
    
    result = await bookings_collection.insert_one(booking_data)
    booking_data["_id"] = str(result.inserted_id)
    
    return booking_data

@app.get("/api/bookings")
async def get_user_bookings(current_user: dict = Depends(get_current_user)):
    bookings = await bookings_collection.find({"user_id": current_user["user_id"]}).to_list(length=100)
    
    for booking in bookings:
        booking["_id"] = str(booking["_id"])
        
        # Add destination details
        destination = await destinations_collection.find_one({"destination_id": booking["destination_id"]})
        if destination:
            booking["destination_details"] = {
                "name": destination["name"],
                "city": destination["city"],
                "country": destination["country"],
                "images": destination.get("images", [])
            }
    
    return bookings

# Enhanced Reviews Routes
@app.post("/api/reviews")
async def create_review(review: ReviewCreate, current_user: dict = Depends(get_current_user)):
    # Validate destination exists
    destination = await destinations_collection.find_one({"destination_id": review.destination_id})
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    review_data = {
        "review_id": str(uuid.uuid4()),
        "destination_id": review.destination_id,
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "rating": review.rating,
        "comment": review.comment,
        "images": review.images,
        "categories": review.categories,
        "helpful_count": 0,
        "verified_stay": False,  # Could be verified based on bookings
        "created_at": datetime.utcnow()
    }
    
    result = await reviews_collection.insert_one(review_data)
    review_data["_id"] = str(result.inserted_id)
    
    # Update destination rating
    await update_destination_rating(review.destination_id)
    
    return review_data

@app.get("/api/reviews/{destination_id}")
async def get_destination_reviews(destination_id: str, limit: Optional[int] = 50):
    reviews = await reviews_collection.find({"destination_id": destination_id}).limit(limit).to_list(length=limit)
    
    for review in reviews:
        review["_id"] = str(review["_id"])
    
    return reviews

async def update_destination_rating(destination_id: str):
    """Update destination rating based on reviews"""
    pipeline = [
        {"$match": {"destination_id": destination_id}},
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
    ]
    
    result = await reviews_collection.aggregate(pipeline).to_list(length=None)
    if result:
        new_rating = round(result[0]["avg_rating"], 1)
        await destinations_collection.update_one(
            {"destination_id": destination_id},
            {"$set": {"rating": new_rating}}
        )

# Travel Packages Routes
@app.get("/api/packages")
async def get_travel_packages(featured_only: Optional[bool] = False):
    query = {}
    if featured_only:
        query["featured"] = True
    
    packages = await packages_collection.find(query).to_list(length=50)
    
    for package in packages:
        package["_id"] = str(package["_id"])
    
    return packages

@app.get("/api/packages/{package_id}")
async def get_travel_package(package_id: str):
    package = await packages_collection.find_one({"package_id": package_id})
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    package["_id"] = str(package["_id"])
    
    # Get destination details for the package
    destination_details = []
    for dest_name in package["destinations"]:
        dest = await destinations_collection.find_one({"name": dest_name})
        if dest:
            dest["_id"] = str(dest["_id"])
            destination_details.append(dest)
    
    package["destination_details"] = destination_details
    
    return package

# WebSocket for real-time notifications
@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now - can be enhanced for real-time features
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Health check
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": "connected",
            "ai_service": "available" if ai_service.model else "limited",
            "weather_service": "available" if weather_service.api_key else "mock_data",
            "virtual_tours": "available"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)