from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from datetime import datetime

from models import BookingCreate, BookingResponse, BookingStatus
from database import get_database
from auth import get_current_user

router = APIRouter(prefix="/api/bookings", tags=["bookings"])

@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking: BookingCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new booking"""
    db = get_database()
    
    # Validate destination exists
    destination = await db.destinations.find_one({"destination_id": booking.destination_id})
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    # Validate dates
    if booking.check_out_date <= booking.check_in_date:
        raise HTTPException(
            status_code=400, 
            detail="Check-out date must be after check-in date"
        )
    
    booking_data = {
        "booking_id": str(uuid.uuid4()),
        "user_id": current_user["user_id"],
        "destination_id": booking.destination_id,
        "destination_name": destination["name"],
        "check_in_date": booking.check_in_date,
        "check_out_date": booking.check_out_date,
        "guests": booking.guests,
        "special_requests": booking.special_requests,
        "status": BookingStatus.PENDING,
        "total_amount": 0.0,  # Calculate based on destination pricing
        "created_at": datetime.utcnow()
    }
    
    result = await db.bookings.insert_one(booking_data)
    booking_data["_id"] = str(result.inserted_id)
    
    return BookingResponse(**booking_data)

@router.get("/", response_model=List[BookingResponse])
async def get_user_bookings(current_user: dict = Depends(get_current_user)):
    """Get current user's bookings"""
    db = get_database()
    
    bookings = await db.bookings.find(
        {"user_id": current_user["user_id"]}
    ).to_list(length=100)
    
    result = []
    for booking in bookings:
        booking["_id"] = str(booking["_id"])
        
        # Add destination details
        destination = await db.destinations.find_one(
            {"destination_id": booking["destination_id"]}
        )
        if destination:
            booking["destination_details"] = {
                "name": destination["name"],
                "city": destination["city"],
                "country": destination["country"],
                "images": destination.get("images", [])
            }
        
        result.append(BookingResponse(**booking))
    
    return result

@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel a booking"""
    db = get_database()
    
    booking = await db.bookings.find_one({
        "booking_id": booking_id,
        "user_id": current_user["user_id"]
    })
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking["status"] != BookingStatus.PENDING:
        raise HTTPException(
            status_code=400, 
            detail="Only pending bookings can be cancelled"
        )
    
    await db.bookings.update_one(
        {"booking_id": booking_id},
        {"$set": {"status": BookingStatus.CANCELLED}}
    )
    
    return {"message": "Booking cancelled successfully"}