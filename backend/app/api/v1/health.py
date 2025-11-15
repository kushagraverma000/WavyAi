"""Health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        if db is None:
            # Database not available, but app is running (prototype mode)
            return {"status": "healthy", "database": "not_connected", "mode": "prototype"}
        
        # Test database connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected", "mode": "full"}
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {"status": "healthy", "database": "not_connected", "mode": "prototype", "error": str(e)}

