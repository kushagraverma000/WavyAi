"""Measurement model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Float, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Measurement(Base):
    """Measurement model for temperature, salinity, pressure data."""

    __tablename__ = "measurements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False, index=True)
    
    # Level information
    level = Column(Integer, nullable=False, index=True)  # Depth level index
    pressure = Column(Float, nullable=True)  # Decibars
    depth = Column(Float, nullable=True, index=True)  # Meters (computed from pressure)

    # Measurements
    temperature = Column(Float, nullable=True)  # Degrees Celsius
    salinity = Column(Float, nullable=True)  # PSU
    pressure_measured = Column(Float, nullable=True)  # Decibars

    # Quality flags
    pressure_qc = Column(Integer, nullable=True)
    temperature_qc = Column(Integer, nullable=True)
    salinity_qc = Column(Integer, nullable=True)

    # Adjusted values (if available)
    temperature_adjusted = Column(Float, nullable=True)
    salinity_adjusted = Column(Float, nullable=True)
    pressure_adjusted = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("Profile", back_populates="measurements")

    def __repr__(self) -> str:
        return f"<Measurement(profile_id='{self.profile_id}', level={self.level}, depth={self.depth}m)>"

