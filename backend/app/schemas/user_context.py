"""User context schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class UserContextResponse(BaseModel):
    """User context response schema."""

    id: UUID
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    user_type: Optional[str] = None
    expertise_level: Optional[str] = None
    query_intent: Optional[str] = None
    preferred_output_format: Optional[str] = None
    preferred_visualization_type: Optional[str] = None
    interaction_history: Optional[List[Dict[str, Any]]] = None
    recent_queries: Optional[List[str]] = None
    preferred_regions: Optional[List[str]] = None
    preferred_parameters: Optional[List[str]] = None
    total_queries: int
    last_query_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserContextUpdate(BaseModel):
    """User context update schema."""

    user_type: Optional[str] = None
    expertise_level: Optional[str] = None
    query_intent: Optional[str] = None
    preferred_output_format: Optional[str] = None
    preferred_visualization_type: Optional[str] = None

