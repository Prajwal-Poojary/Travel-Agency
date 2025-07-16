from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

# Import configuration and database
from config import settings
from database import connect_to_mongo, close_mongo_connection
from models import HealthResponse

# Import routers
from routers import auth, destinations, bookings, reviews, ai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Advanced Travel Platform API...")
    try:
        await connect_to_mongo()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_mongo_connection()

# Create FastAPI app
app = FastAPI(
    title="Advanced Travel Platform API",
    description="Complete travel platform with AI integration, virtual tours, and weather data",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(destinations.router)
app.include_router(bookings.router)
app.include_router(reviews.router)
app.include_router(ai.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Advanced Travel Platform API v2.0",
        "status": "operational",
        "features": [
            "AI-powered recommendations",
            "Complete booking system",
            "User reviews and ratings",
            "Weather integration",
            "Real-time chat assistant"
        ],
        "docs": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }

# Health check endpoint
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    from database import database
    from services.ai_service import ai_service
    from services.weather_service import weather_service
    
    # Check database connection
    db_status = "connected" if database.client else "disconnected"
    
    # Check AI service
    ai_status = "available" if ai_service.model else "limited"
    
    # Check weather service
    weather_status = "available" if weather_service.api_key else "mock_data"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        services={
            "database": db_status,
            "ai_service": ai_status,
            "weather_service": weather_status
        }
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# 404 handler
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )