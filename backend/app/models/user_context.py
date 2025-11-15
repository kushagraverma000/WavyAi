"""User Context model for storing user preferences and history."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class UserContext(Base):
    """User Context model for storing user preferences, history, and detected user type."""

    __tablename__ = "user_contexts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User identification (session ID or user ID if authenticated)
    session_id = Column(String(255), nullable=True, index=True)
    user_id = Column(String(255), nullable=True, index=True)

    # Detected user type
    user_type = Column(String(50), nullable=True, index=True)  # researcher, student, manager, fishery, ngo, shipping
    expertise_level = Column(String(20), nullable=True)  # beginner, intermediate, advanced, expert

    # Query intent
    query_intent = Column(String(50), nullable=True)  # data_exploration, decision_support, learning, monitoring, export

    # Preferences
    preferred_output_format = Column(String(50), nullable=True)  # json, csv, netcdf, pdf, visual
    preferred_visualization_type = Column(String(50), nullable=True)  # map, chart, table, report

    # Interaction history (stored as JSON)
    interaction_history = Column(JSON, nullable=True)  # List of {query, response, timestamp}
    recent_queries = Column(JSON, nullable=True)  # Last N queries
    saved_searches = Column(JSON, nullable=True)  # Saved search configurations

    # Detected entities from queries
    preferred_regions = Column(JSON, nullable=True)  # List of regions user queries
    preferred_parameters = Column(JSON, nullable=True)  # List of parameters user is interested in
    preferred_time_ranges = Column(JSON, nullable=True)  # Typical time ranges queried

    # Statistics
    total_queries = Column(Integer, default=0, nullable=False)
    last_query_date = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<UserContext(session_id='{self.session_id}', user_type='{self.user_type}')>"

