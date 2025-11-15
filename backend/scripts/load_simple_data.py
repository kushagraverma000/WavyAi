#!/usr/bin/env python3
"""Load simple sample data for testing."""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import random

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.float import ARGOFloat
from app.models.profile import Profile
from app.models.measurement import Measurement
from app.models.bgc_data import BGCData

def load_simple_data():
    """Load simple sample data."""
    db = SessionLocal()
    
    try:
        print("Loading simple sample data...")
        
        # Create 5 sample floats
        floats = []
        for i in range(5):
            float_obj = ARGOFloat(
                id=uuid.uuid4(),
                float_id=f"590{i:04d}",
                platform_number=f"590{i:04d}",
                wmo_number=f"59{i:05d}",
                name=f"ARGO Float {i+1}",
                project_name="ARGO_GLOBAL",
                pi_name=f"Sample PI {i+1}",
                data_center="SAMPLE",
                deployment_date=datetime.now() - timedelta(days=random.randint(30, 365)),
                deployment_latitude=random.uniform(-60, 60),
                deployment_longitude=random.uniform(-180, 180),
                last_profile_date=datetime.now() - timedelta(days=random.randint(0, 30)),
                last_latitude=random.uniform(-60, 60),
                last_longitude=random.uniform(-180, 180),
                current_status=random.choice(['active', 'inactive']),
            )
            db.add(float_obj)
            floats.append(float_obj)
        
        db.commit()
        print(f"Created {len(floats)} floats")
        
        # Create profiles for each float
        profiles_created = 0
        measurements_created = 0
        
        for float_obj in floats:
            # Create 3 profiles per float
            for profile_num in range(1, 4):
                profile_date = float_obj.deployment_date + timedelta(days=profile_num * 10)
                
                profile = Profile(
                    id=uuid.uuid4(),
                    float_id=float_obj.id,
                    profile_number=profile_num,
                    profile_date=profile_date,
                    latitude=float_obj.deployment_latitude + random.uniform(-2, 2),
                    longitude=float_obj.deployment_longitude + random.uniform(-3, 3),
                    has_temperature=True,
                    has_salinity=True,
                    has_pressure=True,
                    has_bgc_data=random.choice([True, False]),
                    number_of_levels=50,
                    pressure_min=5.0,
                    pressure_max=2000.0,
                    depth_min=5.0,
                    depth_max=2000.0,
                    summary=f"ARGO profile {profile_num} from float {float_obj.float_id} with temperature and salinity measurements"
                )
                
                db.add(profile)
                db.flush()  # Get the profile ID
                
                # Create 20 measurements per profile
                for level in range(20):
                    pressure = 5 + (level * 100)  # 5, 105, 205, ... 1905
                    depth = pressure * 1.02
                    
                    # Realistic temperature (warm at surface, cold at depth)
                    temperature = 25 - (pressure / 100) + random.uniform(-1, 1)
                    temperature = max(temperature, 2)  # Minimum 2°C
                    
                    # Realistic salinity
                    salinity = 35 + random.uniform(-0.5, 0.5)
                    
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
                    measurements_created += 1
                
                # Add BGC data if applicable
                if profile.has_bgc_data:
                    for level in range(10):  # Fewer BGC measurements
                        pressure = 5 + (level * 200)
                        depth = pressure * 1.02
                        
                        bgc_data = BGCData(
                            id=uuid.uuid4(),
                            profile_id=profile.id,
                            level=level,
                            pressure=pressure,
                            depth=depth,
                            oxygen=300 - (pressure / 10) + random.uniform(-10, 10),
                            chlorophyll=max(0.1, 2 * (1 - pressure/1000) + random.uniform(-0.1, 0.1)),
                            oxygen_qc=1,
                            chlorophyll_qc=1,
                        )
                        db.add(bgc_data)
                
                profiles_created += 1
        
        db.commit()
        
        print(f"Created {profiles_created} profiles")
        print(f"Created {measurements_created} measurements")
        print("Sample data loaded successfully!")
        
        return {
            'floats': len(floats),
            'profiles': profiles_created,
            'measurements': measurements_created
        }
        
    except Exception as e:
        print(f"Error loading sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_simple_data()
