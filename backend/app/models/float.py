"""ARGO Float model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Float, Integer, String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class ARGOFloat(Base):
    """ARGO Float model."""

    __tablename__ = "argo_floats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    float_id = Column(String(50), unique=True, nullable=False, index=True)
    platform_number = Column(String(50), nullable=False, index=True)
    wmo_number = Column(String(50), nullable=True, index=True)
    name = Column(String(255), nullable=True)

    # Float metadata
    project_name = Column(String(255), nullable=True)
    pi_name = Column(String(255), nullable=True)
    data_center = Column(String(100), nullable=True)
    sensor_type = Column(String(100), nullable=True)

    # Deployment information
    deployment_date = Column(DateTime, nullable=True)
    deployment_latitude = Column(Float, nullable=True)
    deployment_longitude = Column(Float, nullable=True)
    deployment_location = Column(String(255), nullable=True)

    # Current status
    last_profile_date = Column(DateTime, nullable=True)
    last_latitude = Column(Float, nullable=True)
    last_longitude = Column(Float, nullable=True)
    current_status = Column(String(50), nullable=True)  # active, inactive, lost

    # Technical specifications
    cycle_time = Column(Integer, nullable=True)  # days
    parking_depth = Column(Float, nullable=True)  # meters
    profile_depth = Column(Float, nullable=True)  # meters

    # Additional metadata
    float_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    profiles = relationship("Profile", back_populates="float_obj", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ARGOFloat(float_id='{self.float_id}', platform_number='{self.platform_number}')>"

