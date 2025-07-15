import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VirtualToursService:
    def __init__(self):
        self.tours_data = self._load_virtual_tours_data()
    
    def _load_virtual_tours_data(self) -> Dict[str, Any]:
        """Load virtual tours data with embedded videos and 360° content"""
        return {
            "maldives": {
                "name": "Maldives Paradise Resort",
                "country": "Maldives",
                "description": "Experience the ultimate luxury in overwater bungalows with crystal-clear waters",
                "tour_type": "360_video",
                "duration": "8:30",
                "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                "thumbnail": "https://images.unsplash.com/photo-1512100356356-de1b84283e18?w=800&h=600&fit=crop",
                "features": ["360° View", "Audio Guide", "Interactive Hotspots", "VR Compatible"],
                "highlights": [
                    {"time": "0:30", "title": "Overwater Bungalows", "description": "Luxury accommodations over crystal waters"},
                    {"time": "2:15", "title": "Underwater Restaurant", "description": "Dine surrounded by marine life"},
                    {"time": "4:45", "title": "Spa Pavilion", "description": "Relaxation with ocean views"},
                    {"time": "6:20", "title": "Sunset Deck", "description": "Perfect spot for romantic evenings"}
                ],
                "interactive_elements": [
                    {"type": "hotspot", "position": {"x": 45, "y": 60}, "info": "Click to learn about marine life"},
                    {"type": "navigation", "position": {"x": 80, "y": 30}, "info": "Navigate to spa area"}
                ]
            },
            "tokyo": {
                "name": "Tokyo Futuristic Experience",
                "country": "Japan",
                "description": "Explore the perfect blend of traditional culture and cutting-edge technology",
                "tour_type": "interactive_360",
                "duration": "12:45",
                "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                "thumbnail": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&h=600&fit=crop",
                "features": ["360° View", "Multi-language Audio", "AR Elements", "Cultural Insights"],
                "highlights": [
                    {"time": "0:45", "title": "Shibuya Crossing", "description": "World's busiest pedestrian crossing"},
                    {"time": "3:20", "title": "Senso-ji Temple", "description": "Ancient Buddhist temple in modern city"},
                    {"time": "6:10", "title": "Tokyo Skytree", "description": "Panoramic city views from 634m high"},
                    {"time": "9:30", "title": "Tsukiji Market", "description": "Fresh sushi and local delicacies"}
                ],
                "interactive_elements": [
                    {"type": "cultural_info", "position": {"x": 30, "y": 40}, "info": "Learn about Japanese customs"},
                    {"type": "food_guide", "position": {"x": 70, "y": 50}, "info": "Discover local cuisine"}
                ]
            },
            "santorini": {
                "name": "Santorini Sunset Villa",
                "country": "Greece",
                "description": "White-washed buildings and the most spectacular sunsets in the world",
                "tour_type": "timelapse_360",
                "duration": "10:20",
                "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                "thumbnail": "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&h=600&fit=crop",
                "features": ["Sunset Timelapse", "360° Views", "Historical Context", "Wine Tasting Guide"],
                "highlights": [
                    {"time": "1:00", "title": "Oia Village", "description": "Iconic blue-domed churches and windmills"},
                    {"time": "3:45", "title": "Caldera Views", "description": "Volcanic crater with stunning vistas"},
                    {"time": "6:30", "title": "Wine Terraces", "description": "Ancient vineyards with unique volcanic soil"},
                    {"time": "8:15", "title": "Sunset Point", "description": "World-famous sunset viewing location"}
                ],
                "interactive_elements": [
                    {"type": "history", "position": {"x": 25, "y": 35}, "info": "Learn about volcanic history"},
                    {"type": "wine_info", "position": {"x": 60, "y": 70}, "info": "Discover local wines"}
                ]
            },
            "swiss_alps": {
                "name": "Swiss Alps Adventure",
                "country": "Switzerland",
                "description": "Breathtaking mountain landscapes and world-class skiing",
                "tour_type": "drone_360",
                "duration": "15:30",
                "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                "thumbnail": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&h=600&fit=crop",
                "features": ["Drone Footage", "Seasonal Views", "Adventure Guide", "Weather Info"],
                "highlights": [
                    {"time": "1:30", "title": "Matterhorn Peak", "description": "Iconic pyramid-shaped mountain"},
                    {"time": "4:20", "title": "Jungfraujoch", "description": "Top of Europe with glacier views"},
                    {"time": "7:45", "title": "Alpine Villages", "description": "Traditional Swiss mountain communities"},
                    {"time": "11:10", "title": "Ski Slopes", "description": "World-renowned skiing destinations"}
                ],
                "interactive_elements": [
                    {"type": "weather", "position": {"x": 20, "y": 20}, "info": "Current mountain weather"},
                    {"type": "activities", "position": {"x": 75, "y": 80}, "info": "Available activities by season"}
                ]
            },
            "bali": {
                "name": "Bali Spiritual Retreat",
                "country": "Indonesia",
                "description": "Tropical paradise with lush rice terraces and ancient temples",
                "tour_type": "cultural_360",
                "duration": "11:15",
                "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                "thumbnail": "https://images.unsplash.com/photo-1537953773345-d172ccf13cf1?w=800&h=600&fit=crop",
                "features": ["Cultural Immersion", "Temple Audio", "Nature Sounds", "Meditation Guide"],
                "highlights": [
                    {"time": "0:50", "title": "Tegallalang Rice Terraces", "description": "UNESCO World Heritage rice fields"},
                    {"time": "3:25", "title": "Tanah Lot Temple", "description": "Sea temple on rocky outcrop"},
                    {"time": "6:40", "title": "Ubud Monkey Forest", "description": "Sacred sanctuary with playful macaques"},
                    {"time": "9:20", "title": "Traditional Village", "description": "Authentic Balinese community life"}
                ],
                "interactive_elements": [
                    {"type": "temple_info", "position": {"x": 40, "y": 30}, "info": "Learn about Hindu traditions"},
                    {"type": "nature_guide", "position": {"x": 65, "y": 60}, "info": "Discover tropical flora and fauna"}
                ]
            },
            "dubai": {
                "name": "Dubai Luxury Experience",
                "country": "UAE",
                "description": "Ultra-modern city with luxury shopping and innovative architecture",
                "tour_type": "luxury_360",
                "duration": "13:40",
                "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                "thumbnail": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&h=600&fit=crop",
                "features": ["Luxury Focus", "Architecture Guide", "Shopping Tour", "Night Views"],
                "highlights": [
                    {"time": "1:15", "title": "Burj Khalifa", "description": "World's tallest building with observation deck"},
                    {"time": "4:30", "title": "Palm Jumeirah", "description": "Artificial island with luxury resorts"},
                    {"time": "7:20", "title": "Dubai Mall", "description": "World's largest shopping destination"},
                    {"time": "10:45", "title": "Desert Safari", "description": "Adventure in golden sand dunes"}
                ],
                "interactive_elements": [
                    {"type": "shopping", "position": {"x": 50, "y": 40}, "info": "Luxury shopping guide"},
                    {"type": "dining", "position": {"x": 30, "y": 70}, "info": "Fine dining recommendations"}
                ]
            }
        }
    
    def get_all_tours(self) -> List[Dict[str, Any]]:
        """Get all available virtual tours"""
        tours = []
        for tour_id, tour_data in self.tours_data.items():
            tours.append({
                "id": tour_id,
                **tour_data,
                "created_at": datetime.utcnow().isoformat()
            })
        return tours
    
    def get_tour_by_id(self, tour_id: str) -> Optional[Dict[str, Any]]:
        """Get specific virtual tour by ID"""
        if tour_id in self.tours_data:
            return {
                "id": tour_id,
                **self.tours_data[tour_id],
                "created_at": datetime.utcnow().isoformat()
            }
        return None
    
    def get_tour_by_destination(self, destination_name: str) -> Optional[Dict[str, Any]]:
        """Get virtual tour by destination name"""
        destination_lower = destination_name.lower()
        for tour_id, tour_data in self.tours_data.items():
            if destination_lower in tour_data["name"].lower():
                return {
                    "id": tour_id,
                    **tour_data,
                    "created_at": datetime.utcnow().isoformat()
                }
        return None
    
    def get_featured_tours(self, limit: int = 6) -> List[Dict[str, Any]]:
        """Get featured virtual tours"""
        all_tours = self.get_all_tours()
        return all_tours[:limit]
    
    def search_tours(self, query: str) -> List[Dict[str, Any]]:
        """Search virtual tours by query"""
        query_lower = query.lower()
        matching_tours = []
        
        for tour_id, tour_data in self.tours_data.items():
            if (query_lower in tour_data["name"].lower() or 
                query_lower in tour_data["country"].lower() or 
                query_lower in tour_data["description"].lower()):
                matching_tours.append({
                    "id": tour_id,
                    **tour_data,
                    "created_at": datetime.utcnow().isoformat()
                })
        
        return matching_tours
    
    def get_tour_analytics(self, tour_id: str) -> Dict[str, Any]:
        """Get analytics for a virtual tour"""
        if tour_id not in self.tours_data:
            return {"error": "Tour not found"}
        
        # Simulated analytics data
        return {
            "tour_id": tour_id,
            "views": 15420,
            "average_duration": "6:45",
            "completion_rate": 78.5,
            "user_ratings": {
                "average": 4.7,
                "total_ratings": 342,
                "distribution": {
                    "5": 65,
                    "4": 25,
                    "3": 8,
                    "2": 1,
                    "1": 1
                }
            },
            "popular_highlights": [
                {"title": "Most viewed section", "timestamp": "3:20", "views": 12340},
                {"title": "Most replayed section", "timestamp": "6:15", "replays": 8760}
            ]
        }

# Global virtual tours service instance
virtual_tours_service = VirtualToursService()