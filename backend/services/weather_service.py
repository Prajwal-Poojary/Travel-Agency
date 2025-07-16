import aiohttp
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from config import settings

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = settings.weather_api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    async def get_current_weather(self, city: str, country: str = None) -> Dict[str, Any]:
        """Get current weather for a city"""
        if not self.api_key or self.api_key == "your-openweathermap-api-key-here":
            return self._get_mock_weather(city, country)
        
        try:
            location = f"{city},{country}" if country else city
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_weather_data(data)
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return self._get_mock_weather(city, country)
        
        except Exception as e:
            logger.error(f"Weather service error: {e}")
            return self._get_mock_weather(city, country)
    
    def _format_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format weather data"""
        return {
            "main": {
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"]
            },
            "weather": [{
                "main": data["weather"][0]["main"],
                "description": data["weather"][0]["description"]
            }],
            "wind": {
                "speed": data["wind"]["speed"]
            },
            "location": {
                "city": data["name"],
                "country": data["sys"]["country"]
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _get_mock_weather(self, city: str, country: str = None) -> Dict[str, Any]:
        """Get mock weather data when API is not available"""
        mock_data = {
            "maldives": {"temp": 28, "condition": "Clear", "humidity": 75},
            "tokyo": {"temp": 22, "condition": "Partly Cloudy", "humidity": 65},
            "santorini": {"temp": 25, "condition": "Sunny", "humidity": 60},
            "dubai": {"temp": 32, "condition": "Sunny", "humidity": 45},
            "bali": {"temp": 26, "condition": "Partly Cloudy", "humidity": 80},
            "switzerland": {"temp": 15, "condition": "Cloudy", "humidity": 70}
        }
        
        city_key = city.lower()
        weather_info = mock_data.get(city_key, {"temp": 20, "condition": "Clear", "humidity": 60})
        
        return {
            "main": {
                "temp": weather_info["temp"],
                "feels_like": weather_info["temp"] + 2,
                "humidity": weather_info["humidity"],
                "pressure": 1013
            },
            "weather": [{
                "main": weather_info["condition"],
                "description": weather_info["condition"]
            }],
            "wind": {"speed": 5},
            "location": {
                "city": city,
                "country": country or "Unknown"
            },
            "last_updated": datetime.utcnow().isoformat(),
            "note": "Mock data - Weather API key not configured"
        }

# Global weather service instance
weather_service = WeatherService()