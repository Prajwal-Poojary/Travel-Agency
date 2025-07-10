from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
import uuid
import json
import asyncio
import google.generativeai as genai
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
import base64
from io import BytesIO
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Advanced Travel Platform API",
    description="High-tech travel platform with AI integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

# Google Gemini AI setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

# Weather API
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

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

class UserProfile(BaseModel):
    username: str
    email: str
    full_name: str
    avatar: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = {}
    created_at: datetime

class DestinationCreate(BaseModel):
    name: str
    country: str
    city: str
    description: str
    price_range: str
    activities: List[str]
    best_time_to_visit: str
    images: List[str]
    coordinates: Dict[str, float]
    rating: float = 0.0
    virtual_tour_url: Optional[str] = None

class BookingCreate(BaseModel):
    destination_id: str
    user_id: str
    check_in_date: datetime
    check_out_date: datetime
    guests: int
    special_requests: Optional[str] = None

class ReviewCreate(BaseModel):
    destination_id: str
    user_id: str
    rating: int
    comment: str
    images: Optional[List[str]] = []

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

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

async def get_weather_data(city: str):
    if not WEATHER_API_KEY:
        return {"error": "Weather API key not configured"}
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Weather data not available"}
    except Exception as e:
        return {"error": str(e)}

async def get_ai_recommendations(user_preferences: Dict[str, Any], context: str = ""):
    if not GEMINI_API_KEY:
        return {"error": "AI service not configured"}
    
    try:
        prompt = f"""
        You are an expert travel advisor. Based on the following user preferences, provide personalized travel recommendations:
        
        User Preferences: {json.dumps(user_preferences)}
        Context: {context}
        
        Please provide:
        1. Top 3 destination recommendations with reasons
        2. Best time to visit each destination
        3. Suggested activities for each destination
        4. Budget estimates
        5. Travel tips specific to the user's preferences
        
        Format your response as a JSON object with clear structure.
        """
        
        response = model.generate_content(prompt)
        return {"recommendations": response.text}
    except Exception as e:
        logger.error(f"AI recommendation error: {str(e)}")
        return {"error": "AI service temporarily unavailable"}

# API Routes

@app.get("/")
async def root():
    return {"message": "Advanced Travel Platform API", "version": "1.0.0"}

# Authentication Routes
@app.post("/api/auth/register")
async def register(user: UserCreate):
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
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
    
    # Create access token
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

# Destinations Routes
@app.get("/api/destinations")
async def get_destinations(
    search: Optional[str] = None,
    country: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    activity: Optional[str] = None
):
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"city": {"$regex": search, "$options": "i"}}
        ]
    
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    
    if activity:
        query["activities"] = {"$in": [activity]}
    
    destinations = await destinations_collection.find(query).to_list(length=100)
    
    # Add weather data for each destination
    for destination in destinations:
        destination["_id"] = str(destination["_id"])
        weather_data = await get_weather_data(destination["city"])
        destination["weather"] = weather_data
    
    return destinations

@app.get("/api/destinations/{destination_id}")
async def get_destination(destination_id: str):
    destination = await destinations_collection.find_one({"_id": destination_id})
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    destination["_id"] = str(destination["_id"])
    weather_data = await get_weather_data(destination["city"])
    destination["weather"] = weather_data
    
    return destination

@app.post("/api/destinations")
async def create_destination(destination: DestinationCreate):
    destination_data = destination.dict()
    destination_data["destination_id"] = str(uuid.uuid4())
    destination_data["created_at"] = datetime.utcnow()
    
    result = await destinations_collection.insert_one(destination_data)
    destination_data["_id"] = str(result.inserted_id)
    
    return destination_data

# Bookings Routes
@app.post("/api/bookings")
async def create_booking(booking: BookingCreate, current_user: dict = Depends(get_current_user)):
    booking_data = booking.dict()
    booking_data["booking_id"] = str(uuid.uuid4())
    booking_data["user_id"] = current_user["user_id"]
    booking_data["status"] = "pending"
    booking_data["created_at"] = datetime.utcnow()
    
    result = await bookings_collection.insert_one(booking_data)
    booking_data["_id"] = str(result.inserted_id)
    
    return booking_data

@app.get("/api/bookings")
async def get_user_bookings(current_user: dict = Depends(get_current_user)):
    bookings = await bookings_collection.find({"user_id": current_user["user_id"]}).to_list(length=100)
    
    for booking in bookings:
        booking["_id"] = str(booking["_id"])
        # Get destination details
        destination = await destinations_collection.find_one({"destination_id": booking["destination_id"]})
        if destination:
            booking["destination"] = {
                "name": destination["name"],
                "city": destination["city"],
                "country": destination["country"]
            }
    
    return bookings

# Reviews Routes
@app.post("/api/reviews")
async def create_review(review: ReviewCreate, current_user: dict = Depends(get_current_user)):
    review_data = review.dict()
    review_data["review_id"] = str(uuid.uuid4())
    review_data["user_id"] = current_user["user_id"]
    review_data["username"] = current_user["username"]
    review_data["created_at"] = datetime.utcnow()
    
    result = await reviews_collection.insert_one(review_data)
    review_data["_id"] = str(result.inserted_id)
    
    return review_data

@app.get("/api/reviews/{destination_id}")
async def get_destination_reviews(destination_id: str):
    reviews = await reviews_collection.find({"destination_id": destination_id}).to_list(length=100)
    
    for review in reviews:
        review["_id"] = str(review["_id"])
    
    return reviews

# AI Recommendations Route
@app.post("/api/ai/recommendations")
async def get_travel_recommendations(
    preferences: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    context = f"User: {current_user['username']}, Email: {current_user['email']}"
    recommendations = await get_ai_recommendations(preferences, context)
    return recommendations

# Chat/AI Assistant Routes
@app.post("/api/chat")
async def chat_with_ai(message: ChatMessage):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="AI service not configured")
    
    try:
        session_id = message.session_id or str(uuid.uuid4())
        
        # Get chat history
        chat_session = await chat_sessions_collection.find_one({"session_id": session_id})
        if not chat_session:
            chat_session = {
                "session_id": session_id,
                "messages": [],
                "created_at": datetime.utcnow()
            }
        
        # Add user message to history
        chat_session["messages"].append({
            "role": "user",
            "content": message.message,
            "timestamp": datetime.utcnow()
        })
        
        # Generate AI response
        context = "You are a helpful travel assistant. Provide helpful, accurate travel advice and recommendations."
        full_prompt = f"{context}\n\nUser: {message.message}"
        
        response = model.generate_content(full_prompt)
        ai_response = response.text
        
        # Add AI response to history
        chat_session["messages"].append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.utcnow()
        })
        
        # Save chat session
        await chat_sessions_collection.replace_one(
            {"session_id": session_id},
            chat_session,
            upsert=True
        )
        
        return {
            "session_id": session_id,
            "response": ai_response,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat service temporarily unavailable")

# WebSocket for real-time notifications
@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)