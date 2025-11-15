"""Profile model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Float, Integer, String, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
import uuid

from app.core.database import Base


class Profile(Base):
    """Profile model representing a single ARGO profile."""

    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    float_id = Column(UUID(as_uuid=True), ForeignKey("argo_floats.id"), nullable=False, index=True)
    profile_number = Column(Integer, nullable=False, index=True)
    
    # Temporal information
    profile_date = Column(DateTime, nullable=False, index=True)
    juld = Column(Float, nullable=True)  # Julian day
    juld_qc = Column(Integer, nullable=True)  # Quality flag

    # Spatial information
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    location = Column(Geometry("POINT", srid=4326), nullable=True)  # PostGIS geometry
    
    # Quality flags
    position_qc = Column(Integer, nullable=True)
    profile_qc = Column(Integer, nullable=True)

    # Profile characteristics
    number_of_levels = Column(Integer, nullable=True)
    pressure_min = Column(Float, nullable=True)
    pressure_max = Column(Float, nullable=True)
    depth_min = Column(Float, nullable=True)
    depth_max = Column(Float, nullable=True)

    # Data availability flags
    has_temperature = Column(Boolean, default=False, nullable=False)
    has_salinity = Column(Boolean, default=False, nullable=False)
    has_pressure = Column(Boolean, default=False, nullable=False)
    has_bgc_data = Column(Boolean, default=False, nullable=False)

    # Embedding for semantic search
    embedding = Column(Text, nullable=True)  # JSON array of floats

    # Summary text for RAG
    summary = Column(Text, nullable=True)

    # Additional metadata
    profile_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    float_obj = relationship("ARGOFloat", back_populates="profiles")
    measurements = relationship("Measurement", back_populates="profile", cascade="all, delete-orphan")
    bgc_data = relationship("BGCData", back_populates="profile", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Profile(float_id='{self.float_id}', profile_number={self.profile_number}, date='{self.profile_date}')>"

