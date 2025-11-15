#!/usr/bin/env python3
"""Create sample ARGO data for testing."""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import numpy as np
import xarray as xr

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.models.float import ARGOFloat
from app.models.profile import Profile
from app.models.measurement import Measurement
from app.models.bgc_data import BGCData

logger = get_logger(__name__)


def create_sample_netcdf_files():
    """Create sample NetCDF files with realistic ARGO data."""
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    files_created = []
    
    # Create data for the last 7 days
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        
        # Create directory structure
        day_dir = data_dir / str(date.year) / f"{date.month:02d}" / f"{date.day:02d}"
        day_dir.mkdir(parents=True, exist_ok=True)
        
        # Create 3 sample profiles per day
        for j in range(3):
            float_id = f"590{i:02d}{j:02d}"
            filename = f"argo_profile_{float_id}_001.nc"
            file_path = day_dir / filename
            
            if not file_path.exists():
                # Generate realistic oceanographic data
                n_levels = np.random.randint(50, 150)
                pressure = np.linspace(0, 2000, n_levels)
                
                # Realistic temperature profile (warm at surface, cold at depth)
                surface_temp = np.random.uniform(15, 28)  # Surface temperature
                temperature = surface_temp * np.exp(-pressure / 1000) + np.random.normal(0, 0.3, n_levels)
                temperature = np.maximum(temperature, 2)  # Minimum 2°C
                
                # Realistic salinity profile
                surface_salinity = np.random.uniform(34, 36)
                salinity = surface_salinity + (pressure / 2000) * np.random.uniform(-0.5, 0.5) + np.random.normal(0, 0.1, n_levels)
                salinity = np.maximum(salinity, 33)  # Minimum salinity
                
                # BGC data (only for some profiles)
                has_bgc = np.random.choice([True, False], p=[0.3, 0.7])
                
                # Random location (global coverage)
                latitude = np.random.uniform(-60, 60)
                longitude = np.random.uniform(-180, 180)
                
                # Create xarray dataset
                ds_vars = {
                    'PRES': (['N_LEVELS'], pressure),
                    'TEMP': (['N_LEVELS'], temperature),
                    'PSAL': (['N_LEVELS'], salinity),
                }
                
                if has_bgc:
                    # Add BGC variables
                    oxygen = 300 - (pressure / 10) + np.random.normal(0, 10, n_levels)
                    oxygen = np.maximum(oxygen, 50)  # Minimum oxygen
                    
                    chlorophyll = np.maximum(0.1, 2 * np.exp(-pressure / 100) + np.random.normal(0, 0.1, n_levels))
                    
                    ds_vars.update({
                        'DOXY': (['N_LEVELS'], oxygen),
                        'CHLA': (['N_LEVELS'], chlorophyll),
                    })
                
                ds = xr.Dataset(ds_vars, coords={'N_LEVELS': range(n_levels)})
                
                # Add global attributes
                ds.attrs.update({
                    'title': 'Sample ARGO Profile',
                    'platform_number': float_id,
                    'cycle_number': 1,
                    'latitude': latitude,
                    'longitude': longitude,
                    'juld': (date - datetime(1950, 1, 1)).total_seconds() / 86400,  # Julian day
                    'date_creation': datetime.now().isoformat(),
                    'institution': 'WavyAI Sample Data',
                    'project_name': 'ARGO_GLOBAL',
                    'pi_name': 'Sample PI',
                    'data_centre': 'SAMPLE',
                })
                
                # Save to NetCDF
                ds.to_netcdf(file_path)
                logger.info(f"Created sample file: {filename}")
                files_created.append(str(file_path))
    
    return files_created


def load_sample_data_to_db():
    """Load sample data directly into the database."""
    db = SessionLocal()
    
    try:
        # Create sample floats
        floats_data = []
        for i in range(10):
            float_id = f"590{i:04d}"
            
            # Random deployment location
            deploy_lat = np.random.uniform(-60, 60)
            deploy_lon = np.random.uniform(-180, 180)
            
            # Random deployment date (last 2 years)
            deploy_date = datetime.now() - timedelta(days=np.random.randint(30, 730))
            last_profile = datetime.now() - timedelta(days=np.random.randint(0, 30))
            
            float_obj = ARGOFloat(
                id=uuid.uuid4(),
                float_id=float_id,
                platform_number=float_id,
                wmo_number=f"59{i:05d}",
                name=f"ARGO Float {float_id}",
                project_name=np.random.choice(['ARGO_GLOBAL', 'ARGO_ATLANTIC', 'ARGO_PACIFIC']),
                pi_name=f"Sample PI {i+1}",
                data_center='SAMPLE',
                deployment_date=deploy_date,
                deployment_latitude=deploy_lat,
                deployment_longitude=deploy_lon,
                last_profile_date=last_profile,
                last_latitude=deploy_lat + np.random.uniform(-5, 5),
                last_longitude=deploy_lon + np.random.uniform(-10, 10),
                current_status=np.random.choice(['active', 'inactive'], p=[0.8, 0.2]),
            )
            
            db.add(float_obj)
            floats_data.append(float_obj)
        
        db.commit()
        
        # Create sample profiles for each float
        profiles_created = 0
        measurements_created = 0
        
        for float_obj in floats_data:
            # Create 5-10 profiles per float
            num_profiles = np.random.randint(5, 11)
            
            for profile_num in range(1, num_profiles + 1):
                # Random profile date
                profile_date = float_obj.deployment_date + timedelta(days=profile_num * 10)
                
                # Random location near deployment
                lat = float_obj.deployment_latitude + np.random.uniform(-2, 2)
                lon = float_obj.deployment_longitude + np.random.uniform(-3, 3)
                
                # Create profile
                profile = Profile(
                    id=uuid.uuid4(),
                    float_id=float_obj.id,
                    profile_number=profile_num,
                    profile_date=profile_date,
                    latitude=lat,
                    longitude=lon,
                    has_temperature=True,
                    has_salinity=True,
                    has_pressure=True,
                    has_bgc_data=np.random.choice([True, False], p=[0.3, 0.7]),
                    summary=f"ARGO profile {profile_num} from float {float_obj.float_id} with temperature and salinity measurements"
                )
                
                db.add(profile)
                db.flush()  # Get the profile ID
                
                # Create measurements
                n_levels = np.random.randint(50, 150)
                pressure = np.linspace(5, 2000, n_levels)
                
                # Realistic temperature profile
                surface_temp = np.random.uniform(15, 28)
                temperature = surface_temp * np.exp(-pressure / 1000) + np.random.normal(0, 0.3, n_levels)
                temperature = np.maximum(temperature, 2)
                
                # Realistic salinity profile
                surface_salinity = np.random.uniform(34, 36)
                salinity = surface_salinity + (pressure / 2000) * np.random.uniform(-0.5, 0.5) + np.random.normal(0, 0.1, n_levels)
                salinity = np.maximum(salinity, 33)
                
                for level in range(n_levels):
                    measurement = Measurement(
                        id=uuid.uuid4(),
                        profile_id=profile.id,
                        level=level,
                        pressure=float(pressure[level]),
                        depth=float(pressure[level] * 1.02),  # Approximate depth
                        temperature=float(temperature[level]),
                        salinity=float(salinity[level]),
                        pressure_measured=float(pressure[level]),
                        temperature_qc=1,
                        salinity_qc=1,
                        pressure_qc=1,
                    )
                    db.add(measurement)
                    measurements_created += 1
                
                # Add BGC data if applicable
                if profile.has_bgc_data:
                    oxygen = 300 - (pressure / 10) + np.random.normal(0, 10, n_levels)
                    oxygen = np.maximum(oxygen, 50)
                    
                    chlorophyll = np.maximum(0.1, 2 * np.exp(-pressure / 100) + np.random.normal(0, 0.1, n_levels))
                    
                    for level in range(n_levels):
                        bgc_data = BGCData(
                            id=uuid.uuid4(),
                            profile_id=profile.id,
                            level=level,
                            pressure=float(pressure[level]),
                            depth=float(pressure[level] * 1.02),
                            oxygen=float(oxygen[level]),
                            chlorophyll=float(chlorophyll[level]),
                            oxygen_qc=1,
                            chlorophyll_qc=1,
                        )
                        db.add(bgc_data)
                
                profiles_created += 1
        
        # Update profile statistics
        for profile in db.query(Profile).all():
            measurements = db.query(Measurement).filter(Measurement.profile_id == profile.id).all()
            if measurements:
                pressures = [m.pressure for m in measurements if m.pressure]
                if pressures:
                    profile.number_of_levels = len(measurements)
                    profile.pressure_min = min(pressures)
                    profile.pressure_max = max(pressures)
                    profile.depth_min = min(m.depth for m in measurements if m.depth)
                    profile.depth_max = max(m.depth for m in measurements if m.depth)
        
        db.commit()
        
        logger.info(f"Created {len(floats_data)} floats, {profiles_created} profiles, {measurements_created} measurements")
        
        return {
            'floats': len(floats_data),
            'profiles': profiles_created,
            'measurements': measurements_created
        }
        
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function to create sample data."""
    logger.info("Creating sample ARGO data...")
    
    # Create NetCDF files
    files = create_sample_netcdf_files()
    logger.info(f"Created {len(files)} sample NetCDF files")
    
    # Load data to database
    stats = load_sample_data_to_db()
    
    logger.info("Sample data creation completed!")
    logger.info(f"Statistics: {stats}")


if __name__ == "__main__":
    main()
