import os
import asyncio
import aiohttp
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.cache = {}
        self.cache_duration = timedelta(minutes=30)
    
    async def get_current_weather(self, city: str, country: str = None) -> Dict[str, Any]:
        """Get current weather for a city"""
        if not self.api_key or self.api_key == "your-openweathermap-api-key-here":
            return self._get_mock_weather(city, country)
        
        # Check cache first
        cache_key = f"{city}_{country or ''}_current"
        if self._is_cached(cache_key):
            return self.cache[cache_key]["data"]
        
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
                        weather_data = self._format_current_weather(data)
                        self._cache_data(cache_key, weather_data)
                        return weather_data
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return self._get_mock_weather(city, country)
        
        except Exception as e:
            logger.error(f"Weather service error: {e}")
            return self._get_mock_weather(city, country)
    
    async def get_weather_forecast(self, city: str, country: str = None, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a city"""
        if not self.api_key or self.api_key == "your-openweathermap-api-key-here":
            return self._get_mock_forecast(city, country, days)
        
        cache_key = f"{city}_{country or ''}_forecast_{days}"
        if self._is_cached(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            location = f"{city},{country}" if country else city
            url = f"{self.base_url}/forecast"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        forecast_data = self._format_forecast(data)
                        self._cache_data(cache_key, forecast_data)
                        return forecast_data
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return self._get_mock_forecast(city, country, days)
        
        except Exception as e:
            logger.error(f"Weather forecast error: {e}")
            return self._get_mock_forecast(city, country, days)
    
    async def get_travel_weather_advice(self, city: str, country: str = None) -> Dict[str, Any]:
        """Get travel-specific weather advice"""
        current_weather = await self.get_current_weather(city, country)
        forecast = await self.get_weather_forecast(city, country, 7)
        
        advice = self._generate_travel_advice(current_weather, forecast)
        
        return {
            "current_weather": current_weather,
            "forecast": forecast,
            "travel_advice": advice,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _format_current_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format current weather data"""
        return {
            "temperature": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "visibility": data.get("visibility", 0) / 1000,  # Convert to km
            "uv_index": data.get("uvi", 0),
            "condition": data["weather"][0]["main"],
            "description": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"],
            "wind": {
                "speed": data["wind"]["speed"],
                "direction": data["wind"].get("deg", 0)
            },
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M"),
            "location": {
                "city": data["name"],
                "country": data["sys"]["country"],
                "coordinates": {
                    "lat": data["coord"]["lat"],
                    "lon": data["coord"]["lon"]
                }
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _format_forecast(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format forecast data"""
        daily_forecasts = []
        current_date = None
        daily_data = []
        
        for item in data["list"]:
            forecast_date = datetime.fromtimestamp(item["dt"]).date()
            
            if current_date != forecast_date:
                if daily_data:
                    daily_forecasts.append(self._aggregate_daily_forecast(current_date, daily_data))
                current_date = forecast_date
                daily_data = []
            
            daily_data.append(item)
        
        # Add the last day
        if daily_data:
            daily_forecasts.append(self._aggregate_daily_forecast(current_date, daily_data))
        
        return {
            "location": {
                "city": data["city"]["name"],
                "country": data["city"]["country"]
            },
            "daily_forecasts": daily_forecasts[:7],  # Limit to 7 days
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _aggregate_daily_forecast(self, date, hourly_data) -> Dict[str, Any]:
        """Aggregate hourly data into daily forecast"""
        temps = [item["main"]["temp"] for item in hourly_data]
        conditions = [item["weather"][0]["main"] for item in hourly_data]
        
        # Find most common condition
        condition_counts = {}
        for condition in conditions:
            condition_counts[condition] = condition_counts.get(condition, 0) + 1
        most_common_condition = max(condition_counts, key=condition_counts.get)
        
        return {
            "date": date.isoformat(),
            "day_name": date.strftime("%A"),
            "temperature": {
                "min": round(min(temps)),
                "max": round(max(temps)),
                "average": round(sum(temps) / len(temps))
            },
            "condition": most_common_condition,
            "description": hourly_data[0]["weather"][0]["description"].title(),
            "icon": hourly_data[0]["weather"][0]["icon"],
            "humidity": round(sum(item["main"]["humidity"] for item in hourly_data) / len(hourly_data)),
            "wind_speed": round(sum(item["wind"]["speed"] for item in hourly_data) / len(hourly_data), 1),
            "precipitation_chance": max(item.get("pop", 0) for item in hourly_data) * 100
        }
    
    def _generate_travel_advice(self, current: Dict[str, Any], forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Generate travel-specific weather advice"""
        advice = {
            "clothing_recommendations": [],
            "activity_suggestions": [],
            "travel_warnings": [],
            "best_times": [],
            "packing_tips": []
        }
        
        temp = current.get("temperature", 20)
        condition = current.get("condition", "Clear").lower()
        
        # Clothing recommendations
        if temp < 0:
            advice["clothing_recommendations"].extend(["Heavy winter coat", "Thermal layers", "Warm boots", "Gloves and hat"])
        elif temp < 10:
            advice["clothing_recommendations"].extend(["Warm jacket", "Long pants", "Closed shoes", "Light scarf"])
        elif temp < 20:
            advice["clothing_recommendations"].extend(["Light jacket", "Long or short pants", "Comfortable shoes"])
        elif temp < 30:
            advice["clothing_recommendations"].extend(["Light clothing", "Shorts/skirts", "Sandals", "Sun hat"])
        else:
            advice["clothing_recommendations"].extend(["Very light clothing", "Shorts", "Sandals", "Sun protection"])
        
        # Activity suggestions based on weather
        if condition in ["clear", "sunny"]:
            advice["activity_suggestions"].extend(["Outdoor sightseeing", "Photography", "Walking tours", "Beach activities"])
        elif condition in ["rain", "drizzle"]:
            advice["activity_suggestions"].extend(["Indoor museums", "Shopping", "Covered markets", "Cafes and restaurants"])
        elif condition in ["snow"]:
            advice["activity_suggestions"].extend(["Winter sports", "Hot springs", "Indoor attractions", "Cozy restaurants"])
        
        # Travel warnings
        if current.get("wind", {}).get("speed", 0) > 15:
            advice["travel_warnings"].append("Strong winds - secure loose items")
        if temp > 35:
            advice["travel_warnings"].append("Extreme heat - stay hydrated and seek shade")
        if temp < -10:
            advice["travel_warnings"].append("Extreme cold - dress warmly and limit outdoor exposure")
        
        # Best times for activities
        sunrise = current.get("sunrise", "06:00")
        sunset = current.get("sunset", "18:00")
        advice["best_times"] = [
            f"Sunrise at {sunrise} - great for photography",
            f"Sunset at {sunset} - perfect for evening activities",
            "Mid-morning (10-11 AM) - comfortable temperatures",
            "Late afternoon (4-5 PM) - good lighting and cooler temps"
        ]
        
        # Packing tips
        advice["packing_tips"] = [
            "Check weather forecast before departure",
            "Pack layers for temperature changes",
            "Bring appropriate footwear for conditions",
            "Don't forget sun protection (sunscreen, hat, sunglasses)",
            "Pack a small umbrella or rain jacket"
        ]
        
        return advice
    
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
            "temperature": weather_info["temp"],
            "feels_like": weather_info["temp"] + 2,
            "humidity": weather_info["humidity"],
            "pressure": 1013,
            "visibility": 10,
            "uv_index": 5,
            "condition": weather_info["condition"],
            "description": weather_info["condition"],
            "icon": "01d",
            "wind": {"speed": 5, "direction": 180},
            "sunrise": "06:30",
            "sunset": "18:30",
            "location": {
                "city": city,
                "country": country or "Unknown",
                "coordinates": {"lat": 0, "lon": 0}
            },
            "last_updated": datetime.utcnow().isoformat(),
            "note": "Mock data - Weather API key not configured"
        }
    
    def _get_mock_forecast(self, city: str, country: str = None, days: int = 5) -> Dict[str, Any]:
        """Get mock forecast data"""
        base_temp = self._get_mock_weather(city, country)["temperature"]
        daily_forecasts = []
        
        for i in range(days):
            date = datetime.now().date() + timedelta(days=i)
            temp_variation = (-2, 2, -1, 3, 1)[i % 5]
            
            daily_forecasts.append({
                "date": date.isoformat(),
                "day_name": date.strftime("%A"),
                "temperature": {
                    "min": base_temp + temp_variation - 3,
                    "max": base_temp + temp_variation + 3,
                    "average": base_temp + temp_variation
                },
                "condition": ["Clear", "Partly Cloudy", "Cloudy", "Rain", "Sunny"][i % 5],
                "description": "Pleasant weather",
                "icon": "01d",
                "humidity": 60 + (i * 5),
                "wind_speed": 5 + i,
                "precipitation_chance": i * 10
            })
        
        return {
            "location": {"city": city, "country": country or "Unknown"},
            "daily_forecasts": daily_forecasts,
            "generated_at": datetime.utcnow().isoformat(),
            "note": "Mock data - Weather API key not configured"
        }
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and still valid"""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key]["timestamp"]
        return datetime.utcnow() - cached_time < self.cache_duration
    
    def _cache_data(self, key: str, data: Dict[str, Any]):
        """Cache data with timestamp"""
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.utcnow()
        }

# Global weather service instance
weather_service = WeatherService()