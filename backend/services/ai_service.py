import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = None
        
        if self.api_key and self.api_key != "your-gemini-api-key-here":
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini AI initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI: {e}")
                self.model = None
        else:
            logger.warning("Gemini API key not configured")

    async def get_travel_recommendations(self, user_preferences: Dict[str, Any], user_context: str = "") -> Dict[str, Any]:
        """Get personalized travel recommendations"""
        if not self.model:
            return self._get_fallback_recommendations(user_preferences)
        
        try:
            prompt = self._build_recommendation_prompt(user_preferences, user_context)
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            recommendations = self._parse_recommendations(response.text)
            return {
                "success": True,
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI recommendation error: {e}")
            return self._get_fallback_recommendations(user_preferences)

    async def chat_with_assistant(self, message: str, session_id: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Chat with AI travel assistant"""
        if not self.model:
            return self._get_fallback_chat_response(message)
        
        try:
            context = self._build_chat_context(chat_history or [])
            
            prompt = f"""
            You are an expert travel assistant with deep knowledge of destinations worldwide. 
            You provide helpful, accurate, and personalized travel advice.
            
            Previous conversation context:
            {context}
            
            Current user message: {message}
            
            Please provide a helpful, informative response about travel. Be conversational and engaging.
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            return {
                "success": True,
                "response": response.text,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return self._get_fallback_chat_response(message)

    def _build_recommendation_prompt(self, preferences: Dict[str, Any], context: str) -> str:
        """Build prompt for travel recommendations"""
        return f"""
        You are an expert travel advisor. Based on the following user preferences, 
        provide personalized travel recommendations:
        
        User Preferences: {json.dumps(preferences, indent=2)}
        User Context: {context}
        
        Please provide recommendations in JSON format with destinations, tips, and advice.
        """

    def _build_chat_context(self, chat_history: List[Dict]) -> str:
        """Build context string from chat history"""
        if not chat_history:
            return "This is the start of the conversation."
        
        context_lines = []
        for msg in chat_history[-5:]:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            context_lines.append(f"{role.title()}: {content}")
        
        return "\n".join(context_lines)

    def _parse_recommendations(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured recommendations"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "top_destinations": [
                    {
                        "name": "Santorini",
                        "country": "Greece",
                        "reason": "Perfect for romantic getaways with stunning sunsets",
                        "best_time": "April to October",
                        "estimated_budget": "$200-400 per day",
                        "key_activities": ["Sunset viewing", "Wine tasting", "Beach relaxation"]
                    }
                ],
                "travel_tips": [
                    "Book accommodations in advance during peak season",
                    "Consider travel insurance for international trips"
                ]
            }

    def _get_fallback_recommendations(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback recommendations when AI is not available"""
        return {
            "success": True,
            "recommendations": {
                "top_destinations": [
                    {
                        "name": "Maldives",
                        "country": "Maldives",
                        "reason": "Ultimate luxury beach experience",
                        "best_time": "November to April",
                        "estimated_budget": "$500-1500 per day",
                        "key_activities": ["Snorkeling", "Spa treatments", "Water sports"]
                    },
                    {
                        "name": "Tokyo",
                        "country": "Japan",
                        "reason": "Perfect blend of culture and modernity",
                        "best_time": "March to May, September to November",
                        "estimated_budget": "$150-400 per day",
                        "key_activities": ["Temple visits", "Sushi tasting", "Shopping"]
                    }
                ],
                "travel_tips": [
                    "Research visa requirements for your destination",
                    "Book flights and accommodations in advance",
                    "Consider travel insurance"
                ]
            },
            "note": "AI service not available - showing curated recommendations",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _get_fallback_chat_response(self, message: str) -> Dict[str, Any]:
        """Provide fallback chat response when AI is not available"""
        responses = {
            "hello": "Hello! I'm your travel assistant. I can help you discover amazing destinations and plan your perfect trip. What would you like to know?",
            "destinations": "I can recommend some amazing destinations! Are you looking for beaches, mountains, cities, or cultural experiences?",
            "budget": "I can help you plan a trip within your budget. What's your preferred price range?",
            "default": "Thank you for your question! I'm here to help you plan the perfect trip. Could you tell me more about what type of destination you're looking for?"
        }
        
        message_lower = message.lower()
        response_key = "default"
        
        for key in responses.keys():
            if key in message_lower:
                response_key = key
                break
        
        return {
            "success": True,
            "response": responses[response_key],
            "session_id": "fallback",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "AI service not available - using fallback responses"
        }

# Global AI service instance
ai_service = AIService()