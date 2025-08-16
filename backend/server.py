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
    allow_origins=CORS_ORIGINS if CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---- DB ----
client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URL)
db_name_match = re.search(r"/([^/?]+)(?:\?|$)", MONGO_URL)
DB_NAME = client.get_default_database().name if getattr(client, 'get_default_database', None) and client.get_default_database() is not None else (db_name_match.group(1) if db_name_match else None)
if not DB_NAME:
    raise RuntimeError('Database name not found in MONGO_URL')
db = client[DB_NAME]

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

# ---- Utils ----
ALG = 'HS256'

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
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALG])
        username = payload.get('username')
        user = await db.users.find_one({'username': username})
        if not user:
            raise HTTPException(status_code=401, detail='User not found')
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail='Invalid token')

# ---- Seed & Indexes ----
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
        seed = [
            {
                'tour_id': str(uuid4()),
                'name': 'Tokyo 360° Night Walk',
                'country': 'Japan',
                'duration': '12:45',
                'tour_type': '360_video',
                'thumbnail': 'https://i.ytimg.com/vi/6kAqQWBH6V0/hqdefault.jpg',
                'video_url': 'https://www.youtube.com/watch?v=6kAqQWBH6V0',
                'description': 'Experience the neon-lit streets of Shinjuku and Shibuya in fully immersive 360°.',
                'features': ['360° View', 'City Walk', 'Nightlife'],
                'featured': True,
                'views': 0,
                'highlights': [
                    {'time': '00:45', 'title': 'Shinjuku Crossing', 'description': 'Bustling intersection views'},
                    {'time': '05:10', 'title': 'Golden Gai', 'description': 'Cozy alleys and bars'},
                ],
                'interactive_elements': [
                    {'info': 'Look left at 02:10 to see Godzilla Head on Hotel Gracery'},
                ]
            },
            {
                'tour_id': str(uuid4()),
                'name': 'Santorini Cliffside 360°',
                'country': 'Greece',
                'duration': '9:03',
                'tour_type': 'drone_360',
                'thumbnail': 'https://i.ytimg.com/vi/m2QK_wC9mE8/hqdefault.jpg',
                'video_url': 'https://www.youtube.com/watch?v=m2QK_wC9mE8',
                'description': 'A breathtaking aerial 360° tour of Santorini’s blue domes and caldera views.',
                'features': ['Drone 360', 'Coastline', 'Sunset'],
                'featured': True,
                'views': 0,
                'highlights': [
                    {'time': '01:40', 'title': 'Oia Blue Domes', 'description': 'Iconic rooftops at golden hour'},
                ],
            },
            {
                'tour_id': str(uuid4()),
                'name': 'Machu Picchu Interactive Tour',
                'country': 'Peru',
                'duration': '14:22',
                'tour_type': 'interactive_360',
                'thumbnail': 'https://i.ytimg.com/vi/2m8uRkJ8A_4/hqdefault.jpg',
                'video_url': 'https://www.youtube.com/watch?v=2m8uRkJ8A_4',
                'description': 'Explore the ancient citadel with points-of-interest overlays and an audio guide.',
                'features': ['Interactive', 'Ruins', 'Mountains'],
                'featured': True,
                'views': 0,
                'highlights': [
                    {'time': '03:20', 'title': 'Sun Temple', 'description': 'Stunning stonework and vistas'},
                ],
                'interactive_elements': [
                    {'info': 'Tap on the terraces (05:30) to learn about Inca agriculture'},
                ]
            },
            {
                'tour_id': str(uuid4()),
                'name': 'Paris Louvre 360° Walkthrough',
                'country': 'France',
                'duration': '11:11',
                'tour_type': 'cultural_360',
                'thumbnail': 'https://i.ytimg.com/vi/7A1tM6l5oMc/hqdefault.jpg',
                'video_url': 'https://www.youtube.com/watch?v=7A1tM6l5oMc',
                'description': 'A cultural 360° stroll through Louvre courtyards and nearby landmarks.',
                'features': ['Museums', 'Culture', 'City Walk'],
                'featured': False,
                'views': 0,
            },
            {
                'tour_id': str(uuid4()),
                'name': 'New Zealand Fiordland 360°',
                'country': 'New Zealand',
                'duration': '10:02',
                'tour_type': 'drone_360',
                'thumbnail': 'https://i.ytimg.com/vi/h0eS0uU56Nw/hqdefault.jpg',
                'video_url': 'https://www.youtube.com/watch?v=h0eS0uU56Nw',
                'description': 'Soar above Milford Sound and dramatic fjords in stunning 360°.',
                'features': ['Nature', 'Drone 360', 'Mountains'],
                'featured': False,
                'views': 0,
            },
            {
                'tour_id': str(uuid4()),
                'name': 'Cairo Pyramids 360°',
                'country': 'Egypt',
                'duration': '8:27',
                'tour_type': 'interactive_360',
                'thumbnail': 'https://i.ytimg.com/vi/1dV7l8l2rKs/hqdefault.jpg',
                'video_url': 'https://www.youtube.com/watch?v=1dV7l8l2rKs',
                'description': 'Interactive 360° with pyramid facts and quick time jumps to key viewpoints.',
                'features': ['Desert', 'History', 'Interactive'],
                'featured': False,
                'views': 0,
            },
            {
                'tour_id': str(uuid4()),
                'name': 'Bali Ubud Rice Terraces 360°',
                'country': 'Indonesia',
                'duration': '7:59',
                'tour_type': '360_video',
                'thumbnail': 'https://i.ytimg.com/vi/i3e0iQH3D1g/hqdefault.jpg',
                'video_url': 'https://www.youtube.com/watch?v=i3e0iQH3D1g',
                'description': 'Walk through lush emerald terraces and jungle sounds in 360°.',
                'features': ['Nature', '360° View', 'Culture'],
                'featured': False,
                'views': 0,
            },
            {
                'tour_id': str(uuid4()),
                'name': 'New York City 360° Rooftop',
                'country': 'USA',
                'duration': '6:45',
                'tour_type': '360_video',
                'thumbnail': 'https://i.ytimg.com/vi/2-Bm-t5nAnw/hqdefault.jpg',
                'video_url': 'https://www.youtube.com/watch?v=2-Bm-t5nAnw',
                'description': 'Iconic skyline views from a Midtown rooftop in 360°.',
                'features': ['City', 'Skyline', '360° View'],
                'featured': False,
                'views': 0,
            },
        ]
        await db.virtual_tours.insert_many(seed)

# ---- Startup ----
@app.on_event('startup')
async def on_start():
    await ensure_indexes_and_seed()

# ---- Routes ----
@app.get('/')
async def root():
    return {'message': 'Advanced Travel Platform (FastAPI)', 'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}

@app.get('/api/health')
async def health():
    return {'status': 'healthy', 'gemini': bool(gemini_client), 'timestamp': datetime.utcnow().isoformat()}

@app.post('/api/auth/register')
async def register(body: RegisterBody):
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
    user = await db.users.find_one({'email': body.email})
    if not user or not pwd_context.verify(body.password, user.get('password','')):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_token(user['username'], user['user_id'])
    return {'access_token': token, 'token_type': 'bearer', 'user': user['username'], 'user_id': user['user_id']}

@app.get('/api/auth/profile', response_model=ProfileOut)
async def profile(user=Depends(get_user_from_token)):
    return ProfileOut(
        user_id=user['user_id'], username=user['username'], email=user['email'], full_name=user.get('full_name',''), avatar=user.get('avatar'), created_at=user['created_at']
    )

# ---- Chat persistence helpers ----
async def upsert_session_message(user_id: str, session_id: str, role: str, content: str):
    now = datetime.utcnow().isoformat()
    await db.chat_sessions.update_one(
        {'session_id': session_id, 'user_id': user_id},
        {
            '$setOnInsert': {
                'session_id': session_id,
                'user_id': user_id,
                'created_at': now,
                'messages': []
            },
            '$set': { 'updated_at': now },
            '$push': { 'messages': {'role': role, 'content': content, 'timestamp': now} }
        },
        upsert=True
    )

@app.get('/api/chat/sessions')
async def list_sessions(user=Depends(get_user_from_token)):
    cursor = db.chat_sessions.find({'user_id': user['user_id']}, {'messages': {'$slice': 1}}).sort('updated_at', -1).limit(50)
    sessions = []
    async for s in cursor:
        sessions.append({'session_id': s['session_id'], 'updated_at': s.get('updated_at'), 'created_at': s.get('created_at')})
    return {'sessions': sessions}

@app.get('/api/chat/sessions/{session_id}')
async def get_session(session_id: str, user=Depends(get_user_from_token)):
    s = await db.chat_sessions.find_one({'session_id': session_id, 'user_id': user['user_id']})
    if not s:
        return {'session_id': session_id, 'messages': [], 'created_at': None}
    return {'session_id': session_id, 'messages': s.get('messages', []), 'created_at': s.get('created_at'), 'updated_at': s.get('updated_at')}

@app.delete('/api/chat/sessions/{session_id}')
async def delete_session(session_id: str, user=Depends(get_user_from_token)):
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
        results.append(doc)
    total = await db.virtual_tours.count_documents(filters)
    return {
        'items': results,
        'page': page,
        'limit': limit,
        'total': total,
        'has_more': (skip + len(results)) < total
    }

@app.get('/api/virtual-tours/featured')
async def get_featured_virtual_tours(limit: int = 6):
    cursor = db.virtual_tours.find({'featured': True}).sort('name', 1).limit(int(limit))
    results = []
    async for doc in cursor:
        results.append(doc)
    return results

@app.get('/api/virtual-tours/trending')
async def get_trending_virtual_tours(limit: int = 6):
    cursor = db.virtual_tours.find({}).sort('views', -1).limit(int(limit))
    results = []
    async for doc in cursor:
        results.append(doc)
    return results

@app.post('/api/virtual-tours/{tour_id}/view')
async def add_view_virtual_tour(tour_id: str):
    res = await db.virtual_tours.update_one({'tour_id': tour_id}, {'$inc': {'views': 1}, '$set': {'last_viewed_at': datetime.utcnow().isoformat()}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail='Virtual tour not found')
    return {'message': 'viewed', 'tour_id': tour_id}

@app.get('/api/virtual-tours/types')
async def get_virtual_tour_types():
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
    countries = await db.virtual_tours.distinct('country')
    countries.sort()
    return {'countries': countries}

@app.get('/api/virtual-tours/{tour_id}')
async def get_virtual_tour(tour_id: str):
    tour = await db.virtual_tours.find_one({'tour_id': tour_id})
    if not tour:
        raise HTTPException(status_code=404, detail='Virtual tour not found')
    return tour

# ---- Favorites (auth required) ----
@app.get('/api/virtual-tours/favorites')
async def list_favorites(user=Depends(get_user_from_token)):
    fav_cursor = db.favorites.find({'user_id': user['user_id']})
    fav_ids = []
    async for f in fav_cursor:
        fav_ids.append(f['tour_id'])
    if not fav_ids:
        return {'items': []}
    cursor = db.virtual_tours.find({'tour_id': {'$in': fav_ids}})
    items = []
    async for t in cursor:
        items.append(t)
    return {'items': items}

@app.post('/api/virtual-tours/{tour_id}/favorite')
async def favorite_tour(tour_id: str, user=Depends(get_user_from_token)):
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
    await db.favorites.delete_one({'user_id': user['user_id'], 'tour_id': tour_id})
    return {'message': 'Unfavorited', 'tour_id': tour_id}

# ---- AI Narration for a tour (auth required) ----
@app.post('/api/virtual-tours/{tour_id}/narrate')
async def narrate_tour(tour_id: str, req: NarrationReq, user=Depends(get_user_from_token)):
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

# ---- Run (handled by supervisor) ----
# Do not add uvicorn.run here.