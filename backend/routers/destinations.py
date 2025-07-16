from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
import uuid
from datetime import datetime

from models import DestinationCreate, DestinationResponse
from database import get_database
from services.weather_service import weather_service
from auth import get_current_user_optional

router = APIRouter(prefix="/api/destinations", tags=["destinations"])

@router.get("/", response_model=List[DestinationResponse])
async def get_destinations(
    search: Optional[str] = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    activity: Optional[str] = None,
    featured_only: Optional[bool] = False,
    limit: Optional[int] = 100
):
    """Get destinations with optional filtering"""
    db = get_database()
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"city": {"$regex": search, "$options": "i"}},
            {"country": {"$regex": search, "$options": "i"}}
        ]
    
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    
    if activity:
        query["activities"] = {"$in": [activity]}
    
    if featured_only:
        query["featured"] = True
    
    destinations = await db.destinations.find(query).limit(limit).to_list(length=limit)
    
    # Add weather data for each destination
    result = []
    for destination in destinations:
        destination["_id"] = str(destination["_id"])
        
        # Add weather data
        weather_data = await weather_service.get_current_weather(
            destination["city"], 
            destination["country"]
        )
        destination["weather"] = weather_data
        
        result.append(DestinationResponse(**destination))
    
    return result

@router.get("/featured", response_model=List[DestinationResponse])
async def get_featured_destinations():
    """Get featured destinations"""
    return await get_destinations(featured_only=True, limit=6)

@router.get("/countries")
async def get_countries():
    """Get all available countries"""
    db = get_database()
    countries = await db.destinations.distinct("country")
    return countries

@router.get("/activities")
async def get_activities():
    """Get all available activities"""
    db = get_database()
    activities = await db.destinations.distinct("activities")
    return activities

@router.get("/{destination_id}", response_model=DestinationResponse)
async def get_destination(destination_id: str):
    """Get specific destination by ID"""
    db = get_database()
    destination = await db.destinations.find_one({"destination_id": destination_id})
    
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    destination["_id"] = str(destination["_id"])
    
    # Add weather data
    weather_data = await weather_service.get_current_weather(
        destination["city"], 
        destination["country"]
    )
    destination["weather"] = weather_data
    
    return DestinationResponse(**destination)

@router.post("/", response_model=DestinationResponse)
async def create_destination(
    destination: DestinationCreate,
    current_user: dict = Depends(get_current_user_optional)
):
    """Create a new destination (admin only for now)"""
    db = get_database()
    
    destination_data = destination.dict()
    destination_data["destination_id"] = str(uuid.uuid4())
    destination_data["created_at"] = datetime.utcnow()
    
    result = await db.destinations.insert_one(destination_data)
    destination_data["_id"] = str(result.inserted_id)
    
    return DestinationResponse(**destination_data)