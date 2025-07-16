from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: str
    created_at: datetime
    avatar: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = {}

class Token(BaseModel):
    access_token: str
    token_type: str
    user: str

class DestinationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    country: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10)
    price_range: str
    activities: List[str] = []
    best_time_to_visit: str
    images: List[str] = []
    coordinates: Optional[Dict[str, float]] = {}
    rating: float = Field(default=0.0, ge=0, le=5)
    featured: bool = False

class DestinationResponse(BaseModel):
    destination_id: str
    name: str
    country: str
    city: str
    category: str
    description: str
    price_range: str
    activities: List[str]
    best_time_to_visit: str
    images: List[str]
    coordinates: Dict[str, float]
    rating: float
    featured: bool
    created_at: datetime
    weather: Optional[Dict[str, Any]] = None

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class BookingCreate(BaseModel):
    destination_id: str
    check_in_date: datetime
    check_out_date: datetime
    guests: int = Field(..., ge=1, le=20)
    special_requests: Optional[str] = None

class BookingResponse(BaseModel):
    booking_id: str
    user_id: str
    destination_id: str
    destination_name: str
    check_in_date: datetime
    check_out_date: datetime
    guests: int
    special_requests: Optional[str]
    status: BookingStatus
    total_amount: float
    created_at: datetime

class ReviewCreate(BaseModel):
    destination_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=10, max_length=1000)
    images: Optional[List[str]] = []
    categories: Optional[Dict[str, int]] = {}

class ReviewResponse(BaseModel):
    review_id: str
    destination_id: str
    user_id: str
    username: str
    rating: int
    comment: str
    images: List[str]
    categories: Dict[str, int]
    helpful_count: int
    verified_stay: bool
    created_at: datetime

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None

class AIRecommendationRequest(BaseModel):
    budget: Optional[str] = "moderate"
    activities: Optional[List[str]] = []
    travel_style: Optional[str] = "leisure"
    duration: Optional[str] = "1 week"
    group_size: Optional[int] = 2
    interests: Optional[List[str]] = []

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]