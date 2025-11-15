"""Profile schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    """Profile response schema."""

    id: UUID
    float_id: UUID
    profile_number: int
    profile_date: datetime
    latitude: float
    longitude: float
    number_of_levels: Optional[int] = None
    pressure_min: Optional[float] = None
    pressure_max: Optional[float] = None
    depth_min: Optional[float] = None
    depth_max: Optional[float] = None
    has_temperature: bool
    has_salinity: bool
    has_pressure: bool
    has_bgc_data: bool
    summary: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ProfileListResponse(BaseModel):
    """Profile list response schema."""

    profiles: List[ProfileResponse]
    total: int
    page: int
    page_size: int

