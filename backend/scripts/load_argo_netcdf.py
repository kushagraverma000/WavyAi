"""Load ArgoNetCDF files from year/month/day directory structure."""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import logging
from typing import Optional, List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import netCDF4 as nc
import numpy as np
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.float import ARGOFloat
from app.models.profile import Profile
from app.models.measurement import Measurement
from app.models.bgc_data import BGCData

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArgoNetCDFLoader:
    """Load ARGO NetCDF files into the database."""
    
    def __init__(self, data_path: str):
        """Initialize the loader with the data path."""
        self.data_path = Path(data_path)
        self.db = SessionLocal()
        
        if not self.data_path.exists():
            raise ValueError(f"Data path does not exist: {data_path}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def find_netcdf_files(self, year: Optional[int] = None, 
                         month: Optional[int] = None, 
                         day: Optional[int] = None) -> List[Path]:
        """Find NetCDF files in the year/month/day structure."""
        files = []
        
        # Build search pattern
        if year:
            year_path = self.data_path / str(year)
            if not year_path.exists():
                logger.warning(f"Year directory not found: {year_path}")
                return files
            
            if month:
                month_path = year_path / f"{month:02d}"
                if not month_path.exists():
                    logger.warning(f"Month directory not found: {month_path}")
                    return files
                
                if day:
                    day_path = month_path / f"{day:02d}"
                    if day_path.exists():
                        files.extend(day_path.glob("*.nc"))
                else:
                    # All days in the month
                    for day_dir in month_path.iterdir():
                        if day_dir.is_dir():
                            files.extend(day_dir.glob("*.nc"))
            else:
                # All months in the year
                for month_dir in year_path.iterdir():
                    if month_dir.is_dir():
                        for day_dir in month_dir.iterdir():
                            if day_dir.is_dir():
                                files.extend(day_dir.glob("*.nc"))
        else:
            # All files
            files.extend(self.data_path.rglob("*.nc"))
        
        return sorted(files)
    
    def extract_float_metadata(self, nc_file: nc.Dataset) -> Dict[str, Any]:
        """Extract float metadata from NetCDF file."""
        metadata = {}
        
        # Common ARGO NetCDF attributes
        attr_mapping = {
            'platform_number': 'platform_number',
            'wmo_inst_type': 'wmo_number',
            'project_name': 'project_name',
            'pi_name': 'pi_name',
            'data_centre': 'data_center',
            'institution': 'institution',
            'source': 'source',
            'references': 'references',
            'comment': 'comment',
        }
        
        for nc_attr, db_field in attr_mapping.items():
            if hasattr(nc_file, nc_attr):
                value = getattr(nc_file, nc_attr)
                if isinstance(value, np.ndarray):
                    value = value.item() if value.size == 1 else str(value)
                elif isinstance(value, bytes):
                    value = value.decode('utf-8', errors='ignore').strip()
                metadata[db_field] = value
        
        return metadata
    
    def extract_profile_data(self, nc_file: nc.Dataset) -> List[Dict[str, Any]]:
        """Extract profile data from NetCDF file."""
        profiles = []
        
        try:
            # Get dimensions
            n_prof = nc_file.dimensions['N_PROF'].size if 'N_PROF' in nc_file.dimensions else 1
            n_levels = nc_file.dimensions['N_LEVELS'].size if 'N_LEVELS' in nc_file.dimensions else 0
            
            for prof_idx in range(n_prof):
                profile_data = {
                    'measurements': [],
                    'bgc_data': []
                }
                
                # Extract profile metadata
                if 'CYCLE_NUMBER' in nc_file.variables:
                    cycle_num = nc_file.variables['CYCLE_NUMBER'][prof_idx]
                    profile_data['profile_number'] = int(cycle_num) if not np.ma.is_masked(cycle_num) else prof_idx + 1
                else:
                    profile_data['profile_number'] = prof_idx + 1
                
                # Extract date/time
                if 'JULD' in nc_file.variables:
                    juld = nc_file.variables['JULD'][prof_idx]
                    if not np.ma.is_masked(juld):
                        # ARGO Julian day (days since 1950-01-01)
                        profile_data['profile_date'] = datetime(1950, 1, 1) + timedelta(days=float(juld))
                    else:
                        profile_data['profile_date'] = datetime.now()
                else:
                    profile_data['profile_date'] = datetime.now()
                
                # Extract position
                if 'LATITUDE' in nc_file.variables:
                    lat = nc_file.variables['LATITUDE'][prof_idx]
                    profile_data['latitude'] = float(lat) if not np.ma.is_masked(lat) else 0.0
                else:
                    profile_data['latitude'] = 0.0
                
                if 'LONGITUDE' in nc_file.variables:
                    lon = nc_file.variables['LONGITUDE'][prof_idx]
                    profile_data['longitude'] = float(lon) if not np.ma.is_masked(lon) else 0.0
                else:
                    profile_data['longitude'] = 0.0
                
                # Extract measurements
                for level in range(n_levels):
                    measurement = {'level': level}
                    
                    # Core measurements
                    var_mapping = {
                        'PRES': 'pressure',
                        'TEMP': 'temperature', 
                        'PSAL': 'salinity',
                        'PRES_QC': 'pressure_qc',
                        'TEMP_QC': 'temperature_qc',
                        'PSAL_QC': 'salinity_qc'
                    }
                    
                    for nc_var, db_field in var_mapping.items():
                        if nc_var in nc_file.variables:
                            if nc_file.variables[nc_var].ndim == 2:
                                value = nc_file.variables[nc_var][prof_idx, level]
                            else:
                                value = nc_file.variables[nc_var][level]
                            
                            if not np.ma.is_masked(value):
                                if 'QC' in nc_var:
                                    # Quality control flags are usually strings/bytes
                                    measurement[db_field] = int(value) if str(value).isdigit() else 1
                                else:
                                    measurement[db_field] = float(value)
                    
                    # Calculate depth from pressure if not available
                    if 'pressure' in measurement and 'depth' not in measurement:
                        # Approximate depth calculation: depth ≈ pressure * 1.019716
                        measurement['depth'] = measurement['pressure'] * 1.019716
                    
                    # Only add measurement if we have at least pressure
                    if 'pressure' in measurement:
                        profile_data['measurements'].append(measurement)
                
                # Extract BGC data if available
                bgc_vars = {
                    'DOXY': 'oxygen',
                    'CHLA': 'chlorophyll', 
                    'NITRATE': 'nitrate',
                    'PH_IN_SITU_TOTAL': 'ph',
                    'DOXY_QC': 'oxygen_qc',
                    'CHLA_QC': 'chlorophyll_qc',
                    'NITRATE_QC': 'nitrate_qc',
                    'PH_IN_SITU_TOTAL_QC': 'ph_qc'
                }
                
                has_bgc = any(var in nc_file.variables for var in bgc_vars.keys())
                profile_data['has_bgc_data'] = has_bgc
                
                if has_bgc:
                    for level in range(n_levels):
                        bgc_measurement = {'level': level}
                        
                        for nc_var, db_field in bgc_vars.items():
                            if nc_var in nc_file.variables:
                                if nc_file.variables[nc_var].ndim == 2:
                                    value = nc_file.variables[nc_var][prof_idx, level]
                                else:
                                    value = nc_file.variables[nc_var][level]
                                
                                if not np.ma.is_masked(value):
                                    if 'QC' in nc_var:
                                        bgc_measurement[db_field] = int(value) if str(value).isdigit() else 1
                                    else:
                                        bgc_measurement[db_field] = float(value)
                        
                        # Add corresponding pressure and depth
                        if level < len(profile_data['measurements']):
                            meas = profile_data['measurements'][level]
                            if 'pressure' in meas:
                                bgc_measurement['pressure'] = meas['pressure']
                            if 'depth' in meas:
                                bgc_measurement['depth'] = meas['depth']
                        
                        # Only add BGC data if we have at least one BGC variable
                        if any(field in bgc_measurement for field in ['oxygen', 'chlorophyll', 'nitrate', 'ph']):
                            profile_data['bgc_data'].append(bgc_measurement)
                
                # Set profile summary info
                profile_data['number_of_levels'] = len(profile_data['measurements'])
                if profile_data['measurements']:
                    pressures = [m.get('pressure', 0) for m in profile_data['measurements'] if 'pressure' in m]
                    if pressures:
                        profile_data['pressure_min'] = min(pressures)
                        profile_data['pressure_max'] = max(pressures)
                    
                    depths = [m.get('depth', 0) for m in profile_data['measurements'] if 'depth' in m]
                    if depths:
                        profile_data['depth_min'] = min(depths)
                        profile_data['depth_max'] = max(depths)
                
                profiles.append(profile_data)
        
        except Exception as e:
            logger.error(f"Error extracting profile data: {e}")
            return []
        
        return profiles
    
    def load_netcdf_file(self, file_path: Path) -> bool:
        """Load a single NetCDF file into the database."""
        try:
            logger.info(f"Loading file: {file_path}")
            
            with nc.Dataset(file_path, 'r') as nc_file:
                # Extract float metadata
                float_metadata = self.extract_float_metadata(nc_file)
                
                # Get or create float
                platform_number = float_metadata.get('platform_number', file_path.stem)
                float_obj = self.db.query(ARGOFloat).filter(
                    ARGOFloat.platform_number == platform_number
                ).first()
                
                if not float_obj:
                    float_obj = ARGOFloat(
                        id=uuid.uuid4(),
                        float_id=platform_number,
                        platform_number=platform_number,
                        wmo_number=float_metadata.get('wmo_number'),
                        name=f"ARGO Float {platform_number}",
                        project_name=float_metadata.get('project_name', 'ARGO'),
                        pi_name=float_metadata.get('pi_name'),
                        data_center=float_metadata.get('data_center'),
                        current_status='active',
                        metadata=float_metadata
                    )
                    self.db.add(float_obj)
                    self.db.flush()
                
                # Extract and load profiles
                profiles_data = self.extract_profile_data(nc_file)
                
                for profile_data in profiles_data:
                    # Check if profile already exists
                    existing_profile = self.db.query(Profile).filter(
                        Profile.float_id == float_obj.id,
                        Profile.profile_number == profile_data['profile_number']
                    ).first()
                    
                    if existing_profile:
                        logger.debug(f"Profile {profile_data['profile_number']} already exists, skipping")
                        continue
                    
                    # Create profile
                    profile = Profile(
                        id=uuid.uuid4(),
                        float_id=float_obj.id,
                        profile_number=profile_data['profile_number'],
                        profile_date=profile_data['profile_date'],
                        latitude=profile_data['latitude'],
                        longitude=profile_data['longitude'],
                        number_of_levels=profile_data.get('number_of_levels', 0),
                        pressure_min=profile_data.get('pressure_min', 0.0),
                        pressure_max=profile_data.get('pressure_max', 0.0),
                        depth_min=profile_data.get('depth_min', 0.0),
                        depth_max=profile_data.get('depth_max', 0.0),
                        has_temperature=any('temperature' in m for m in profile_data['measurements']),
                        has_salinity=any('salinity' in m for m in profile_data['measurements']),
                        has_pressure=any('pressure' in m for m in profile_data['measurements']),
                        has_bgc_data=profile_data.get('has_bgc_data', False),
                        summary=f"Profile {profile_data['profile_number']} from {file_path.name}"
                    )
                    self.db.add(profile)
                    self.db.flush()
                    
                    # Add measurements
                    for meas_data in profile_data['measurements']:
                        measurement = Measurement(
                            id=uuid.uuid4(),
                            profile_id=profile.id,
                            level=meas_data['level'],
                            pressure=meas_data.get('pressure'),
                            depth=meas_data.get('depth'),
                            temperature=meas_data.get('temperature'),
                            salinity=meas_data.get('salinity'),
                            pressure_measured=meas_data.get('pressure'),
                            temperature_qc=meas_data.get('temperature_qc', 1),
                            salinity_qc=meas_data.get('salinity_qc', 1),
                            pressure_qc=meas_data.get('pressure_qc', 1)
                        )
                        self.db.add(measurement)
                    
                    # Add BGC data
                    for bgc_data_item in profile_data['bgc_data']:
                        bgc_data = BGCData(
                            id=uuid.uuid4(),
                            profile_id=profile.id,
                            level=bgc_data_item['level'],
                            pressure=bgc_data_item.get('pressure'),
                            depth=bgc_data_item.get('depth'),
                            oxygen=bgc_data_item.get('oxygen'),
                            chlorophyll=bgc_data_item.get('chlorophyll'),
                            nitrate=bgc_data_item.get('nitrate'),
                            ph=bgc_data_item.get('ph'),
                            oxygen_qc=bgc_data_item.get('oxygen_qc', 1),
                            chlorophyll_qc=bgc_data_item.get('chlorophyll_qc', 1),
                            nitrate_qc=bgc_data_item.get('nitrate_qc', 1),
                            ph_qc=bgc_data_item.get('ph_qc', 1)
                        )
                        self.db.add(bgc_data)
                
                self.db.commit()
                logger.info(f"Successfully loaded {len(profiles_data)} profiles from {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            self.db.rollback()
            return False
    
    def load_data(self, year: Optional[int] = None, 
                  month: Optional[int] = None, 
                  day: Optional[int] = None,
                  max_files: Optional[int] = None) -> Dict[str, int]:
        """Load ARGO data from NetCDF files."""
        files = self.find_netcdf_files(year, month, day)
        
        if max_files:
            files = files[:max_files]
        
        logger.info(f"Found {len(files)} NetCDF files to process")
        
        stats = {
            'total_files': len(files),
            'successful': 0,
            'failed': 0
        }
        
        for file_path in files:
            try:
                if self.load_netcdf_file(file_path):
                    stats['successful'] += 1
                else:
                    stats['failed'] += 1
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                stats['failed'] += 1
        
        return stats


def main():
    """Main function to load ARGO NetCDF data."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load ARGO NetCDF data')
    parser.add_argument('data_path', help='Path to ARGO data directory')
    parser.add_argument('--year', type=int, help='Specific year to load')
    parser.add_argument('--month', type=int, help='Specific month to load')
    parser.add_argument('--day', type=int, help='Specific day to load')
    parser.add_argument('--max-files', type=int, help='Maximum number of files to process')
    
    args = parser.parse_args()
    
    try:
        with ArgoNetCDFLoader(args.data_path) as loader:
            stats = loader.load_data(
                year=args.year,
                month=args.month, 
                day=args.day,
                max_files=args.max_files
            )
            
            print(f"\nLoading completed:")
            print(f"Total files: {stats['total_files']}")
            print(f"Successful: {stats['successful']}")
            print(f"Failed: {stats['failed']}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
