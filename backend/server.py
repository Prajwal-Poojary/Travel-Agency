import os
import uuid
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import DuplicateKeyError

# --- Environment variables ---
# Load .env explicitly to ensure supervisor-provided environment matches file
from dotenv import load_dotenv
from os.path import dirname, join
load_dotenv(join(dirname(__file__), '.env'))

MONGO_URL = os.environ.get('MONGO_URL')
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'dev_secret')
CORS_ORIGINS = [o.strip() for o in (os.environ.get('CORS_ORIGINS') or '').split(',') if o.strip()]

if not MONGO_URL:
    raise RuntimeError('MONGO_URL is not set. Check backend/.env')

# --- Database setup ---
client = MongoClient(MONGO_URL, maxPoolSize=10)
# Use default database from URI (works when DB name is included)
try:
    db = client.get_default_database()
except Exception:
    # Fallback parse last path segment
    _db_name = None
    try:
        _db_name = MONGO_URL.split('/')[-1].split('?')[0]
    except Exception:
        pass
    if not _db_name:
        raise RuntimeError('Could not determine database name from MONGO_URL')
    db = client[_db_name]

# Ensure indexes & seed data

def ensure_indexes_and_seed():
    # Users
    db.users.create_index([('email', ASCENDING)], unique=True)
    db.users.create_index([('username', ASCENDING)], unique=True)

    # Destinations
    db.destinations.create_index([('destination_id', ASCENDING)], unique=True)

    # Virtual Tours
    db.virtual_tours.create_index([('tour_id', ASCENDING)], unique=True)
    db.virtual_tours.create_index([('tour_type', ASCENDING)])
    db.virtual_tours.create_index([('featured', ASCENDING)])
    db.virtual_tours.create_index([('active', ASCENDING)])
    db.virtual_tours.create_index([('name', TEXT), ('description', TEXT), ('city', TEXT), ('country', TEXT), ('tags', TEXT)], name='vt_text_idx')

    # Seed demo user
    if db.users.count_documents({'email': 'demo@example.com'}) == 0:
        db.users.insert_one({
            'user_id': str(uuid.uuid4()),
            'username': 'demo_user',
            'email': 'demo@example.com',
            'full_name': 'Demo User',
            'password': bcrypt.hashpw('password123'.encode(), bcrypt.gensalt()).decode(),
            'avatar': None,
            'created_at': datetime.utcnow()
        })

    # Seed some destinations if empty
    if db.destinations.count_documents({}) == 0:
        db.destinations.insert_many([
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
            }
        ])

    # Seed virtual tours if empty
    if db.virtual_tours.count_documents({}) == 0:
        common_features = ['360° View', 'Audio Guide', 'Landmarks', 'Cultural Insights']
        db.virtual_tours.insert_many([
            {
                'tour_id': str(uuid.uuid4()),
                'name': 'Tokyo 360° City Tour',
                'description': 'Explore the bustling streets of Tokyo in an immersive 360° experience.',
                'country': 'Japan',
                'city': 'Tokyo',
                'tour_type': '360_video',
                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'thumbnail': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80',
                'duration': '5:00',
                'featured': True,
                'views': 0,
                'rating': 4.7,
                'features': common_features,
                'highlights': [
                    {'time': '0:30', 'title': 'Shibuya Crossing', 'description': 'World-famous pedestrian scramble.'},
                    {'time': '2:10', 'title': 'Tokyo Tower Views', 'description': 'Panoramic skyline vistas.'}
                ],
                'interactive_elements': [
                    {'time': '1:20', 'type': 'hotspot', 'info': 'Tap to learn about Shinto shrines'}
                ],
                'coordinates': {'latitude': 35.6762, 'longitude': 139.6503},
                'destination_id': None,
                'tags': ['city', 'asia', 'nightlife'],
                'language': 'English',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'active': True
            },
            {
                'tour_id': str(uuid.uuid4()),
                'name': 'Santorini Cliffside Walk',
                'description': 'Stroll through Oia with breathtaking caldera views in 360°.',
                'country': 'Greece',
                'city': 'Oia',
                'tour_type': 'interactive_360',
                'video_url': 'https://www.youtube.com/watch?v=oHg5SJYRHA0',
                'thumbnail': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&q=80',
                'duration': '6:30',
                'featured': True,
                'views': 0,
                'rating': 4.6,
                'features': common_features,
                'highlights': [
                    {'time': '1:00', 'title': 'Blue Domes', 'description': 'Iconic architecture.'}
                ],
                'interactive_elements': [
                    {'time': '2:30', 'type': 'navigation', 'info': 'Jump to Amoudi Bay'}
                ],
                'coordinates': {'latitude': 36.3932, 'longitude': 25.4615},
                'destination_id': None,
                'tags': ['island', 'europe', 'sunset'],
                'language': 'English',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'active': True
            }
        ])

ensure_indexes_and_seed()

# --- JWT helpers ---

def create_token(username: str, user_id: str) -> str:
    payload = {
        'username': username,
        'user_id': user_id,
        'iat': int(datetime.utcnow().timestamp()),
        'exp': int((datetime.utcnow() + timedelta(days=30)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='No token provided')
    token = authorization[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = db.users.find_one({'username': payload.get('username')})
        if user is None:
            raise HTTPException(status_code=401, detail='User not found')
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail='Invalid token')

# --- Pydantic models (minimal) ---

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str

class BookingRequest(BaseModel):
    destination_id: str
    check_in_date: str
    check_out_date: str
    guests: int
    special_requests: Optional[str] = None

# --- FastAPI app ---
app = FastAPI(default_response_class=ORJSONResponse)

# Compression for large JSON responses
app.add_middleware(GZipMiddleware, minimum_size=500)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Health
@app.get('/api/health')
def health():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}

# Auth
@app.post('/api/auth/login')
def login(data: LoginRequest):
    user = db.users.find_one({'email': data.email})
    if not user:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    if not bcrypt.checkpw(data.password.encode(), user['password'].encode()):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_token(user['username'], user['user_id'])
    return {'access_token': token, 'token_type': 'bearer', 'user': user['username'], 'user_id': user['user_id']}

@app.post('/api/auth/register')
def register(data: RegisterRequest):
    try:
        doc = {
            'user_id': str(uuid.uuid4()),
            'username': data.username,
            'email': data.email,
            'full_name': data.full_name,
            'password': bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode(),
            'avatar': None,
            'created_at': datetime.utcnow(),
        }
        db.users.insert_one(doc)
        token = create_token(doc['username'], doc['user_id'])
        return {'access_token': token, 'token_type': 'bearer', 'user': doc['username'], 'user_id': doc['user_id']}
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail='Email or username already exists')

@app.get('/api/auth/profile')
def profile(user=Depends(get_current_user)):
    return {
        'user_id': user['user_id'],
        'username': user['username'],
        'email': user['email'],
        'full_name': user.get('full_name') or '',
        'avatar': user.get('avatar'),
        'created_at': user.get('created_at'),
    }

# Destinations (public)
@app.get('/api/destinations')
def get_destinations(search: Optional[str] = None, country: Optional[str] = None, activity: Optional[str] = None, limit: int = 100):
    limit = max(1, min(limit, 100))
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
    docs = list(db.destinations.find(query).limit(limit))
    for d in docs:
        d['destination_id'] = d.get('destination_id') or str(d.get('_id'))
        d.pop('_id', None)
    return docs

@app.get('/api/destinations/countries')
def get_countries():
    countries = sorted({d['country'] for d in db.destinations.find({}, {'country': 1}) if d.get('country')})
    return countries

@app.get('/api/destinations/activities')
def get_activities():
    activities = set()
    for d in db.destinations.find({}, {'activities': 1}):
        for a in d.get('activities', []):
            activities.add(a)
    return sorted(list(activities))

@app.get('/api/destinations/{destination_id}')
def get_destination(destination_id: str):
    doc = db.destinations.find_one({'destination_id': destination_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Destination not found')
    doc['destination_id'] = doc.get('destination_id') or str(doc.get('_id'))
    doc.pop('_id', None)
    return doc

# AI Chat (secured)
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@app.post('/api/chat')
def chat(data: ChatRequest, user=Depends(get_current_user)):
    reply = 'Thanks for your message! The AI service is enabled for authenticated users. Ask me anything about travel.'
    return {'session_id': data.session_id or f"session_{uuid.uuid4().hex[:8]}", 'response': reply, 'timestamp': datetime.utcnow().isoformat()}

@app.get('/api/chat/sessions/{session_id}')
def get_chat_session(session_id: str, user=Depends(get_current_user)):
    return {
        'session_id': session_id,
        'messages': [
            {'role': 'user', 'content': 'Hello', 'timestamp': datetime.utcnow().isoformat()},
            {'role': 'assistant', 'content': 'Thanks for your message! The AI service is enabled for authenticated users. Ask me anything about travel.', 'timestamp': datetime.utcnow().isoformat()},
        ],
        'created_at': datetime.utcnow().isoformat()
    }

# Virtual Tours (public)
@app.get('/api/virtual-tours')
def get_virtual_tours(search: Optional[str] = None, country: Optional[str] = None, tour_type: Optional[str] = None, featured_only: Optional[bool] = None, limit: int = 50, skip: int = 0, response: Response = None):
    limit = max(1, min(limit, 100))
    skip = max(0, skip)
    query = {'active': True}
    if search:
        # Prefer text search when index exists
        try:
            query['$text'] = {'$search': search}
        except Exception:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}},
                {'city': {'$regex': search, '$options': 'i'}},
                {'country': {'$regex': search, '$options': 'i'}},
                {'tags': {'$in': [search]}}
            ]
    if country:
        query['country'] = {'$regex': country, '$options': 'i'}
    if tour_type:
        query['tour_type'] = tour_type
    if featured_only is True or (isinstance(featured_only, str) and featured_only.lower() == 'true'):
        query['featured'] = True
    docs = list(db.virtual_tours.find(query).sort([('featured', DESCENDING), ('views', DESCENDING), ('created_at', DESCENDING)]).skip(skip).limit(limit))
    for d in docs:
        d['tour_id'] = d.get('tour_id') or str(d.get('_id'))
        d.pop('_id', None)
    return docs

@app.get('/api/virtual-tours/featured')
def get_featured_virtual_tours(limit: int = 6):
    limit = max(1, min(limit, 20))
    docs = list(db.virtual_tours.find({'featured': True, 'active': True}).sort([('views', DESCENDING), ('created_at', DESCENDING)]).limit(limit))
    for d in docs:
        d['tour_id'] = d.get('tour_id') or str(d.get('_id'))
        d.pop('_id', None)
    return docs

@app.get('/api/virtual-tours/types')
def get_virtual_tour_types():
    pipeline = [
        {'$match': {'active': True}},
        {'$group': {'_id': '$tour_type', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    types = list(db.virtual_tours.aggregate(pipeline))
    return [
        {'type': t['_id'], 'count': t['count'], 'label': (t['_id'] or '').replace('_', ' ').title()}
        for t in types
    ]

@app.get('/api/virtual-tours/countries')
def get_virtual_tour_countries():
    countries = db.virtual_tours.distinct('country', {'active': True})
    return countries

@app.get('/api/virtual-tours/{tour_id}')
def get_virtual_tour(tour_id: str):
    doc = db.virtual_tours.find_one({'tour_id': tour_id, 'active': True})
    if not doc:
        raise HTTPException(status_code=404, detail='Virtual tour not found')
    # increment views
    db.virtual_tours.update_one({'tour_id': tour_id}, {'$inc': {'views': 1}})
    doc['tour_id'] = doc.get('tour_id') or str(doc.get('_id'))
    doc.pop('_id', None)
    return doc