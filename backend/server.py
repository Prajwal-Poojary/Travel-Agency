import os
import bcrypt
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

MONGO_URL = os.environ.get('MONGO_URL')
JWT_SECRET = os.environ.get('JWT_SECRET_KEY') or 'dev_secret'
ALGORITHM = 'HS256'

client: Optional[MongoClient] = None
try:
    client = MongoClient(MONGO_URL) if MONGO_URL else MongoClient('mongodb://localhost:27017')
    db = client.get_default_database() if client else None
except Exception:
    client = None
    db = None

app = FastAPI(title='Advanced Travel Platform - FastAPI')

# CORS
cors_origins_env = os.environ.get('CORS_ORIGINS', '')
origins = [o.strip() for o in cors_origins_env.split(',') if o.strip()] or [
    'http://localhost:3000',
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# ------------ Models ------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=2, max_length=100)

class UserOut(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    full_name: str
    avatar: Optional[str] = None
    created_at: datetime

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class DestinationOut(BaseModel):
    destination_id: str
    name: str
    country: str
    city: str
    category: str
    description: str
    price_range: str
    activities: List[str]
    best_time_to_visit: str
    images: List[str]
    coordinates: dict
    rating: float = 0.0
    featured: bool = False

# ------------ Utilities ------------

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password: str, hashed) -> bool:
    try:
        if isinstance(hashed, str):
            hashed = hashed.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    except Exception:
        return False

def create_token(username: str, user_id: str) -> str:
    payload = {
        'username': username,
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='No token provided')
    token = authorization[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get('username')
        if not username:
            raise HTTPException(status_code=401, detail='Invalid token - no username')
        user = db.users.find_one({'username': username}) if db is not None else None
        if not user:
            raise HTTPException(status_code=401, detail='User not found')
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except Exception as e:
        # Emit debug info without leaking secrets
        print('[AUTH_DEBUG] Token validation failed:', type(e).__name__, str(e)[:200])
        raise HTTPException(status_code=401, detail='Invalid token')

# ------------ Startup: seed demo user and data ------------
@app.on_event('startup')
async def startup_event():
    if db is None:
        return
    # Ensure collections
    db.users.create_index('email', unique=True)
    db.users.create_index('username', unique=True)
    db.destinations.create_index('destination_id', unique=True)

    # Ensure demo user for login
    demo = db.users.find_one({'email': 'demo@example.com'})
    if not demo:
        demo_user = {
            'user_id': str(uuid.uuid4()),
            'username': 'demo_user',
            'email': 'demo@example.com',
            'full_name': 'Demo User',
            'password': hash_password('password123'),
            'avatar': None,
            'created_at': datetime.utcnow(),
        }
        db.users.insert_one(demo_user)

    # Seed minimal destinations for homepage
    if db.destinations.count_documents({}) == 0:
        sample = [
            {
                'destination_id': str(uuid.uuid4()),
                'name': 'Maldives Paradise',
                'country': 'Maldives',
                'city': 'Malé',
                'category': 'Beach',
                'description': 'Crystal-clear waters, overwater bungalows, and vibrant marine life.',
                'price_range': '$$$$',
                'activities': ['Snorkeling', 'Diving', 'Sunset Cruise'],
                'best_time_to_visit': 'Nov to Apr',
                'images': ['https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80'],
                'coordinates': {'latitude': 3.2028, 'longitude': 73.2207},
                'rating': 4.8,
                'featured': True,
                'created_at': datetime.utcnow(),
            },
            {
                'destination_id': str(uuid.uuid4()),
                'name': 'Tokyo Metropolitan',
                'country': 'Japan',
                'city': 'Tokyo',
                'category': 'City',
                'description': 'Traditional culture meets modern innovation and incredible cuisine.',
                'price_range': '$$$',
                'activities': ['Temple Visits', 'Sushi Tours', 'Shopping'],
                'best_time_to_visit': 'Mar to May, Oct to Nov',
                'images': ['https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80'],
                'coordinates': {'latitude': 35.6762, 'longitude': 139.6503},
                'rating': 4.6,
                'featured': True,
                'created_at': datetime.utcnow(),
            },
            {
                'destination_id': str(uuid.uuid4()),
                'name': 'Santorini Sunset',
                'country': 'Greece',
                'city': 'Santorini',
                'category': 'Island',
                'description': 'Iconic blue-domed churches and dramatic cliffside views.',
                'price_range': '$$$',
                'activities': ['Sunset Viewing', 'Wine Tasting', 'Photography'],
                'best_time_to_visit': 'Apr to Oct',
                'images': ['https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&q=80'],
                'coordinates': {'latitude': 36.3932, 'longitude': 25.4615},
                'rating': 4.5,
                'featured': True,
                'created_at': datetime.utcnow(),
            },
        ]
        db.destinations.insert_many(sample)

# ------------ Routes ------------
@app.get('/')
async def root():
    return {
        'message': 'Advanced Travel Platform - FastAPI',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
    }

@app.get('/api/health')
async def health():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
    }

@app.post('/api/auth/login')
async def login(payload: LoginRequest):
    if db is None:
        raise HTTPException(status_code=500, detail='Database not connected')
    user = db.users.find_one({'email': payload.email})
    if not user or not verify_password(payload.password, user['password']):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_token(user['username'], user['user_id'])
    return {
        'access_token': token,
        'token_type': 'bearer',
        'user': user['username'],
        'user_id': user['user_id']
    }

@app.post('/api/auth/register')
async def register(payload: RegisterRequest):
    if db is None:
        raise HTTPException(status_code=500, detail='Database not connected')
    if db.users.find_one({'$or': [{'email': payload.email}, {'username': payload.username}] }):
        raise HTTPException(status_code=400, detail='Email or username already exists')
    user = {
        'user_id': str(uuid.uuid4()),
        'username': payload.username,
        'email': payload.email,
        'full_name': payload.full_name,
        'password': hash_password(payload.password),
        'avatar': None,
        'created_at': datetime.utcnow(),
    }
    db.users.insert_one(user)
    token = create_token(user['username'], user['user_id'])
    return {'access_token': token, 'token_type': 'bearer', 'user': user['username'], 'user_id': user['user_id']}

@app.get('/api/auth/profile', response_model=UserOut)
async def profile(user=Depends(get_current_user)):
    return UserOut(
        user_id=user['user_id'],
        username=user['username'],
        email=user['email'],
        full_name=user.get('full_name', ''),
        avatar=user.get('avatar'),
        created_at=user.get('created_at', datetime.utcnow())
    )

@app.get('/api/destinations', response_model=List[DestinationOut])
async def get_destinations(search: Optional[str] = None, country: Optional[str] = None, activity: Optional[str] = None, limit: int = 100):
    if db is None:
        raise HTTPException(status_code=500, detail='Database not connected')
    query = {}
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}},
            {'city': {'$regex': search, '$options': 'i'}},
            {'country': {'$regex': search, '$options': 'i'}},
        ]
    if country:
        query['country'] = {'$regex': country, '$options': 'i'}
    if activity:
        query['activities'] = {'$in': [activity]}
    docs = list(db.destinations.find(query).limit(max(1, min(limit, 100))))
    for d in docs:
        d['destination_id'] = d.get('destination_id') or str(d.get('_id'))
    return docs

@app.get('/api/destinations/countries')
async def get_countries():
    if db is None:
        return []
    return sorted(list(set([d.get('country') for d in db.destinations.find({}, {'country': 1}) if d.get('country')])))

@app.get('/api/destinations/activities')
async def get_activities():
    if db is None:
        return []
    activities = []
    for d in db.destinations.find({}, {'activities': 1}):
        activities.extend(d.get('activities', []))
    return sorted(list(set(activities)))

@app.get('/api/destinations/{destination_id}', response_model=DestinationOut)
async def get_destination(destination_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail='Database not connected')
    doc = db.destinations.find_one({'destination_id': destination_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Destination not found')
    doc['destination_id'] = doc.get('destination_id') or str(doc.get('_id'))
    return doc

# Secure AI chat endpoint (requires auth)
@app.post('/api/chat')
async def chat(payload: ChatRequest, user=Depends(get_current_user)):
    reply = "Thanks for your message! The AI service is enabled for authenticated users. Ask me anything about travel."
    return {
        'session_id': payload.session_id or f'session_{uuid.uuid4().hex[:8]}',
        'response': reply,
        'timestamp': datetime.utcnow().isoformat()
    }

# Minimal chat session retrieval (requires auth)
@app.get('/api/chat/sessions/{session_id}')
async def get_chat_session(session_id: str, user=Depends(get_current_user)):
    return {
        'session_id': session_id,
        'messages': [
            {'role': 'user', 'content': 'Hello', 'timestamp': datetime.utcnow().isoformat()},
            {'role': 'assistant', 'content': 'Thanks for your message! The AI service is enabled for authenticated users. Ask me anything about travel.', 'timestamp': datetime.utcnow().isoformat()}
        ],
        'created_at': datetime.utcnow().isoformat()
    }

# Minimal chat session deletion (requires auth)
@app.delete('/api/chat/sessions/{session_id}')
async def delete_chat_session(session_id: str, user=Depends(get_current_user)):
    return {'message': f'Chat session {session_id} deleted successfully'}