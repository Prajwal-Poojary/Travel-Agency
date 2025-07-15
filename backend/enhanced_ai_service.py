import os
import json
import asyncio
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EnhancedAIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        self.chat_sessions = {}
        
        if self.api_key and self.api_key != "your-gemini-api-key-here":
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini AI initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI: {e}")
                self.model = None
        else:
            logger.warning("Gemini API key not configured")

    async def get_travel_recommendations(self, user_preferences: Dict[str, Any], user_context: str = "") -> Dict[str, Any]:
        """Get personalized travel recommendations based on user preferences"""
        if not self.model:
            return self._get_fallback_recommendations(user_preferences)
        
        try:
            prompt = self._build_recommendation_prompt(user_preferences, user_context)
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            # Parse and structure the response
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
            # Build context from chat history
            context = self._build_chat_context(chat_history or [])
            
            prompt = f"""
            You are an expert travel assistant with deep knowledge of destinations worldwide. 
            You provide helpful, accurate, and personalized travel advice.
            
            Previous conversation context:
            {context}
            
            Current user message: {message}
            
            Please provide a helpful, informative response about travel. Be conversational and engaging.
            If asked about specific destinations, provide detailed information about attractions, 
            best times to visit, local culture, and practical tips.
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

    async def generate_destination_description(self, destination_name: str, country: str) -> str:
        """Generate enhanced destination description"""
        if not self.model:
            return f"Discover the beauty of {destination_name} in {country}. A wonderful destination with rich culture and stunning landscapes."
        
        try:
            prompt = f"""
            Write a compelling, detailed description for {destination_name} in {country}.
            Include information about:
            - Key attractions and landmarks
            - Cultural highlights
            - Natural beauty
            - Best experiences
            - What makes it unique
            
            Keep it engaging and informative, around 150-200 words.
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Description generation error: {e}")
            return f"Discover the beauty of {destination_name} in {country}. A wonderful destination with rich culture and stunning landscapes."

    async def suggest_activities(self, destination: str, user_interests: List[str]) -> List[str]:
        """Suggest activities based on destination and user interests"""
        if not self.model:
            return self._get_fallback_activities(destination)
        
        try:
            interests_str = ", ".join(user_interests) if user_interests else "general travel"
            
            prompt = f"""
            Suggest 8-10 specific activities and experiences for {destination} 
            that would appeal to someone interested in: {interests_str}
            
            Return only a JSON array of activity names, like:
            ["Activity 1", "Activity 2", "Activity 3", ...]
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            # Try to parse JSON response
            try:
                activities = json.loads(response.text.strip())
                return activities if isinstance(activities, list) else self._get_fallback_activities(destination)
            except json.JSONDecodeError:
                # Fallback to text parsing
                lines = response.text.strip().split('\n')
                activities = [line.strip('- "[]') for line in lines if line.strip()]
                return activities[:10]
                
        except Exception as e:
            logger.error(f"Activity suggestion error: {e}")
            return self._get_fallback_activities(destination)

    def _build_recommendation_prompt(self, preferences: Dict[str, Any], context: str) -> str:
        """Build prompt for travel recommendations"""
        return f"""
        You are an expert travel advisor. Based on the following user preferences, 
        provide personalized travel recommendations:
        
        User Preferences: {json.dumps(preferences, indent=2)}
        User Context: {context}
        
        Please provide recommendations in the following JSON format:
        {{
            "top_destinations": [
                {{
                    "name": "Destination Name",
                    "country": "Country",
                    "reason": "Why this destination fits their preferences",
                    "best_time": "Best time to visit",
                    "estimated_budget": "Budget range",
                    "key_activities": ["Activity 1", "Activity 2", "Activity 3"]
                }}
            ],
            "travel_tips": [
                "Tip 1",
                "Tip 2",
                "Tip 3"
            ],
            "budget_advice": "Budget planning advice",
            "packing_suggestions": ["Item 1", "Item 2", "Item 3"]
        }}
        """

    def _build_chat_context(self, chat_history: List[Dict]) -> str:
        """Build context string from chat history"""
        if not chat_history:
            return "This is the start of the conversation."
        
        context_lines = []
        for msg in chat_history[-5:]:  # Last 5 messages for context
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            context_lines.append(f"{role.title()}: {content}")
        
        return "\n".join(context_lines)

    def _parse_recommendations(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured recommendations"""
        try:
            # Try to parse as JSON first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback to text parsing
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
                    "Consider travel insurance for international trips",
                    "Research local customs and etiquette"
                ],
                "budget_advice": "Set aside 20% extra for unexpected expenses",
                "packing_suggestions": ["Comfortable walking shoes", "Weather-appropriate clothing", "Travel adapter"]
            }

    def _get_fallback_recommendations(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback recommendations when AI is not available"""
        budget = preferences.get('budget', 'moderate')
        activities = preferences.get('activities', ['sightseeing'])
        
        destinations = {
            'luxury': [
                {"name": "Maldives", "country": "Maldives", "reason": "Ultimate luxury beach experience"},
                {"name": "Swiss Alps", "country": "Switzerland", "reason": "Premium mountain resort experience"}
            ],
            'budget': [
                {"name": "Bali", "country": "Indonesia", "reason": "Affordable tropical paradise"},
                {"name": "Prague", "country": "Czech Republic", "reason": "Beautiful city with reasonable prices"}
            ],
            'moderate': [
                {"name": "Tokyo", "country": "Japan", "reason": "Perfect blend of culture and modernity"},
                {"name": "Santorini", "country": "Greece", "reason": "Iconic Mediterranean destination"}
            ]
        }
        
        selected_destinations = destinations.get(budget, destinations['moderate'])
        
        return {
            "success": True,
            "recommendations": {
                "top_destinations": [
                    {
                        **dest,
                        "best_time": "Year-round",
                        "estimated_budget": f"${budget} range",
                        "key_activities": activities[:3]
                    } for dest in selected_destinations
                ],
                "travel_tips": [
                    "Research visa requirements for your destination",
                    "Book flights and accommodations in advance",
                    "Consider travel insurance"
                ],
                "budget_advice": "Plan for 20% extra expenses beyond your main budget",
                "packing_suggestions": ["Comfortable shoes", "Weather-appropriate clothing", "Travel documents"]
            },
            "note": "AI service not available - showing curated recommendations",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _get_fallback_chat_response(self, message: str) -> Dict[str, Any]:
        """Provide fallback chat response when AI is not available"""
        responses = {
            "hello": "Hello! I'm your travel assistant. I can help you discover amazing destinations and plan your perfect trip. What would you like to know?",
            "destinations": "I can recommend some amazing destinations! Are you looking for beaches, mountains, cities, or cultural experiences?",
            "budget": "I can help you plan a trip within your budget. What's your preferred price range - budget-friendly, moderate, or luxury?",
            "activities": "There are so many exciting activities to choose from! Are you interested in adventure sports, cultural experiences, relaxation, or sightseeing?",
            "default": "Thank you for your question! I'm here to help you plan the perfect trip. Could you tell me more about what type of destination or experience you're looking for?"
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

    def _get_fallback_activities(self, destination: str) -> List[str]:
        """Get fallback activities for a destination"""
        activities_map = {
            "maldives": ["Snorkeling", "Diving", "Spa treatments", "Sunset cruise", "Water sports", "Beach relaxation"],
            "tokyo": ["Temple visits", "Sushi tasting", "Shopping", "Cherry blossom viewing", "Museum tours", "Nightlife"],
            "santorini": ["Sunset viewing", "Wine tasting", "Beach hopping", "Photography", "Boat tours", "Local cuisine"],
            "bali": ["Temple visits", "Rice terrace tours", "Yoga classes", "Surfing", "Cooking classes", "Art workshops"],
            "default": ["Sightseeing", "Local cuisine", "Cultural tours", "Photography", "Shopping", "Relaxation"]
        }
        
        destination_key = destination.lower()
        for key in activities_map.keys():
            if key in destination_key:
                return activities_map[key]
        
        return activities_map["default"]

# Global AI service instance
ai_service = EnhancedAIService()