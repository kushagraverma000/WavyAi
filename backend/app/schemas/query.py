"""Query schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Query request schema."""

    query: str = Field(..., description="Natural language query")
    session_id: Optional[str] = Field(None, description="Session ID for user context")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class QueryResponse(BaseModel):
    """Query response schema."""

    response: str = Field(..., description="AI-generated response")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Data sources used")
    visualization: Optional[Dict[str, Any]] = Field(None, description="Visualization configuration")
    user_type: Optional[str] = Field(None, description="Detected user type")
    query_intent: Optional[str] = Field(None, description="Detected query intent")
    entities: Optional[Dict[str, Any]] = Field(None, description="Extracted entities")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

