"""Float endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.float import FloatResponse, FloatListResponse
from app.models.float import ARGOFloat

router = APIRouter()
logger = get_logger(__name__)


@router.get("", response_model=FloatListResponse)
async def get_floats(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get floats with filtering."""
    try:
        if db is None:
            raise HTTPException(
                status_code=503,
                detail="Database not available. Use /api/v1/simple/floats/list endpoint for prototype data."
            )
        
        query_obj = db.query(ARGOFloat)

        # Apply filters
        if status:
            query_obj = query_obj.filter(ARGOFloat.current_status == status)

        # Get total count
        total = query_obj.count()

        # Apply pagination
        floats = query_obj.offset((page - 1) * page_size).limit(page_size).all()

        return FloatListResponse(
            floats=[FloatResponse.model_validate(f) for f in floats],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error("Failed to get floats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get floats: {str(e)}")


@router.get("/{float_id}", response_model=FloatResponse)
async def get_float(float_id: str, db: Session = Depends(get_db)):
    """Get a single float by ID."""
    try:
        if db is None:
            raise HTTPException(
                status_code=503,
                detail="Database not available. Use /api/v1/simple/floats endpoint for prototype data."
            )
        
        float_obj = db.query(ARGOFloat).filter(ARGOFloat.float_id == float_id).first()
        if not float_obj:
            raise HTTPException(status_code=404, detail="Float not found")
        return FloatResponse.model_validate(float_obj)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get float", error=str(e), float_id=float_id)
        raise HTTPException(status_code=500, detail=f"Failed to get float: {str(e)}")

