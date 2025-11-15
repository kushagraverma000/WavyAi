"""Float schemas."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field


class FloatResponse(BaseModel):
    """Float response schema."""

    id: UUID
    float_id: str
    platform_number: str
    wmo_number: Optional[str] = None
    name: Optional[str] = None
    project_name: Optional[str] = None
    deployment_date: Optional[datetime] = None
    deployment_latitude: Optional[float] = None
    deployment_longitude: Optional[float] = None
    last_profile_date: Optional[datetime] = None
    last_latitude: Optional[float] = None
    last_longitude: Optional[float] = None
    current_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class FloatListResponse(BaseModel):
    """Float list response schema."""

    floats: List[FloatResponse]
    total: int
    page: int
    page_size: int

