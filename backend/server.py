import os
import re
import json
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, Header, Request, Query
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
    allow_origins=["*"],
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

class ProfileOut(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: str = ''
    avatar: Optional[str] = None
    created_at: datetime

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
    activities: List[str]
    featured: bool


class BookingReq(BaseModel):
    destination_id: str
    date: str
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
        'thumbnail': 'https://i.ytimg.com/vi/6kAqQWBH6V0/hqdefault.jpg',
        'video_url': 'https://www.youtube.com/watch?v=6kAqQWBH6V0',
        'description': 'Experience the neon-lit streets of Shinjuku and Shibuya in fully immersive 360°.',
        'features': ['360° View', 'City Walk', 'Nightlife'],
        'featured': True,
        'views': 120,
        'highlights': [
            {'time': '00:45', 'title': 'Shinjuku Crossing', 'description': 'Bustling intersection views'},
            {'time': '05:10', 'title': 'Golden Gai', 'description': 'Cozy alleys and bars'},
        ],
        'interactive_elements': [
            {'info': 'Look left at 02:10 to see Godzilla Head on Hotel Gracery'},
        ]
    },
    {
        'tour_id': '2',
        'name': 'Santorini Cliffside 360°',
        'country': 'Greece',
        'duration': '9:03',
        'tour_type': 'drone_360',
        'thumbnail': 'https://i.ytimg.com/vi/m2QK_wC9mE8/hqdefault.jpg',
        'video_url': 'https://www.youtube.com/watch?v=m2QK_wC9mE8',
        'description': 'A breathtaking aerial 360° tour of Santorini’s blue domes and caldera views.',
        'features': ['Drone 360', 'Coastline', 'Sunset'],
        'featured': True,
        'views': 85,
        'highlights': [
            {'time': '01:40', 'title': 'Oia Blue Domes', 'description': 'Iconic rooftops at golden hour'},
        ],
    },
    {
        'tour_id': '3',
        'name': 'Machu Picchu Interactive Tour',
        'country': 'Peru',
        'duration': '14:22',
        'tour_type': 'interactive_360',
        'thumbnail': 'https://i.ytimg.com/vi/2m8uRkJ8A_4/hqdefault.jpg',
        'video_url': 'https://www.youtube.com/watch?v=2m8uRkJ8A_4',
        'description': 'Explore the ancient citadel with points-of-interest overlays and an audio guide.',
        'features': ['Interactive', 'Ruins', 'Mountains'],
        'featured': True,
        'views': 200,
        'highlights': [
            {'time': '03:20', 'title': 'Sun Temple', 'description': 'Stunning stonework and vistas'},
        ],
        'interactive_elements': [
            {'info': 'Tap on the terraces (05:30) to learn about Inca agriculture'},
        ]
    },
    {
        'tour_id': '4',
        'name': 'Paris Louvre 360° Walkthrough',
        'country': 'France',
        'duration': '11:11',
        'tour_type': 'cultural_360',
        'thumbnail': 'https://i.ytimg.com/vi/7A1tM6l5oMc/hqdefault.jpg',
        'video_url': 'https://www.youtube.com/watch?v=7A1tM6l5oMc',
        'description': 'A cultural 360° stroll through Louvre courtyards and nearby landmarks.',
        'features': ['Museums', 'Culture', 'City Walk'],
        'featured': False,
        'views': 45,
    },
    {
        'tour_id': '5',
        'name': 'New Zealand Fiordland 360°',
        'country': 'New Zealand',
        'duration': '10:02',
        'tour_type': 'drone_360',
        'thumbnail': 'https://i.ytimg.com/vi/h0eS0uU56Nw/hqdefault.jpg',
        'video_url': 'https://www.youtube.com/watch?v=h0eS0uU56Nw',
        'description': 'Soar above Milford Sound and dramatic fjords in stunning 360°.',
        'features': ['Nature', 'Drone 360', 'Mountains'],
        'featured': False,
        'views': 30,
    },
    {
        'tour_id': '6',
        'name': 'Cairo Pyramids 360°',
        'country': 'Egypt',
        'duration': '8:27',
        'tour_type': 'interactive_360',
        'thumbnail': 'https://i.ytimg.com/vi/1dV7l8l2rKs/hqdefault.jpg',
        'video_url': 'https://www.youtube.com/watch?v=1dV7l8l2rKs',
        'description': 'Interactive 360° with pyramid facts and quick time jumps to key viewpoints.',
        'features': ['Desert', 'History', 'Interactive'],
        'featured': False,
        'views': 60,
    },
    {
        'tour_id': '7',
        'name': 'Bali Ubud Rice Terraces 360°',
        'country': 'Indonesia',
        'duration': '7:59',
        'tour_type': '360_video',
        'thumbnail': 'https://i.ytimg.com/vi/i3e0iQH3D1g/hqdefault.jpg',
        'video_url': 'https://www.youtube.com/watch?v=i3e0iQH3D1g',
        'description': 'Walk through lush emerald terraces and jungle sounds in 360°.',
        'features': ['Nature', '360° View', 'Culture'],
        'featured': False,
        'views': 25,
    },
    {
        'tour_id': '8',
        'name': 'New York City 360° Rooftop',
        'country': 'USA',
        'duration': '6:45',
        'tour_type': '360_video',
        'thumbnail': 'https://i.ytimg.com/vi/2-Bm-t5nAnw/hqdefault.jpg',
        'video_url': 'https://www.youtube.com/watch?v=2-Bm-t5nAnw',
        'description': 'Iconic skyline views from a Midtown rooftop in 360°.',
        'features': ['City', 'Skyline', '360° View'],
        'featured': False,
        'views': 90,
    },
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

    # Seed virtual tours (only if empty)
    count = await db.virtual_tours.estimated_document_count()
    if count == 0:
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
    except Exception:
        err = 'I am experiencing technical difficulties. Please try again shortly.'
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
async def get_destinations(limit: int = 6):
    if db is None:
        return MOCK_DESTINATIONS[:limit]
    cursor = db.destinations.find({}).limit(int(limit))
    results = []
    async for doc in cursor:
        results.append(fix_id(doc))
    return results

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
@app.post('/api/bookings')
async def create_booking(body: BookingReq, user=Depends(get_user_from_token)):
    if db is None:
        return {'booking_id': str(uuid4()), **body.dict(), 'status': 'confirmed', 'created_at': datetime.utcnow()}
    
    # Verify destination exists
    destination = await db.destinations.find_one({'destination_id': body.destination_id})
    if not destination:
        raise HTTPException(status_code=404, detail='Destination not found')

    booking = {
        'booking_id': str(uuid4()),
        'user_id': user['user_id'],
        'destination_id': body.destination_id,
        'destination_name': destination['name'],
        'destination_image': destination['images'][0] if destination.get('images') else None,
        'date': body.date,
        'guests': body.guests,
        'total_price': body.total_price,
        'status': 'confirmed',
        'created_at': datetime.utcnow()
    }
    await db.bookings.insert_one(booking)
    return fix_id(booking)

@app.get('/api/bookings')
async def get_user_bookings(user=Depends(get_user_from_token)):
    if db is None: return []
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