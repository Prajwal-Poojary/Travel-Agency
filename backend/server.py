import os
import re
import json
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, Header, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import jwt
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
from uuid import uuid4
import asyncio

# Gemini SDK (2025)
from google import genai
from google.genai import types as genai_types

# Load env from backend/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# ---- Env ----
MONGO_URL = os.environ.get('MONGO_URL')
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'dev_secret')
CORS_ORIGINS = [o.strip() for o in (os.environ.get('CORS_ORIGINS') or '').split(',') if o.strip()]
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', '8001'))
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')

if not MONGO_URL:
    raise RuntimeError('MONGO_URL is required in backend/.env')

# ---- App ----
app = FastAPI(title='Advanced Travel Platform (FastAPI)', version='1.4.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---- DB ----
import dns.resolver
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']

try:
    client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db_name_match = re.search(r"/([^/?]+)(?:\?|$)", MONGO_URL)
    DB_NAME = client.get_default_database().name if getattr(client, 'get_default_database', None) and client.get_default_database() is not None else (db_name_match.group(1) if db_name_match else None)
    if not DB_NAME:
        print("Warning: Database name not found in MONGO_URL")
        db = None
    else:
        db = client[DB_NAME]
except Exception as e:
    print(f"Warning: Could not initialize MongoDB client: {e}")
    db = None
    client = None

# ---- Gemini ----
gemini_client: Optional[genai.Client] = None
if GEMINI_API_KEY:
    try:
        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=genai_types.HttpOptions(timeout=120_000),
        )
    except Exception:
        gemini_client = None

# ---- Models ----
class RegisterBody(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = ''

class LoginBody(BaseModel):
    email: str
    password: str

class ForgotPasswordReq(BaseModel):
    email: str

class ResetPasswordReq(BaseModel):
    token: str
    new_password: str

class ProfileOut(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: str = ''
    avatar: Optional[str] = None
    created_at: datetime

class ProfileUpdateBody(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None

class ChatBody(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None

class ChatOut(BaseModel):
    session_id: str
    response: str
    timestamp: datetime

class RecReq(BaseModel):
    budget: Optional[str] = None
    activities: Optional[List[str]] = None
    travel_style: Optional[str] = None
    duration: Optional[str] = None
    group_size: Optional[int] = None
    interests: Optional[List[str]] = None

class NarrationReq(BaseModel):
    voice_style: Optional[str] = Field(default='friendly', description='Narration style')
    pace: Optional[str] = Field(default='medium', description='slow/medium/fast')
    duration_hint: Optional[str] = Field(default='short', description='short/medium/long')
    language: Optional[str] = Field(default='en', description='Language code')

class Destination(BaseModel):
    destination_id: str
    name: str
    description: str
    country: str
    images: List[str]
    rating: float
    price_range: str
    price: Optional[float] = None
    activities: List[str]
    featured: bool


class BookingReq(BaseModel):
    destination_id: str
    check_in_date: str
    check_out_date: str
    guests: int
    total_price: float

class ReviewReq(BaseModel):
    destination_id: str
    rating: int
    comment: str

# ---- Mock Data (Fallback) ----
MOCK_DESTINATIONS = [
    {
        "destination_id": "1",
        "name": "Santorini",
        "description": "Whitewashed buildings, blue domes, and stunning sunsets over the Aegean Sea.",
        "country": "Greece",
        "images": ["https://images.unsplash.com/photo-1613395877344-13d4c2ce5d4d?w=800"],
        "rating": 4.8,
        "price_range": "$1500 - $3000",
        "activities": ["Sightseeing", "Boating", "Dining"],
        "featured": True
    },
    {
        "destination_id": "2",
        "name": "Kyoto",
        "description": "Ancient temples, traditional tea houses, and beautiful cherry blossoms.",
        "country": "Japan",
        "images": ["https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800"],
        "rating": 4.9,
        "price_range": "$2000 - $4000",
        "activities": ["Cultural", "Walking", "Food"],
        "featured": True
    },
    {
        "destination_id": "3",
        "name": "Machu Picchu",
        "description": "Incan citadel set high in the Andes Mountains in Peru.",
        "country": "Peru",
        "images": ["https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=800"],
        "rating": 4.9,
        "price_range": "$1200 - $2500",
        "activities": ["Hiking", "History", "Nature"],
        "featured": True
    },
    {
        "destination_id": "4",
        "name": "Maldives",
        "description": "Tropical nation in the Indian Ocean known for its beaches, blue lagoons and extensive reefs.",
        "country": "Maldives",
        "images": ["https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800"],
        "rating": 4.9,
        "price_range": "$3000 - $6000",
        "activities": ["Relaxation", "Diving", "Luxury"],
        "featured": True
    },
    {
        "destination_id": "5",
        "name": "Amalfi Coast",
        "description": "Stretch of coastline in Southern Italy overlooking the Tyrrhenian Sea and the Gulf of Salerno.",
        "country": "Italy",
        "images": ["https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800"],
        "rating": 4.7,
        "price_range": "$1800 - $3500",
        "activities": ["Driving", "Dining", "Coastal"],
        "featured": True
    },
    {
        "destination_id": "6",
        "name": "Banff",
        "description": "Resort town in the province of Alberta, located within Banff National Park.",
        "country": "Canada",
        "images": ["https://images.unsplash.com/photo-1533587851505-d119e13fa0d7?w=800"],
        "rating": 4.8,
        "price_range": "$1000 - $2500",
        "activities": ["Hiking", "Nature", "Skiing"],
        "featured": True
    }
]

MOCK_VIRTUAL_TOURS = [
    {
        'tour_id': '1',
        'name': 'Tokyo 360° Night Walk',
        'country': 'Japan',
        'duration': '12:45',
        'tour_type': '360_video',
        'thumbnail': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800',
        'video_url': 'https://www.youtube.com/watch?v=LXb3EKWsInQ',
        'description': 'Experience the neon-lit streets of Shinjuku and Shibuya in fully immersive 360°.',
        'features': ['360° View', 'City Walk', 'Nightlife'],
        'featured': True,
        'views': 1200,
        'highlights': [
            {'time': '00:45', 'title': 'Shinjuku Crossing', 'description': 'Bustling intersection views'},
            {'time': '05:10', 'title': 'Golden Gai', 'description': 'Cozy alleys and bars'},
        ],
    },
    {
        'tour_id': '2',
        'name': 'Santorini Cliffside 360°',
        'country': 'Greece',
        'duration': '9:03',
        'tour_type': 'drone_360',
        'thumbnail': 'https://images.unsplash.com/photo-1613395877344-13d4c2ce5d4d?w=800',
        'video_url': 'https://www.youtube.com/watch?v=LXb3EKWsInQ',
        'description': 'A breathtaking aerial 360° tour of Santorini’s blue domes and caldera views.',
        'features': ['Drone 360', 'Coastline', 'Sunset'],
        'featured': True,
        'views': 950,
        'highlights': [],
    },
    {
        'tour_id': '3',
        'name': 'Times Square Live',
        'country': 'USA',
        'duration': 'LIVE',
        'tour_type': 'live_cam',
        'thumbnail': 'https://images.unsplash.com/photo-1534430480872-3498386e7856?w=800',
        'video_url': 'https://www.youtube.com/watch?v=LXb3EKWsInQ',
        'description': 'Live streaming view of the heart of New York City.',
        'features': ['Live Stream', 'Cityscape', 'Crowds'],
        'featured': True,
        'views': 5000,
        'highlights': [],
    },
    {
        'tour_id': '4',
        'name': 'Maldives Drone 4K',
        'country': 'Maldives',
        'duration': '04:15',
        'tour_type': 'drone_video',
        'thumbnail': 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800',
        'video_url': 'https://www.youtube.com/watch?v=LXb3EKWsInQ',
        'description': 'Cinematic drone footage of crystal clear waters and overwater bungalows.',
        'features': ['4K Resolution', 'Drone View', 'Relaxation'],
        'featured': False,
        'views': 320,
        'highlights': [],
    },
    {
        'tour_id': '5',
        'name': 'Aurora Borealis 360',
        'country': 'Iceland',
        'duration': '02:30',
        'tour_type': '360_video',
        'thumbnail': 'https://images.unsplash.com/photo-1520769945061-0a448c4ece65?w=800',
        'video_url': 'https://www.youtube.com/watch?v=LXb3EKWsInQ',
        'description': 'Immersive 360 video of the Northern Lights dancing over snow-covered landscapes.',
        'features': ['360° View', 'Nature', 'Night Sky'],
        'featured': True,
        'views': 450,
        'highlights': [],
    },
    {
        'tour_id': '6',
        'name': 'Venice Grand Canal Live',
        'country': 'Italy',
        'duration': 'LIVE',
        'tour_type': 'live_cam',
        'thumbnail': 'https://images.unsplash.com/photo-1514890547357-a9ee288728e0?w=800',
        'video_url': 'https://www.youtube.com/watch?v=LXb3EKWsInQ',
        'description': 'Live view of the Grand Canal and Rialto Bridge in Venice.',
        'features': ['Live Stream', 'Historic', 'Waterway'],
        'featured': False,
        'views': 1200,
        'highlights': [],
    },
    {
        'tour_id': '7',
        'name': 'Machu Picchu Interactive',
        'country': 'Peru',
        'duration': '14:22',
        'tour_type': '360_video',
        'thumbnail': 'https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=800',
        'video_url': 'https://www.youtube.com/watch?v=LXb3EKWsInQ',
        'description': 'Explore the ancient citadel with points-of-interest overlays.',
        'features': ['Interactive', 'Ruins', 'Mountains'],
        'featured': True,
        'views': 200,
        'highlights': [],
    },
    {
        'tour_id': '8',
        'name': 'Paris Louvre Walkthrough',
        'country': 'France',
        'duration': '11:11',
        'tour_type': '360_video',
        'thumbnail': 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=800',
        'video_url': 'https://www.youtube.com/watch?v=LXb3EKWsInQ',
        'description': 'A cultural 360° stroll through Louvre courtyards and nearby landmarks.',
        'features': ['Museums', 'Culture', 'City Walk'],
        'featured': False,
        'views': 45,
    },
    {
        'tour_id': '9',
        'name': 'Swiss Alps Drone View',
        'country': 'Switzerland',
        'duration': '05:45',
        'tour_type': 'drone_video',
        'thumbnail': 'https://images.unsplash.com/photo-1531366936337-7785a610e20f?w=800',
        'video_url': 'https://www.youtube.com/watch?v=LXb3EKWsInQ',
        'description': 'Stunning 4K drone footage of the Swiss Alps in winter.',
        'features': ['Drone View', 'Mountains', 'Snow'],
        'featured': False,
        'views': 550,
    },
    {
        'tour_id': '10',
        'name': 'Kyoto Cherry Blossoms',
        'country': 'Japan',
        'duration': '08:20',
        'tour_type': '360_video',
        'thumbnail': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800',
        'video_url': 'https://www.youtube.com/watch?v=LXb3EKWsInQ',
        'description': 'Relaxing 360° walk through Kyoto temples during cherry blossom season.',
        'features': ['360° View', 'Nature', 'Relaxation'],
        'featured': True,
        'views': 890,
    }
]

# ---- Utils ----
ALG = 'HS256'

def fix_id(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

def create_token(username: str, user_id: str) -> str:
    payload = {
        'username': username,
        'user_id': user_id,
        'iat': int(datetime.utcnow().timestamp()),
        'exp': int((datetime.utcnow() + timedelta(days=30)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALG)

async def get_user_from_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='No token provided')
    token = authorization.split(' ', 1)[1]
    if token == 'mock_token':
        return {'user_id': 'mock_user_id', 'username': 'demo_user', 'email': 'demo@example.com', 'created_at': datetime.utcnow()}
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALG])
        username = payload.get('username')
        if db is None:
             raise HTTPException(status_code=500, detail='Database unavailable')
        user = await db.users.find_one({'username': username})
        if not user:
            raise HTTPException(status_code=401, detail='User not found')
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail='Invalid token')

# ---- Chat persistence helpers ----
async def upsert_session_message(user_id: str, session_id: str, role: str, content: str):
    if db is None: return # Skip persistence
    now = datetime.utcnow().isoformat()
    await db.chat_sessions.update_one(
        {'session_id': session_id, 'user_id': user_id},
        {
            '$setOnInsert': {
                'session_id': session_id,
                'user_id': user_id,
                'created_at': now
            },
            '$set': { 'updated_at': now },
            '$push': { 'messages': {'role': role, 'content': content, 'timestamp': now} }
        },
        upsert=True
    )

async def ensure_indexes_and_seed():
    # Users
    await db.users.create_index('email', unique=True)
    await db.users.create_index('username', unique=True)

    # Chat sessions
    await db.chat_sessions.create_index('session_id', unique=True)
    await db.chat_sessions.create_index('user_id')

    # Favorites
    await db.favorites.create_index([('user_id', 1), ('tour_id', 1)], unique=True)
    await db.favorites.create_index('user_id')

    # Virtual tours
    await db.virtual_tours.create_index('tour_id', unique=True)
    await db.virtual_tours.create_index('name')
    await db.virtual_tours.create_index('country')
    await db.virtual_tours.create_index('tour_type')
    await db.virtual_tours.create_index('featured')
    await db.virtual_tours.create_index('views')

    # Seed demo user
    demo = await db.users.find_one({'email': 'demo@example.com'})
    if not demo:
        await db.users.insert_one({
            'user_id': str(uuid4()),
            'username': 'demo_user',
            'email': 'demo@example.com',
            'full_name': 'Demo User',
            'password': pwd_context.hash('password123'),
            'avatar': None,
            'created_at': datetime.utcnow(),
        })

    # Force refresh virtual tours for development
    await db.virtual_tours.delete_many({})
    await db.virtual_tours.insert_many(MOCK_VIRTUAL_TOURS)

    # Seed destinations (only if empty)
    d_count = await db.destinations.estimated_document_count()
    if d_count == 0:
        await db.destinations.insert_many(MOCK_DESTINATIONS)

# ---- Startup ----
@app.on_event('startup')
async def on_start():
    global db
    if db is not None:
        try:
            # Verify actual connection
            await client.admin.command('ping')
            await ensure_indexes_and_seed()
            print("Database connected and seeded successfully.")
        except Exception as e:
            print(f"Warning: Database connection failed: {e}")
            print("Switching to Mock Data Mode.")
            db = None
    else:
        print("Warning: Database not connected. Using in-memory mock data where possible.")

# ---- Routes ----
@app.get('/')
async def root():
    return {'message': 'Advanced Travel Platform (FastAPI)', 'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}

@app.get('/api/health')
async def health():
    return {'status': 'healthy', 'gemini': bool(gemini_client), 'db': bool(db is not None), 'timestamp': datetime.utcnow().isoformat()}

@app.post('/api/auth/register')
async def register(body: RegisterBody):
    if db is None:
        # Mock registration
        return {'access_token': 'mock_token', 'token_type': 'bearer', 'user': body.username, 'user_id': str(uuid4())}
    existing = await db.users.find_one({'$or': [{'email': body.email}, {'username': body.username}]})
    if existing:
        raise HTTPException(status_code=400, detail='Email or username already exists')
    doc = {
        'user_id': str(uuid4()),
        'username': body.username,
        'email': body.email,
        'full_name': body.full_name,
        'password': pwd_context.hash(body.password),
        'avatar': None,
        'created_at': datetime.utcnow(),
    }
    await db.users.insert_one(doc)
    token = create_token(doc['username'], doc['user_id'])
    return {'access_token': token, 'token_type': 'bearer', 'user': doc['username'], 'user_id': doc['user_id']}

@app.post('/api/auth/login')
async def login(body: LoginBody):
    if db is None:
        # Mock login for demo purpose when DB is down
        if body.email == 'demo@example.com' or True: # Allow anyone to login in fallback mode
             return {'access_token': 'mock_token', 'token_type': 'bearer', 'user': 'demo_user', 'user_id': 'mock_user_id'}

    user = await db.users.find_one({'email': body.email})
    if not user or not pwd_context.verify(body.password, user.get('password','')):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_token(user['username'], user['user_id'])
    return {'access_token': token, 'token_type': 'bearer', 'user': user['username'], 'user_id': user['user_id']}

@app.get('/api/auth/profile', response_model=ProfileOut)
async def profile(user=Depends(get_user_from_token)):
    if user.get('user_id') == 'mock_user_id':
         return ProfileOut(
            user_id='mock_user_id', username='demo_user', email='demo@example.com', full_name='Demo User', avatar=None, created_at=datetime.utcnow()
        )
    return ProfileOut(
        user_id=user['user_id'], username=user['username'], email=user['email'], full_name=user.get('full_name',''), avatar=user.get('avatar'), created_at=user['created_at']
    )

@app.put('/api/auth/profile', response_model=ProfileOut)
async def update_profile(body: ProfileUpdateBody, user=Depends(get_user_from_token)):
    if user.get('user_id') == 'mock_user_id':
         return ProfileOut(
            user_id='mock_user_id', username='demo_user', email=body.email or 'demo@example.com', full_name=body.full_name or 'Demo User', avatar=body.avatar, created_at=datetime.utcnow()
        )
    
    update_data = {}
    if body.full_name is not None:
        update_data['full_name'] = body.full_name
    if body.email is not None:
        # Check if email is taken
        if body.email != user.get('email'):
            existing = await db.users.find_one({'email': body.email})
            if existing:
                raise HTTPException(status_code=400, detail='Email is already in use')
        update_data['email'] = body.email
    if body.avatar is not None:
        update_data['avatar'] = body.avatar
        
    if update_data:
        await db.users.update_one({'user_id': user['user_id']}, {'$set': update_data})
        # Fetch updated user
        user = await db.users.find_one({'user_id': user['user_id']})
        
    return ProfileOut(
        user_id=user['user_id'], username=user['username'], email=user['email'], full_name=user.get('full_name',''), avatar=user.get('avatar'), created_at=user['created_at']
    )

@app.post('/api/auth/forgot-password')
async def forgot_password(body: ForgotPasswordReq):
    if db is None:
        return {'message': 'If an account exists, a password reset link will be sent.'}
        
    user = await db.users.find_one({'email': body.email})
    if not user:
        return {'message': 'If an account exists, a password reset link will be sent.'}
        
    payload = {
        'user_id': user['user_id'],
        'action': 'reset',
        'exp': int((datetime.utcnow() + timedelta(minutes=15)).timestamp())
    }
    reset_token = jwt.encode(payload, JWT_SECRET, algorithm=ALG)
    
    base_url = CORS_ORIGINS[0] if CORS_ORIGINS else "http://localhost:3000"
    reset_link = f"{base_url}/reset-password?token={reset_token}"
    
    html_content = f"""
    <h2>Password Reset Request</h2>
    <p>Hi {user.get('username', 'there')},</p>
    <p>You requested a password reset. Click the button below to reset your password. This link is valid for 15 minutes.</p>
    <br>
    <a href="{reset_link}" style="background-color: #0ea5e9; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
    <br><br>
    <p>If you didn't request this, you can safely ignore this email.</p>
    """
    
    await send_email_async(body.email, "Password Reset", html_content)
    return {'message': 'If an account exists, a password reset link will be sent.'}

@app.post('/api/auth/reset-password')
async def reset_password(body: ResetPasswordReq):
    if db is None:
        return {'message': 'Password has been reset successfully'}
        
    try:
        payload = jwt.decode(body.token, JWT_SECRET, algorithms=[ALG])
        if payload.get('action') != 'reset':
            raise HTTPException(status_code=400, detail='Invalid token content')
            
        user_id = payload.get('user_id')
        hashed_password = pwd_context.hash(body.new_password)
        
        res = await db.users.update_one({'user_id': user_id}, {'$set': {'password': hashed_password}})
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail='User not found')
            
        return {'message': 'Password has been reset successfully'}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='Reset token has expired')
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail='Invalid reset token')


@app.get('/api/chat/sessions')
async def list_sessions(user=Depends(get_user_from_token)):
    if db is None: return {'sessions': []}
    cursor = db.chat_sessions.find({'user_id': user['user_id']}, {'messages': {'$slice': 1}}).sort('updated_at', -1).limit(50)
    sessions = []
    async for s in cursor:
        sessions.append({'session_id': s['session_id'], 'updated_at': s.get('updated_at'), 'created_at': s.get('created_at')})
    return {'sessions': sessions}

@app.get('/api/chat/sessions/{session_id}')
async def get_session(session_id: str, user=Depends(get_user_from_token)):
    if db is None: return {'session_id': session_id, 'messages': [], 'created_at': None}
    s = await db.chat_sessions.find_one({'session_id': session_id, 'user_id': user['user_id']})
    if not s:
        return {'session_id': session_id, 'messages': [], 'created_at': None}
    return {'session_id': session_id, 'messages': s.get('messages', []), 'created_at': s.get('created_at'), 'updated_at': s.get('updated_at')}

@app.delete('/api/chat/sessions/{session_id}')
async def delete_session(session_id: str, user=Depends(get_user_from_token)):
    if db is None: return {'message': 'Deleted (Mock)'}
    await db.chat_sessions.delete_one({'session_id': session_id, 'user_id': user['user_id']})
    return {'message': f'Chat session {session_id} deleted successfully'}

@app.post('/api/chat', response_model=ChatOut)
async def chat(body: ChatBody, user=Depends(get_user_from_token)):
    session_id = body.session_id or f"session_{str(uuid4())[:8]}"
    # persist user message first
    await upsert_session_message(user_id=user['user_id'], session_id=session_id, role='user', content=body.message)

    if not gemini_client:
        # Save assistant fallback and return
        fallback = 'AI service is not configured. Please add a valid GEMINI_API_KEY to backend/.env.'
        await upsert_session_message(user_id=user['user_id'], session_id=session_id, role='assistant', content=fallback)
        return ChatOut(session_id=session_id, response=fallback, timestamp=datetime.utcnow())

    try:
        safety = [
            genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=genai_types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
            genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=genai_types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
        ]
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: gemini_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=body.message,
                config=genai_types.GenerateContentConfig(
                    system_instruction='You are a helpful AI travel assistant. Keep answers focused, clear, and travel-specific when possible.',
                    max_output_tokens=800,
                    temperature=0.7,
                    safety_settings=safety,
                )
            )
        )
        text = getattr(result, 'text', None) or 'I could not generate a response. Please try again.'
        await upsert_session_message(user_id=user['user_id'], session_id=session_id, role='assistant', content=text)
        return ChatOut(session_id=session_id, response=text, timestamp=datetime.utcnow())
    except Exception as e:
        import traceback
        traceback.print_exc()
        err = f'I am experiencing technical difficulties: {str(e)}'
        await upsert_session_message(user_id=user['user_id'], session_id=session_id, role='assistant', content=err)
        return ChatOut(session_id=session_id, response=err, timestamp=datetime.utcnow())

@app.post('/api/ai/recommendations')
async def ai_recommendations(prefs: RecReq, user=Depends(get_user_from_token)):
    prompt = (
        "Generate concise travel recommendations as bullet points based on these preferences: "
        + json.dumps(prefs.model_dump(exclude_none=True))
    )
    if not gemini_client:
        return {'recommendations': ['Enable GEMINI_API_KEY to get AI recommendations.']}
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: gemini_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=genai_types.GenerateContentConfig(max_output_tokens=600, temperature=0.5)
            )
        )
        text = getattr(result, 'text', '')
        lines = [l.strip('- ').strip() for l in text.split('\n') if l.strip()]
        return {'recommendations': lines[:10]}
    except Exception:
        return {'recommendations': ['Unable to generate recommendations at this time. Please try again later.']}

# ---- Virtual Tours API ----
@app.get('/api/virtual-tours')
async def get_virtual_tours(
    search: Optional[str] = Query(None),
    type: Optional[str] = Query(None, alias='type'),
    country: Optional[str] = Query(None),
    page: int = 1,
    limit: int = 12,
):
    try:
        if db is None: raise Exception("Use Mock")
        filters = {}
        if search:
            filters['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}},
                {'country': {'$regex': search, '$options': 'i'}},
            ]
        if type:
            filters['tour_type'] = type
        if country:
            filters['country'] = country

        skip = max(0, (page - 1) * limit)
        cursor = db.virtual_tours.find(filters).sort([('featured', -1), ('views', -1)]).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            results.append(fix_id(doc))
        total = await db.virtual_tours.count_documents(filters)
        return {
            'items': results,
            'page': page,
            'limit': limit,
            'total': total,
            'has_more': (skip + len(results)) < total
        }
    except Exception as e:
        print(f"Error serving virtual tours: {e}. Returning Mocks.")
        # Mock filtering
        results = MOCK_VIRTUAL_TOURS
        if search:
            s = search.lower()
            results = [t for t in results if s in t['name'].lower() or s in t.get('description','').lower()]
        if type:
            results = [t for t in results if t.get('tour_type') == type]
        if country:
            results = [t for t in results if t.get('country') == country]
        
        start = (page - 1) * limit
        end = start + limit
        return {
            'items': results[start:end],
            'page': page,
            'limit': limit,
            'total': len(results),
            'has_more': end < len(results)
        }

@app.get('/api/virtual-tours/featured')
async def get_featured_virtual_tours(limit: int = 6):
    try:
        if db is None: raise Exception("Use Mock")
        cursor = db.virtual_tours.find({'featured': True}).sort('name', 1).limit(int(limit))
        results = []
        async for doc in cursor:
            results.append(fix_id(doc))
        return results
    except Exception:
        return [t for t in MOCK_VIRTUAL_TOURS if t.get('featured')][:limit]

@app.get('/api/virtual-tours/trending')
async def get_trending_virtual_tours(limit: int = 6):
    if db is None:
        return sorted(MOCK_VIRTUAL_TOURS, key=lambda x: x.get('views', 0), reverse=True)[:limit]
    cursor = db.virtual_tours.find({}).sort('views', -1).limit(int(limit))
    results = []
    async for doc in cursor:
        results.append(fix_id(doc))
    return results

@app.post('/api/virtual-tours/{tour_id}/view')
async def add_view_virtual_tour(tour_id: str):
    if db is None: return {'message': 'viewed (mock)', 'tour_id': tour_id}
    res = await db.virtual_tours.update_one({'tour_id': tour_id}, {'$inc': {'views': 1}, '$set': {'last_viewed_at': datetime.utcnow().isoformat()}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail='Virtual tour not found')
    return {'message': 'viewed', 'tour_id': tour_id}

@app.get('/api/virtual-tours/types')
async def get_virtual_tour_types():
    if db is None:
         # Aggregate mock types
         types = {}
         for t in MOCK_VIRTUAL_TOURS:
             tt = t.get('tour_type')
             if tt: types[tt] = types.get(tt, 0) + 1
         return {'types': [{'type': k, 'count': v} for k,v in types.items()]}
    pipeline = [
        {'$group': {'_id': '$tour_type', 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ]
    agg = db.virtual_tours.aggregate(pipeline)
    types = []
    async for t in agg:
        types.append({'type': t['_id'], 'count': t['count']})
    return {'types': types}

@app.get('/api/virtual-tours/countries')
async def get_virtual_tour_countries():
    if db is None:
        return {'countries': sorted(list(set(t['country'] for t in MOCK_VIRTUAL_TOURS if t.get('country'))))}
    countries = await db.virtual_tours.distinct('country')
    countries.sort()
    return {'countries': countries}



# ---- Destinations API (New) ----
@app.get('/api/destinations')
async def get_destinations(
    search: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    activity: Optional[str] = Query(None),
    limit: int = 6
):
    try:
        if db is None: raise Exception("Use Mock")
        filters = {}
        if search:
            filters['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}},
                {'country': {'$regex': search, '$options': 'i'}},
            ]
        if country:
            filters['country'] = country
        if activity:
            filters['activities'] = activity
            
        if min_price is not None or max_price is not None:
            price_filter = {}
            if min_price is not None:
                price_filter['$gte'] = min_price
            if max_price is not None:
                price_filter['$lte'] = max_price
            filters['price'] = price_filter
            
        cursor = db.destinations.find(filters).limit(int(limit))
        results = []
        async for doc in cursor:
            results.append(fix_id(doc))
                
        return results
    except Exception as e:
        results = MOCK_DESTINATIONS
        if search:
            s = search.lower()
            results = [t for t in results if s in t['name'].lower() or s in t.get('description','').lower() or s in t.get('country','').lower()]
        if country:
            results = [t for t in results if t.get('country') == country]
        if activity:
            results = [t for t in results if activity in t.get('activities', [])]
        if min_price is not None:
            results = [t for t in results if t.get('price', float('inf')) >= min_price]
        if max_price is not None:
            results = [t for t in results if t.get('price', 0) <= max_price]

        return results[:limit]

@app.get('/api/destinations/featured')
async def get_featured_destinations(limit: int = 6):
    if db is None:
        return [d for d in MOCK_DESTINATIONS if d['featured']][:limit]
    cursor = db.destinations.find({'featured': True}).limit(int(limit))
    results = []
    async for doc in cursor:
        results.append(fix_id(doc))
    return results

@app.get('/api/destinations/countries')
async def get_destination_countries():
    if db is None:
        return sorted(list(set(d['country'] for d in MOCK_DESTINATIONS)))
    countries = await db.destinations.distinct('country')
    countries.sort()
    return sorted(countries)

@app.get('/api/destinations/activities')
async def get_destination_activities():
    if db is None:
        acts = set()
        for d in MOCK_DESTINATIONS:
            for a in d.get('activities', []):
                acts.add(a)
        return sorted(list(acts))
    # Use aggregation to get distinct activities
    pipeline = [
        {'$unwind': '$activities'},
        {'$group': {'_id': None, 'all_activities': {'$addToSet': '$activities'}}}
    ]
    result = await db.destinations.aggregate(pipeline).to_list(1)
    if result:
        return sorted(result[0]['all_activities'])
    return []

@app.get('/api/destinations/{destination_id}')
async def get_destination(destination_id: str):
    if db is None:
        d = next((x for x in MOCK_DESTINATIONS if x['destination_id'] == destination_id), None)
        if not d: raise HTTPException(status_code=404, detail='Destination not found')
        return d
    d = await db.destinations.find_one({'destination_id': destination_id})
    if not d:
        raise HTTPException(status_code=404, detail='Destination not found')
    return fix_id(d)

@app.post('/api/destinations')
async def create_destination(body: Destination):
    doc = body.dict()
    if db is None:
        MOCK_DESTINATIONS.append(doc)
        return body
    
    # Check for duplicate ID
    existing = await db.destinations.find_one({'destination_id': body.destination_id})
    if existing:
        raise HTTPException(status_code=400, detail='Destination ID already exists')
    
    await db.destinations.insert_one(doc)
    return fix_id(doc)

# ---- Favorites (auth required) ----
@app.get('/api/virtual-tours/favorites')
async def list_favorites(user=Depends(get_user_from_token)):
    if db is None: return {'items': []}
    fav_cursor = db.favorites.find({'user_id': user['user_id']})
    fav_ids = []
    async for f in fav_cursor:
        fav_ids.append(f['tour_id'])
    if not fav_ids:
        return {'items': []}
    cursor = db.virtual_tours.find({'tour_id': {'$in': fav_ids}})
    items = []
    async for t in cursor:
        items.append(fix_id(t))
    return {'items': items}

@app.post('/api/virtual-tours/{tour_id}/favorite')
async def favorite_tour(tour_id: str, user=Depends(get_user_from_token)):
    if db is None: return {'message': 'Favorited (Mock)', 'tour_id': tour_id}
    tour = await db.virtual_tours.find_one({'tour_id': tour_id})
    if not tour:
        raise HTTPException(status_code=404, detail='Virtual tour not found')
    try:
        await db.favorites.update_one(
            {'user_id': user['user_id'], 'tour_id': tour_id},
            {'$setOnInsert': {'created_at': datetime.utcnow().isoformat()}},
            upsert=True
        )
        return {'message': 'Favorited', 'tour_id': tour_id}
    except Exception:
        return {'message': 'Favorited', 'tour_id': tour_id}

@app.delete('/api/virtual-tours/{tour_id}/favorite')
async def unfavorite_tour(tour_id: str, user=Depends(get_user_from_token)):
    if db is None: return {'message': 'Unfavorited (Mock)', 'tour_id': tour_id}
    await db.favorites.delete_one({'user_id': user['user_id'], 'tour_id': tour_id})
    return {'message': 'Unfavorited', 'tour_id': tour_id}

@app.get('/api/virtual-tours/{tour_id}')
async def get_virtual_tour(tour_id: str):
    try:
        if db is None: raise Exception("Use Mock")
        tour = await db.virtual_tours.find_one({'tour_id': tour_id})
        if not tour:
            raise HTTPException(status_code=404, detail='Virtual tour not found')
        return fix_id(tour)
    except Exception:
        t = next((x for x in MOCK_VIRTUAL_TOURS if x['tour_id'] == tour_id), None)
        if not t: raise HTTPException(status_code=404, detail='Virtual tour not found')
        return t

# ---- AI Narration for a tour (auth required) ----
@app.post('/api/virtual-tours/{tour_id}/narrate')
async def narrate_tour(tour_id: str, req: NarrationReq, user=Depends(get_user_from_token)):
    if db is None:
        tour = next((x for x in MOCK_VIRTUAL_TOURS if x['tour_id'] == tour_id), None)
    else:
        tour = await db.virtual_tours.find_one({'tour_id': tour_id})
    
    if not tour:
        raise HTTPException(status_code=404, detail='Virtual tour not found')

    prompt = (
        f"Create a {req.duration_hint} narration in {req.language} with a {req.voice_style} tone and {req.pace} pace for this 360° virtual tour. "
        f"Keep it engaging and travel-guide-like. Include 2-4 highlights if available, and paint a vivid picture for listeners.\n\n"
        f"Tour Name: {tour.get('name')}\n"
        f"Country: {tour.get('country')}\n"
        f"Duration: {tour.get('duration')}\n"
        f"Type: {tour.get('tour_type')}\n"
        f"Description: {tour.get('description')}\n"
        f"Features: {', '.join(tour.get('features', []))}\n"
        f"Highlights: {json.dumps(tour.get('highlights', []))}\n"
    )

    if not gemini_client:
        return {'narration': 'AI service is not configured. Please add GEMINI_API_KEY to backend/.env.'}

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: gemini_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=genai_types.GenerateContentConfig(max_output_tokens=500, temperature=0.6)
            )
        )
        narration = getattr(result, 'text', '') or 'Unable to generate narration at this time.'
        return {'narration': narration}
    except Exception:
        return {'narration': 'We are experiencing technical difficulties generating narration. Please try again later.'}

# ---- Bookings API ----
# ---- Email Utils ----
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
ADMIN_EMAIL = 'prajwalps2604@gmail.com'

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

async def send_email_async(to_email: str, subject: str, html_content: str):
    # Re-fetch env vars in case they changed (though usually requires restart)
    current_user = os.environ.get('EMAIL_USER')
    current_pass = os.environ.get('EMAIL_PASS')
    
    if not current_user or not current_pass:
        print(f"\n[MOCK EMAIL - MISSING CONFIG] To: {to_email}\nSubject: {subject}\nContent:\n{html_content}\n")
        print("Tip: Add EMAIL_USER and EMAIL_PASS to .env and restart the server.")
        return

    print(f"Attempting to send email to {to_email} from {current_user}...")
    try:
        # Run synchronous SMTP in a thread
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send_email_sync, to_email, subject, html_content, current_user, current_pass)
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"CRITICAL ERROR sending email: {e}")
        print("Falling back to console print so you can still test:")
        print(f"\n[EMAIL FAILED - FALLBACK] To: {to_email}\nSubject: {subject}\nContent:\n{html_content}\n")

def _send_email_sync(to_email, subject, html_content, user_email, user_pass):
    try:
        msg = MIMEMultipart()
        msg['From'] = user_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user_email, user_pass)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        raise e

# ---- Bookings API ----
@app.post('/api/bookings')
async def create_booking(body: BookingReq, request: Request, user=Depends(get_user_from_token)):
    if db is None:
        # Mock behavior with email print
        booking_id = str(uuid4())
        print(f"[MOCK] Booking created: {booking_id}. Email would be sent to {ADMIN_EMAIL}")
        return {'booking_id': booking_id, **body.dict(), 'status': 'pending', 'created_at': datetime.utcnow()}
    
    # Verify destination exists
    destination = await db.destinations.find_one({'destination_id': body.destination_id})
    if not destination:
        raise HTTPException(status_code=404, detail='Destination not found')

    booking_id = str(uuid4())
    booking = {
        'booking_id': booking_id,
        'user_id': user['user_id'],
        'user_email': user.get('email', 'Unknown'),
        'user_name': user.get('username', 'Unknown'),
        'destination_id': body.destination_id,
        'destination_name': destination['name'],
        'destination_image': destination['images'][0] if destination.get('images') else None,
        'check_in_date': body.check_in_date,
        'check_out_date': body.check_out_date,
        'guests': body.guests,
        'total_price': body.total_price,
        'status': 'pending', # Default to pending
        'created_at': datetime.utcnow()
    }
    await db.bookings.insert_one(booking)

    # Generate confirmation token (simple JWT)
    token_payload = {'booking_id': booking_id, 'action': 'confirm'}
    confirm_token = jwt.encode(token_payload, JWT_SECRET, algorithm=ALG)
    
    token_payload_reject = {'booking_id': booking_id, 'action': 'reject'}
    reject_token = jwt.encode(token_payload_reject, JWT_SECRET, algorithm=ALG)

    base_url = str(request.base_url).rstrip('/')
    confirm_link = f"{base_url}/api/bookings/confirm?token={confirm_token}"
    reject_link = f"{base_url}/api/bookings/reject?token={reject_token}"

    # Email Content
    html_content = f"""
    <h2>New Booking Request</h2>
    <p><strong>User:</strong> {user.get('username')} ({user.get('email')})</p>
    <p><strong>Destination:</strong> {destination['name']}</p>
    <p><strong>Check-in:</strong> {body.check_in_date}</p>
    <p><strong>Check-out:</strong> {body.check_out_date}</p>
    <p><strong>Guests:</strong> {body.guests}</p>
    <p><strong>Total Price:</strong> ${body.total_price}</p>
    <br>
    <p>Please confirm or reject this booking:</p>
    <a href="{confirm_link}" style="background-color: green; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Confirm Booking</a>
    &nbsp;
    <a href="{reject_link}" style="background-color: red; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reject Booking</a>
    """
    
    # Send Email to Admin
    await send_email_async(ADMIN_EMAIL, f"New Booking Request: {destination['name']}", html_content)

    return fix_id(booking)

@app.get('/api/bookings/confirm')
async def confirm_booking_endpoint(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALG])
        booking_id = payload.get('booking_id')
        if payload.get('action') != 'confirm':
            raise ValueError("Invalid token action")
            
        if db is None:
             return HTMLResponse(content="<h1>Mock: Booking Confirmed</h1>")

        result = await db.bookings.update_one(
            {'booking_id': booking_id},
            {'$set': {'status': 'confirmed'}}
        )
        
        if result.matched_count == 0:
            return HTMLResponse(content="<h1>Error: Booking not found</h1>", status_code=404)
            
        # Optional: Notify user (implementation omitted for brevity)
        
        return HTMLResponse(content="<h1 style='color: green;'>Booking Confirmed Successfully!</h1><p>You can close this window.</p>")
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=400)

@app.get('/api/bookings/reject')
async def reject_booking_endpoint(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALG])
        booking_id = payload.get('booking_id')
        if payload.get('action') != 'reject':
             raise ValueError("Invalid token action")

        if db is None:
             return HTMLResponse(content="<h1>Mock: Booking Rejected</h1>")

        result = await db.bookings.update_one(
            {'booking_id': booking_id},
            {'$set': {'status': 'cancelled'}}
        )

        if result.matched_count == 0:
            return HTMLResponse(content="<h1>Error: Booking not found</h1>", status_code=404)

        return HTMLResponse(content="<h1 style='color: red;'>Booking Rejected</h1><p>The booking has been marked as cancelled.</p>")
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=400)

@app.get('/api/bookings')
async def get_user_bookings(user=Depends(get_user_from_token)):
    if db is None: return []

    # Auto-complete past bookings
    now_str = datetime.utcnow().isoformat()
    # Find bookings that are 'confirmed' and have check_out_date < now
    # Note: This simple string comparison relies on ISO format dates. 
    # If using just YYYY-MM-DD, verify it works or use datetime objects.
    # For now, we assume simple string compare works for YYYY-MM-DD if format is consistent.
    
    await db.bookings.update_many(
        {
            'user_id': user['user_id'],
            'status': 'confirmed',
            'check_out_date': {'$lt': now_str}
        },
        {'$set': {'status': 'completed'}}
    )

    cursor = db.bookings.find({'user_id': user['user_id']}).sort('created_at', -1)
    bookings = []
    async for doc in cursor:
        bookings.append(fix_id(doc))
    return bookings

@app.delete('/api/bookings/{booking_id}')
async def cancel_booking(booking_id: str, user=Depends(get_user_from_token)):
    if db is None: return {'message': 'Booking cancelled (mock)'}
    result = await db.bookings.delete_one({'booking_id': booking_id, 'user_id': user['user_id']})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Booking not found')
    return {'message': 'Booking cancelled successfully'}

# ---- Reviews API ----
@app.post('/api/reviews')
async def create_review(body: ReviewReq, user=Depends(get_user_from_token)):
    if db is None: return {'message': 'Review added (mock)'}
    
    # Verify destination
    destination = await db.destinations.find_one({'destination_id': body.destination_id})
    if not destination:
         raise HTTPException(status_code=404, detail='Destination not found')

    review = {
        'review_id': str(uuid4()),
        'user_id': user['user_id'],
        'username': user['username'],
        'destination_id': body.destination_id,
        'rating': body.rating,
        'comment': body.comment,
        'created_at': datetime.utcnow()
    }
    await db.reviews.insert_one(review)
    return fix_id(review)

@app.get('/api/reviews/{destination_id}')
async def get_destination_reviews(destination_id: str):
    if db is None: return []
    cursor = db.reviews.find({'destination_id': destination_id}).sort('created_at', -1)
    reviews = []
    async for doc in cursor:
        reviews.append(fix_id(doc))
    return reviews

@app.delete('/api/reviews/{review_id}')
async def delete_review(review_id: str, user=Depends(get_user_from_token)):
    if db is None: return {'message': 'Deleted (mock)'}
    # Allow deletion if user owns it OR if user is admin (logic for admin not implemented, assuming owner only)
    result = await db.reviews.delete_one({'review_id': review_id, 'user_id': user['user_id']})
    if result.deleted_count == 0:
         raise HTTPException(status_code=404, detail='Review not found or permission denied')
    return {'message': 'Review deleted successfully'}

# ---- Run (handled by supervisor) ----
# Do not add uvicorn.run here.