from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session_sqlite import get_db  # Use SQLite session for local development
from app.core.config import settings
import redis
import time

router = APIRouter()

@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check endpoint
    """
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check Redis connection (optional for local development)
    redis_status = "healthy"
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
        # For local development, Redis is optional
        if "Connection refused" in str(e):
            redis_status = "disabled (local development)"
    
    # Check overall system health (Redis is optional for local dev)
    overall_status = "healthy" if db_status == "healthy" else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": time.time(),
        "version": "1.0.0",
        "services": {
            "database": db_status,
            "redis": redis_status,
            "api": "healthy"
        },
        "environment": settings.PROJECT_NAME
    }

@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for load balancers
    """
    return {"pong": time.time()}
