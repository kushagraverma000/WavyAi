from sqlalchemy import Boolean, Column, Date, DateTime, Float as SAFloat, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .db import Base


class Float(Base):
    __tablename__ = "floats"

    id = Column(Integer, primary_key=True, index=True)
    float_id = Column(String, unique=True, index=True, nullable=False)
    platform_number = Column(String, index=True, nullable=True)
    wmo_number = Column(String, nullable=True)
    name = Column(String, nullable=True)
    project_name = Column(String, nullable=True)
    deployment_date = Column(DateTime, nullable=True)
    deployment_latitude = Column(SAFloat, nullable=True)
    deployment_longitude = Column(SAFloat, nullable=True)
    last_profile_date = Column(DateTime, nullable=True)
    last_latitude = Column(SAFloat, nullable=True)
    last_longitude = Column(SAFloat, nullable=True)
    current_status = Column(String, nullable=True)

    profiles = relationship("Profile", back_populates="float", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    float_id = Column(Integer, ForeignKey("floats.id", ondelete="CASCADE"))
    profile_identifier = Column(String, index=True)
    profile_number = Column(Integer, nullable=True)
    profile_date = Column(DateTime, index=True)
    latitude = Column(SAFloat)
    longitude = Column(SAFloat)
    number_of_levels = Column(Integer, nullable=True)
    pressure_min = Column(SAFloat, nullable=True)
    pressure_max = Column(SAFloat, nullable=True)
    depth_min = Column(SAFloat, nullable=True)
    depth_max = Column(SAFloat, nullable=True)
    has_temperature = Column(Boolean, default=False)
    has_salinity = Column(Boolean, default=False)
    has_pressure = Column(Boolean, default=False)
    has_bgc_data = Column(Boolean, default=False)

    float = relationship("Float", back_populates="profiles")
    measurements = relationship("ProfileMeasurement", back_populates="profile", cascade="all, delete-orphan")


class ProfileMeasurement(Base):
    __tablename__ = "profile_measurements"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), index=True)
    level_index = Column(Integer)
    depth = Column(SAFloat, nullable=True)
    pressure = Column(SAFloat, nullable=True)
    temperature = Column(SAFloat, nullable=True)
    salinity = Column(SAFloat, nullable=True)

    profile = relationship("Profile", back_populates="measurements")


class DaySummary(Base):
    __tablename__ = "day_summaries"

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, index=True)
    year = Column(Integer, index=True)
    month = Column(Integer, index=True)
    day = Column(Integer, index=True)
    summary_text = Column(String)
