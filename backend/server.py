import os
import re
import json
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import jwt
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
from uuid import uuid4

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
app = FastAPI(title='Advanced Travel Platform (FastAPI)', version='1.0.0')
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
DB_NAME = getattr(client, 'options', None).dbName if getattr(client, 'options', None) and hasattr(client.options, 'dbName') else (db_name_match.group(1) if db_name_match else None)
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

async def ensure_demo_seed():
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

# ---- Startup ----
@app.on_event('startup')
async def on_start():
    # Indexes
    await db.users.create_index('email', unique=True)
    await db.users.create_index('username', unique=True)
    await ensure_demo_seed()

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

@app.post('/api/chat', response_model=ChatOut)
async def chat(body: ChatBody, user=Depends(get_user_from_token)):
    session_id = body.session_id or f"session_{str(uuid4())[:8]}"
    if not gemini_client:
        # Fallback response when Gemini not configured
        return ChatOut(session_id=session_id, response='AI service is not configured. Please add a valid GEMINI_API_KEY to backend/.env.', timestamp=datetime.utcnow())
    try:
        safety = [
            genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=genai_types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
            genai_types.SafetySetting(category=genai_types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=genai_types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
        ]
        result = await app.loop.run_in_executor(
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
        return ChatOut(session_id=session_id, response=text, timestamp=datetime.utcnow())
    except Exception as e:
        # Graceful fallback
        return ChatOut(session_id=session_id, response='I am experiencing technical difficulties. Please try again shortly.', timestamp=datetime.utcnow())

@app.post('/api/ai/recommendations')
async def ai_recommendations(prefs: RecReq, user=Depends(get_user_from_token)):
    # Use a deterministic prompt
    prompt = (
        "Generate concise travel recommendations as bullet points based on these preferences: "
        + json.dumps(prefs.model_dump(exclude_none=True))
    )
    if not gemini_client:
        return {'recommendations': ['Enable GEMINI_API_KEY to get AI recommendations.']}
    try:
        result = await app.loop.run_in_executor(
            None,
            lambda: gemini_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=genai_types.GenerateContentConfig(max_output_tokens=600, temperature=0.5)
            )
        )
        text = getattr(result, 'text', '')
        # Simple parse into list lines
        lines = [l.strip('- ').strip() for l in text.split('\n') if l.strip()]
        return {'recommendations': lines[:10]}
    except Exception:
        return {'recommendations': ['Unable to generate recommendations at this time. Please try again later.']}

# ---- Run (handled by supervisor) ----
# Do not add uvicorn.run here.