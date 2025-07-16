from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from datetime import datetime

from models import ReviewCreate, ReviewResponse
from database import get_database
from auth import get_current_user

router = APIRouter(prefix="/api/reviews", tags=["reviews"])

@router.post("/", response_model=ReviewResponse)
async def create_review(
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new review"""
    db = get_database()
    
    # Validate destination exists
    destination = await db.destinations.find_one({"destination_id": review.destination_id})
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    # Check if user already reviewed this destination
    existing_review = await db.reviews.find_one({
        "destination_id": review.destination_id,
        "user_id": current_user["user_id"]
    })
    if existing_review:
        raise HTTPException(
            status_code=400, 
            detail="You have already reviewed this destination"
        )
    
    review_data = {
        "review_id": str(uuid.uuid4()),
        "destination_id": review.destination_id,
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "rating": review.rating,
        "comment": review.comment,
        "images": review.images or [],
        "categories": review.categories or {},
        "helpful_count": 0,
        "verified_stay": False,  # Could be verified based on bookings
        "created_at": datetime.utcnow()
    }
    
    result = await db.reviews.insert_one(review_data)
    review_data["_id"] = str(result.inserted_id)
    
    # Update destination rating
    await update_destination_rating(review.destination_id)
    
    return ReviewResponse(**review_data)

@router.get("/{destination_id}", response_model=List[ReviewResponse])
async def get_destination_reviews(destination_id: str, limit: int = 50):
    """Get reviews for a destination"""
    db = get_database()
    
    reviews = await db.reviews.find(
        {"destination_id": destination_id}
    ).limit(limit).to_list(length=limit)
    
    result = []
    for review in reviews:
        review["_id"] = str(review["_id"])
        result.append(ReviewResponse(**review))
    
    return result

async def update_destination_rating(destination_id: str):
    """Update destination rating based on reviews"""
    db = get_database()
    
    pipeline = [
        {"$match": {"destination_id": destination_id}},
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
    ]
    
    result = await db.reviews.aggregate(pipeline).to_list(length=None)
    if result:
        new_rating = round(result[0]["avg_rating"], 1)
        await db.destinations.update_one(
            {"destination_id": destination_id},
            {"$set": {"rating": new_rating}}
        )