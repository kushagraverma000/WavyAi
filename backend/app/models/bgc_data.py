"""BGC (Biogeochemical) Data model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Float, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class BGCData(Base):
    """BGC Data model for biogeochemical measurements."""

    __tablename__ = "bgc_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False, index=True)
    
    # Level information
    level = Column(Integer, nullable=False, index=True)  # Depth level index
    pressure = Column(Float, nullable=True)  # Decibars
    depth = Column(Float, nullable=True, index=True)  # Meters

    # BGC Measurements
    oxygen = Column(Float, nullable=True)  # Micromoles per kg
    chlorophyll = Column(Float, nullable=True)  # mg/m³
    nitrate = Column(Float, nullable=True)  # Micromoles per kg
    ph = Column(Float, nullable=True)  # pH units
    cdom = Column(Float, nullable=True)  # ppb
    bbp = Column(Float, nullable=True)  # m⁻¹
    downwelling_irradiance = Column(Float, nullable=True)  # W/m²

    # Quality flags
    oxygen_qc = Column(Integer, nullable=True)
    chlorophyll_qc = Column(Integer, nullable=True)
    nitrate_qc = Column(Integer, nullable=True)
    ph_qc = Column(Integer, nullable=True)
    cdom_qc = Column(Integer, nullable=True)
    bbp_qc = Column(Integer, nullable=True)

    # Adjusted values (if available)
    oxygen_adjusted = Column(Float, nullable=True)
    chlorophyll_adjusted = Column(Float, nullable=True)
    nitrate_adjusted = Column(Float, nullable=True)
    ph_adjusted = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("Profile", back_populates="bgc_data")

    def __repr__(self) -> str:
        return f"<BGCData(profile_id='{self.profile_id}', level={self.level}, depth={self.depth}m)>"

