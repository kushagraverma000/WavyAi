"""Profile endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.profile import ProfileResponse, ProfileListResponse
from app.models.profile import Profile
from sqlalchemy import and_

router = APIRouter()
logger = get_logger(__name__)


@router.get("", response_model=ProfileListResponse)
async def get_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    float_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_latitude: Optional[float] = None,
    max_latitude: Optional[float] = None,
    min_longitude: Optional[float] = None,
    max_longitude: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Get profiles with filtering."""
    try:
        if db is None:
            # Fallback to simple endpoint - return empty result or raise redirect
            from fastapi import HTTPException
            raise HTTPException(
                status_code=503,
                detail="Database not available. Use /api/v1/simple/profiles endpoint for prototype data."
            )
        
        query_obj = db.query(Profile)

        # Apply filters
        if float_id:
            query_obj = query_obj.filter(Profile.float_id == float_id)
        if start_date:
            query_obj = query_obj.filter(Profile.profile_date >= start_date)
        if end_date:
            query_obj = query_obj.filter(Profile.profile_date <= end_date)
        if min_latitude:
            query_obj = query_obj.filter(Profile.latitude >= min_latitude)
        if max_latitude:
            query_obj = query_obj.filter(Profile.latitude <= max_latitude)
        if min_longitude:
            query_obj = query_obj.filter(Profile.longitude >= min_longitude)
        if max_longitude:
            query_obj = query_obj.filter(Profile.longitude <= max_longitude)

        # Get total count
        total = query_obj.count()

        # Apply pagination
        profiles = query_obj.offset((page - 1) * page_size).limit(page_size).all()

        return ProfileListResponse(
            profiles=[ProfileResponse.model_validate(p) for p in profiles],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error("Failed to get profiles", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get profiles: {str(e)}")


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: str, db: Session = Depends(get_db)):
    """Get a single profile by ID."""
    try:
        if db is None:
            raise HTTPException(
                status_code=503,
                detail="Database not available. Use /api/v1/simple/profiles/{profile_id} endpoint for prototype data."
            )
        
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return ProfileResponse.model_validate(profile)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get profile", error=str(e), profile_id=profile_id)
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

