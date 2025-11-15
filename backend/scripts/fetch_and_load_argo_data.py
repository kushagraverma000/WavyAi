#!/usr/bin/env python3
"""
Fetch and load ARGO data from official sources.
This script downloads recent ARGO data and loads it into the database.
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, engine
from app.core.logging import get_logger
from app.services.argo_data_fetcher import get_argo_fetcher
from app.core.database import Base
from app.models.float import ARGOFloat
from app.models.profile import Profile
from app.models.measurement import Measurement
from app.models.bgc_data import BGCData
import xarray as xr
import numpy as np
from sqlalchemy.exc import IntegrityError
from uuid import uuid4

logger = get_logger(__name__)


class ARGODataLoader:
    """Load ARGO NetCDF data into the database."""
    
    def __init__(self):
        """Initialize the data loader."""
        self.db = SessionLocal()
        self.fetcher = get_argo_fetcher()
        
    def __del__(self):
        """Clean up database connection."""
        if hasattr(self, 'db'):
            self.db.close()

    async def fetch_and_load_data(self, days_back: int = 30, max_files: int = 50):
        """Fetch recent ARGO data and load it into the database."""
        logger.info("Starting ARGO data fetch and load process")
        
        try:
            # Step 1: Fetch recent profile files
            logger.info(f"Fetching ARGO profiles from last {days_back} days")
            profile_files = await self.fetcher.fetch_recent_profiles(days_back, max_files)
            
            if not profile_files:
                logger.warning("No profile files downloaded")
                return
            
            # Step 2: Fetch float metadata
            logger.info("Fetching float metadata")
            float_metadata = await self.fetcher.fetch_float_metadata()
            
            # Step 3: Load float metadata into database
            logger.info("Loading float metadata into database")
            await self._load_float_metadata(float_metadata)
            
            # Step 4: Load profile data
            logger.info(f"Loading {len(profile_files)} profile files")
            loaded_count = 0
            
            for file_path in profile_files:
                try:
                    if await self._load_profile_file(file_path):
                        loaded_count += 1
                        logger.info(f"Loaded profile {loaded_count}/{len(profile_files)}: {Path(file_path).name}")
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {e}")
                    continue
            
            logger.info(f"Successfully loaded {loaded_count} profiles into database")
            
            # Step 5: Generate summary
            await self._generate_summary()
            
        except Exception as e:
            logger.error(f"Data fetch and load failed: {e}")
            raise
        finally:
            self.db.close()

    async def _load_float_metadata(self, float_metadata_list):
        """Load float metadata into the database."""
        for metadata in float_metadata_list:
            try:
                # Check if float already exists
                existing_float = self.db.query(ARGOFloat).filter(
                    ARGOFloat.platform_number == metadata['platform_number']
                ).first()
                
                if existing_float:
                    # Update existing float
                    for key, value in metadata.items():
                        if hasattr(existing_float, key) and value is not None:
                            setattr(existing_float, key, value)
                else:
                    # Create new float
                    float_obj = ARGOFloat(
                        id=uuid4(),
                        float_id=metadata['platform_number'],
                        platform_number=metadata['platform_number'],
                        wmo_number=metadata.get('wmo_number'),
                        project_name=metadata.get('project_name'),
                        deployment_date=self._parse_date(metadata.get('deployment_date')),
                        deployment_latitude=metadata.get('deployment_latitude'),
                        deployment_longitude=metadata.get('deployment_longitude'),
                        last_profile_date=self._parse_date(metadata.get('last_profile_date')),
                        last_latitude=metadata.get('last_latitude'),
                        last_longitude=metadata.get('last_longitude'),
                        current_status=metadata.get('current_status', 'unknown'),
                    )
                    self.db.add(float_obj)
                
                self.db.commit()
                
            except Exception as e:
                logger.error(f"Failed to load float metadata {metadata.get('platform_number')}: {e}")
                self.db.rollback()
                continue

    async def _load_profile_file(self, file_path: str) -> bool:
        """Load a single ARGO profile NetCDF file."""
        try:
            # Open NetCDF file
            ds = xr.open_dataset(file_path)
            
            # Extract profile metadata
            platform_number = str(ds.attrs.get('platform_number', 'unknown'))
            cycle_number = int(ds.attrs.get('cycle_number', 1))
            
            # Get or create float
            float_obj = self.db.query(ARGOFloat).filter(
                ARGOFloat.platform_number == platform_number
            ).first()
            
            if not float_obj:
                # Create float if it doesn't exist
                float_obj = ARGOFloat(
                    id=uuid4(),
                    float_id=platform_number,
                    platform_number=platform_number,
                    current_status='active'
                )
                self.db.add(float_obj)
                self.db.commit()
                self.db.refresh(float_obj)
            
            # Extract profile data
            latitude = float(ds.attrs.get('latitude', 0))
            longitude = float(ds.attrs.get('longitude', 0))
            profile_date = self._parse_timestamp(ds.attrs.get('juld', datetime.now().timestamp()))
            
            # Check if profile already exists
            existing_profile = self.db.query(Profile).filter(
                Profile.float_id == float_obj.id,
                Profile.profile_number == cycle_number
            ).first()
            
            if existing_profile:
                logger.debug(f"Profile already exists: {platform_number}_{cycle_number}")
                return False
            
            # Create profile
            profile = Profile(
                id=uuid4(),
                float_id=float_obj.id,
                profile_number=cycle_number,
                profile_date=profile_date,
                latitude=latitude,
                longitude=longitude,
                has_temperature='TEMP' in ds.data_vars,
                has_salinity='PSAL' in ds.data_vars,
                has_pressure='PRES' in ds.data_vars,
                has_bgc_data=any(var in ds.data_vars for var in ['DOXY', 'CHLA', 'NITRATE']),
            )
            
            # Calculate depth and level statistics
            if 'PRES' in ds.data_vars:
                pressure_data = ds['PRES'].values
                valid_pressure = pressure_data[~np.isnan(pressure_data)]
                if len(valid_pressure) > 0:
                    profile.number_of_levels = len(valid_pressure)
                    profile.pressure_min = float(np.min(valid_pressure))
                    profile.pressure_max = float(np.max(valid_pressure))
                    
                    # Approximate depth from pressure (depth ≈ pressure / 10)
                    depth_data = valid_pressure / 10.0
                    profile.depth_min = float(np.min(depth_data))
                    profile.depth_max = float(np.max(depth_data))
            
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            
            # Load measurements
            await self._load_measurements(ds, profile)
            
            # Load BGC data if available
            await self._load_bgc_data(ds, profile)
            
            ds.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to load profile file {file_path}: {e}")
            self.db.rollback()
            return False

    async def _load_measurements(self, ds: xr.Dataset, profile: Profile):
        """Load core measurements (T, S, P) from NetCDF dataset."""
        try:
            # Get data arrays
            pressure = ds.get('PRES')
            temperature = ds.get('TEMP')
            salinity = ds.get('PSAL')
            depth = ds.get('DEPTH')
            
            if pressure is None:
                return
            
            pressure_data = pressure.values
            n_levels = len(pressure_data)
            
            # Get other data arrays or create defaults
            temp_data = temperature.values if temperature is not None else np.full(n_levels, np.nan)
            sal_data = salinity.values if salinity is not None else np.full(n_levels, np.nan)
            depth_data = depth.values if depth is not None else pressure_data / 10.0  # Approximate depth
            
            # Load measurements level by level
            for i in range(n_levels):
                if np.isnan(pressure_data[i]):
                    continue
                
                measurement = Measurement(
                    id=uuid4(),
                    profile_id=profile.id,
                    level_number=i + 1,
                    pressure=float(pressure_data[i]),
                    depth=float(depth_data[i]) if not np.isnan(depth_data[i]) else None,
                    temperature=float(temp_data[i]) if not np.isnan(temp_data[i]) else None,
                    salinity=float(sal_data[i]) if not np.isnan(sal_data[i]) else None,
                    temperature_qc=1 if not np.isnan(temp_data[i]) else 9,
                    salinity_qc=1 if not np.isnan(sal_data[i]) else 9,
                )
                
                self.db.add(measurement)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to load measurements: {e}")
            self.db.rollback()

    async def _load_bgc_data(self, ds: xr.Dataset, profile: Profile):
        """Load biogeochemical data from NetCDF dataset."""
        try:
            # BGC variables
            bgc_vars = {
                'DOXY': 'oxygen',
                'CHLA': 'chlorophyll',
                'NITRATE': 'nitrate',
                'PH_IN_SITU_TOTAL': 'ph'
            }
            
            # Check if any BGC data is available
            available_bgc = {var: ds.get(var) for var in bgc_vars.keys() if var in ds.data_vars}
            
            if not available_bgc:
                return
            
            # Get pressure for indexing
            pressure = ds.get('PRES')
            if pressure is None:
                return
            
            pressure_data = pressure.values
            n_levels = len(pressure_data)
            
            # Load BGC data level by level
            for i in range(n_levels):
                if np.isnan(pressure_data[i]):
                    continue
                
                bgc_data = BGCData(
                    id=uuid4(),
                    profile_id=profile.id,
                    level_number=i + 1,
                    pressure=float(pressure_data[i]),
                )
                
                # Add available BGC parameters
                for var_name, attr_name in bgc_vars.items():
                    if var_name in available_bgc:
                        value = available_bgc[var_name].values[i]
                        if not np.isnan(value):
                            setattr(bgc_data, attr_name, float(value))
                
                self.db.add(bgc_data)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to load BGC data: {e}")
            self.db.rollback()

    def _parse_date(self, date_str):
        """Parse date string to datetime object."""
        if not date_str:
            return None
        
        try:
            if isinstance(date_str, str):
                # Try different date formats
                for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%Y%m%d']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
            return None
        except Exception:
            return None

    def _parse_timestamp(self, timestamp):
        """Parse timestamp to datetime object."""
        try:
            if isinstance(timestamp, (int, float)):
                return datetime.fromtimestamp(timestamp)
            return datetime.now()
        except Exception:
            return datetime.now()

    async def _generate_summary(self):
        """Generate and log data summary."""
        try:
            float_count = self.db.query(ARGOFloat).count()
            profile_count = self.db.query(Profile).count()
            measurement_count = self.db.query(Measurement).count()
            bgc_count = self.db.query(BGCData).count()
            
            logger.info("=== ARGO Data Load Summary ===")
            logger.info(f"Floats: {float_count}")
            logger.info(f"Profiles: {profile_count}")
            logger.info(f"Measurements: {measurement_count}")
            logger.info(f"BGC Data Points: {bgc_count}")
            logger.info("==============================")
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")


async def main():
    """Main function to fetch and load ARGO data."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch and load ARGO data')
    parser.add_argument('--days', type=int, default=30, help='Days back to fetch data (default: 30)')
    parser.add_argument('--max-files', type=int, default=50, help='Maximum files to download (default: 50)')
    parser.add_argument('--init-db', action='store_true', help='Initialize database tables')
    
    args = parser.parse_args()
    
    # Initialize database if requested
    if args.init_db:
        logger.info("Initializing database tables")
        Base.metadata.create_all(bind=engine)
    
    # Create data loader and run
    loader = ARGODataLoader()
    await loader.fetch_and_load_data(args.days, args.max_files)


if __name__ == "__main__":
    asyncio.run(main())
