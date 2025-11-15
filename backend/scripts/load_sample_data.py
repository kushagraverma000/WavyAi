"""Load sample data into the database."""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.float import ARGOFloat
from app.models.profile import Profile
from app.models.measurement import Measurement
from app.models.bgc_data import BGCData

# Sample float data
SAMPLE_FLOATS = [
    {
        "float_id": "6902903",
        "platform_number": "6902903",
        "wmo_number": "6902903",
        "name": "ARGO Float 6902903",
        "project_name": "ARGO",
        "deployment_date": datetime(2020, 1, 15),
        "deployment_latitude": 25.0,
        "deployment_longitude": -70.0,
        "current_status": "active",
        "cycle_time": 10,
        "parking_depth": 1000.0,
        "profile_depth": 2000.0,
    },
    {
        "float_id": "6902904",
        "platform_number": "6902904",
        "wmo_number": "6902904",
        "name": "ARGO Float 6902904",
        "project_name": "ARGO",
        "deployment_date": datetime(2020, 2, 20),
        "deployment_latitude": 30.0,
        "deployment_longitude": -75.0,
        "current_status": "active",
        "cycle_time": 10,
        "parking_depth": 1000.0,
        "profile_depth": 2000.0,
    },
]


def create_sample_profile(
    db: Session,
    float_obj: ARGOFloat,
    profile_number: int,
    profile_date: datetime,
    latitude: float,
    longitude: float,
) -> Profile:
    """Create a sample profile with measurements."""
    profile = Profile(
        id=uuid.uuid4(),
        float_id=float_obj.id,
        profile_number=profile_number,
        profile_date=profile_date,
        latitude=latitude,
        longitude=longitude,
        number_of_levels=50,
        pressure_min=0.0,
        pressure_max=2000.0,
        depth_min=0.0,
        depth_max=2000.0,
        has_temperature=True,
        has_salinity=True,
        has_pressure=True,
        has_bgc_data=random.choice([True, False]),
        summary=f"Profile {profile_number} from float {float_obj.float_id}",
    )
    db.add(profile)
    db.flush()

    # Create measurements
    for level in range(50):
        depth = level * 40  # 0 to 1960 meters
        pressure = depth / 10.0  # Approximate pressure in decibars
        
        # Temperature profile (decreases with depth)
        temperature = 25.0 - (depth / 100.0) + random.uniform(-1, 1)
        
        # Salinity profile (varies with depth)
        salinity = 35.0 + random.uniform(-0.5, 0.5)
        
        measurement = Measurement(
            id=uuid.uuid4(),
            profile_id=profile.id,
            level=level,
            pressure=pressure,
            depth=depth,
            temperature=temperature,
            salinity=salinity,
            pressure_measured=pressure,
            temperature_qc=1,
            salinity_qc=1,
            pressure_qc=1,
        )
        db.add(measurement)

        # Add BGC data for some profiles
        if profile.has_bgc_data and level % 5 == 0:
            bgc_data = BGCData(
                id=uuid.uuid4(),
                profile_id=profile.id,
                level=level,
                pressure=pressure,
                depth=depth,
                oxygen=200.0 - (depth / 20.0) + random.uniform(-10, 10),
                chlorophyll=0.5 + random.uniform(-0.2, 0.2),
                nitrate=30.0 + random.uniform(-5, 5),
                ph=8.0 + random.uniform(-0.1, 0.1),
                oxygen_qc=1,
                chlorophyll_qc=1,
                nitrate_qc=1,
                ph_qc=1,
            )
            db.add(bgc_data)

    return profile


def load_sample_data():
    """Load sample data into the database."""
    db = SessionLocal()
    try:
        print("Loading sample data...")
        
        # Create floats
        float_objects = []
        for float_data in SAMPLE_FLOATS:
            float_obj = ARGOFloat(
                id=uuid.uuid4(),
                **float_data,
                last_profile_date=datetime.now() - timedelta(days=5),
                last_latitude=float_data["deployment_latitude"] + random.uniform(-2, 2),
                last_longitude=float_data["deployment_longitude"] + random.uniform(-2, 2),
            )
            db.add(float_obj)
            float_objects.append(float_obj)
        
        db.commit()
        print(f"Created {len(float_objects)} floats")
        
        # Create profiles for each float
        profile_count = 0
        for float_obj in float_objects:
            # Create 10 profiles per float
            for i in range(10):
                profile_date = float_obj.deployment_date + timedelta(days=i * 10)
                latitude = float_obj.deployment_latitude + random.uniform(-1, 1)
                longitude = float_obj.deployment_longitude + random.uniform(-1, 1)
                
                profile = create_sample_profile(
                    db=db,
                    float_obj=float_obj,
                    profile_number=i + 1,
                    profile_date=profile_date,
                    latitude=latitude,
                    longitude=longitude,
                )
                profile_count += 1
        
        db.commit()
        print(f"Created {profile_count} profiles with measurements")
        print("Sample data loaded successfully!")
        
    except Exception as e:
        print(f"Error loading sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_sample_data()

