import os
import asyncio
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from google import genai
from google.genai import types as genai_types

# Load env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

MONGO_URL = os.environ.get('MONGO_URL')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

async def check_mongo():
    print(f"Checking MongoDB connection...")
    if not MONGO_URL:
        print("❌ MONGO_URL not found in .env")
        return False
    
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        print("✅ MongoDB connected successfully!")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

async def check_gemini():
    print(f"Checking Gemini API...")
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not found in .env")
        return False
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents='Hello, are you working?',
        )
        print(f"✅ Gemini API working! Response: {response.text[:20]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini API failed: {e}")
        return False

async def main():
    mongo_ok = await check_mongo()
    gemini_ok = await check_gemini()
    
    if mongo_ok and gemini_ok:
        print("\n✅ Backend connectivity check PASSED")
    else:
        print("\n❌ Backend connectivity check FAILED")

if __name__ == "__main__":
    asyncio.run(main())
