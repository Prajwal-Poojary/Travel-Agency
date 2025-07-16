from fastapi import APIRouter, Depends
from models import AIRecommendationRequest, ChatMessage
from services.ai_service import ai_service
from auth import get_current_user, get_current_user_optional
from database import get_database
import uuid
from datetime import datetime

router = APIRouter(prefix="/api", tags=["ai"])

@router.post("/ai/recommendations")
async def get_ai_recommendations(
    request: AIRecommendationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get AI-powered travel recommendations"""
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

@router.post("/chat")
async def chat_with_ai(
    message: ChatMessage,
    current_user: dict = Depends(get_current_user_optional)
):
    """Chat with AI travel assistant"""
    try:
        session_id = message.session_id or str(uuid.uuid4())
        
        # Get chat history if user is authenticated
        chat_history = []
        if current_user:
            db = get_database()
            chat_session = await db.chat_sessions.find_one({"session_id": session_id})
            chat_history = chat_session.get("messages", []) if chat_session else []
        
        # Get AI response
        response = await ai_service.chat_with_assistant(
            message.message, 
            session_id, 
            chat_history
        )
        
        # Update chat session if user is authenticated
        if current_user:
            db = get_database()
            new_messages = chat_history + [
                {"role": "user", "content": message.message, "timestamp": datetime.utcnow()},
                {"role": "assistant", "content": response["response"], "timestamp": datetime.utcnow()}
            ]
            
            await db.chat_sessions.replace_one(
                {"session_id": session_id},
                {
                    "session_id": session_id,
                    "user_id": current_user["user_id"],
                    "messages": new_messages,
                    "updated_at": datetime.utcnow()
                },
                upsert=True
            )
        
        return response
        
    except Exception as e:
        return {
            "success": False,
            "response": "I'm having trouble connecting right now. Please try again in a moment.",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }