"""Data ingestion service for NetCDF files."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import xarray as xr
import numpy as np
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.database import SessionLocal
from app.models.float import ARGOFloat
from app.models.profile import Profile
from app.models.measurement import Measurement
from app.models.bgc_data import BGCData
from app.services.embedding_service import get_embedding_service
from app.core.vector_db import get_vector_db

logger = get_logger(__name__)


class DataIngestionService:
    """Service for ingesting NetCDF files."""

    def __init__(self, db: Session):
        """Initialize data ingestion service."""
        self.db = db
        self.embedding_service = get_embedding_service()
        self.vector_db = get_vector_db()

    def ingest_netcdf_file(self, file_path: str) -> Dict[str, Any]:
        """Ingest a NetCDF file into the database."""
        try:
            logger.info("Starting NetCDF ingestion", file_path=file_path)
            
            # Open NetCDF file
            ds = xr.open_dataset(file_path)
            
            # Extract float information
            float_data = self._extract_float_data(ds)
            float_obj = self._create_or_update_float(float_data)
            
            # Extract profile data
            profiles_created = 0
            measurements_created = 0
            bgc_data_created = 0
            
            if "N_PROF" in ds.dims:
                num_profiles = ds.dims["N_PROF"]
                
                for profile_idx in range(num_profiles):
                    profile_data = self._extract_profile_data(ds, profile_idx, float_obj.id)
                    profile = self._create_profile(profile_data, float_obj.id)
                    
                    if profile:
                        profiles_created += 1
                        
                        # Extract measurements
                        measurements = self._extract_measurements(ds, profile_idx, profile.id)
                        for measurement in measurements:
                            self.db.add(measurement)
                            measurements_created += 1
                        
                        # Extract BGC data
                        bgc_data_list = self._extract_bgc_data(ds, profile_idx, profile.id)
                        for bgc_data in bgc_data_list:
                            self.db.add(bgc_data)
                            bgc_data_created += 1
                        
                        # Generate embedding and add to vector DB
                        if profile.summary and self.embedding_service and self.vector_db:
                            embedding = self.embedding_service.generate_embedding(profile.summary)
                            if embedding:
                                self.vector_db.add_vectors([{
                                    "id": str(profile.id),
                                    "vector": embedding,
                                    "payload": {
                                        "profile_id": str(profile.id),
                                        "float_id": str(float_obj.float_id),
                                        "date": profile.profile_date.isoformat(),
                                        "latitude": profile.latitude,
                                        "longitude": profile.longitude,
                                        "summary": profile.summary,
                                    },
                                }])
                
                self.db.commit()
                logger.info(
                    "NetCDF ingestion completed",
                    file_path=file_path,
                    profiles=profiles_created,
                    measurements=measurements_created,
                    bgc_data=bgc_data_created,
                )
                
                return {
                    "status": "success",
                    "file_path": file_path,
                    "profiles_created": profiles_created,
                    "measurements_created": measurements_created,
                    "bgc_data_created": bgc_data_created,
                }
            else:
                logger.warning("No profiles found in NetCDF file", file_path=file_path)
                return {
                    "status": "success",
                    "file_path": file_path,
                    "profiles_created": 0,
                    "measurements_created": 0,
                    "bgc_data_created": 0,
                }
                
        except Exception as e:
            logger.error("NetCDF ingestion failed", error=str(e), file_path=file_path, exc_info=True)
            self.db.rollback()
            return {
                "status": "error",
                "file_path": file_path,
                "error": str(e),
            }

    def _extract_float_data(self, ds: xr.Dataset) -> Dict[str, Any]:
        """Extract float data from NetCDF dataset."""
        float_data = {
            "float_id": str(ds.attrs.get("PLATFORM_NUMBER", "unknown")),
            "platform_number": str(ds.attrs.get("PLATFORM_NUMBER", "unknown")),
            "wmo_number": str(ds.attrs.get("WMO_INST_TYPE", "")),
            "project_name": str(ds.attrs.get("PROJECT_NAME", "")),
            "pi_name": str(ds.attrs.get("PI_NAME", "")),
            "data_center": str(ds.attrs.get("DATA_CENTRE", "")),
            "sensor_type": str(ds.attrs.get("SENSOR", "")),
        }
        return float_data

    def _create_or_update_float(self, float_data: Dict[str, Any]) -> ARGOFloat:
        """Create or update float in database."""
        float_obj = self.db.query(ARGOFloat).filter(
            ARGOFloat.float_id == float_data["float_id"]
        ).first()
        
        if not float_obj:
            float_obj = ARGOFloat(
                id=uuid.uuid4(),
                **float_data,
                current_status="active",
            )
            self.db.add(float_obj)
            self.db.flush()
        else:
            # Update existing float
            for key, value in float_data.items():
                setattr(float_obj, key, value)
            self.db.flush()
        
        return float_obj

    def _extract_profile_data(
        self,
        ds: xr.Dataset,
        profile_idx: int,
        float_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Extract profile data from NetCDF dataset."""
        try:
            lat_val = ds["LATITUDE"].isel(N_PROF=profile_idx).values
            lon_val = ds["LONGITUDE"].isel(N_PROF=profile_idx).values
            
            # Handle NaN values
            if hasattr(lat_val, 'item'):
                latitude = float(lat_val.item()) if not np.isnan(lat_val.item()) else 0.0
            else:
                latitude = float(lat_val) if not np.isnan(lat_val) else 0.0
                
            if hasattr(lon_val, 'item'):
                longitude = float(lon_val.item()) if not np.isnan(lon_val.item()) else 0.0
            else:
                longitude = float(lon_val) if not np.isnan(lon_val) else 0.0
        except Exception as e:
            logger.warning("Failed to extract lat/lon", error=str(e))
            latitude = 0.0
            longitude = 0.0
        
        # Extract date from JULD if available
        profile_date = datetime.utcnow()  # Default to current time
        try:
            if "JULD" in ds.data_vars:
                juld = ds["JULD"].isel(N_PROF=profile_idx).values
                if hasattr(juld, 'item'):
                    juld_val = juld.item()
                else:
                    juld_val = float(juld)
                
                if not np.isnan(juld_val):
                    # Convert Julian day to datetime (simplified - assumes reference date)
                    # In real implementation, use JULD_REFERENCE_DATE from attributes
                    from datetime import timedelta
                    reference_date = datetime(1950, 1, 1)  # Common ARGO reference
                    profile_date = reference_date + timedelta(days=float(juld_val))
        except Exception as e:
            logger.warning("Failed to extract date from JULD", error=str(e))
            # Keep default datetime.utcnow()
        
        # Generate summary
        has_temperature = "TEMP" in ds.data_vars
        has_salinity = "PSAL" in ds.data_vars
        has_pressure = "PRES" in ds.data_vars
        has_bgc_data = any(var in ds.data_vars for var in ["DOXY", "CHLA", "NITRATE"])
        
        summary_parts = []
        if has_temperature:
            summary_parts.append("temperature")
        if has_salinity:
            summary_parts.append("salinity")
        if has_bgc_data:
            summary_parts.append("biogeochemical data")
        summary = f"Profile with {', '.join(summary_parts)}" if summary_parts else "ARGO profile"
        
        profile_data = {
            "float_id": float_id,
            "profile_number": profile_idx + 1,
            "latitude": latitude,
            "longitude": longitude,
            "profile_date": profile_date,
            "has_temperature": has_temperature,
            "has_salinity": has_salinity,
            "has_pressure": has_pressure,
            "has_bgc_data": has_bgc_data,
            "summary": summary,
        }
        
        return profile_data

    def _create_profile(
        self,
        profile_data: Dict[str, Any],
        float_id: uuid.UUID,
    ) -> Optional[Profile]:
        """Create profile in database."""
        try:
            profile = Profile(
                id=uuid.uuid4(),
                float_id=float_id,
                **profile_data,
            )
            self.db.add(profile)
            self.db.flush()
            return profile
        except Exception as e:
            logger.error("Failed to create profile", error=str(e))
            return None

    def _extract_measurements(
        self,
        ds: xr.Dataset,
        profile_idx: int,
        profile_id: uuid.UUID,
    ) -> List[Measurement]:
        """Extract measurements from NetCDF dataset."""
        measurements = []
        
        if "PRES" not in ds.data_vars:
            return measurements
        
        try:
            pressure = ds["PRES"].isel(N_PROF=profile_idx).values
            temperature = ds["TEMP"].isel(N_PROF=profile_idx).values if "TEMP" in ds.data_vars else None
            salinity = ds["PSAL"].isel(N_PROF=profile_idx).values if "PSAL" in ds.data_vars else None
            
            num_levels = len(pressure)
            
            for level in range(num_levels):
                try:
                    pressure_val = pressure[level]
                    if np.isnan(pressure_val) or pressure_val < 0:
                        continue
                    
                    # Handle scalar vs array values
                    if hasattr(pressure_val, 'item'):
                        pressure_val = pressure_val.item()
                    
                    temp_val = None
                    if temperature is not None and level < len(temperature):
                        temp_val = temperature[level]
                        if hasattr(temp_val, 'item'):
                            temp_val = temp_val.item()
                        if np.isnan(temp_val):
                            temp_val = None
                    
                    sal_val = None
                    if salinity is not None and level < len(salinity):
                        sal_val = salinity[level]
                        if hasattr(sal_val, 'item'):
                            sal_val = sal_val.item()
                        if np.isnan(sal_val):
                            sal_val = None
                    
                    measurement = Measurement(
                        id=uuid.uuid4(),
                        profile_id=profile_id,
                        level=level,
                        pressure=float(pressure_val),
                        depth=float(pressure_val) * 10,  # Approximate depth
                        temperature=float(temp_val) if temp_val is not None else None,
                        salinity=float(sal_val) if sal_val is not None else None,
                        pressure_measured=float(pressure_val),
                        temperature_qc=1,
                        salinity_qc=1,
                        pressure_qc=1,
                    )
                    measurements.append(measurement)
                except Exception as e:
                    logger.warning(f"Failed to extract measurement at level {level}", error=str(e))
                    continue
        except Exception as e:
            logger.error("Failed to extract measurements", error=str(e))
        
        return measurements

    def _extract_bgc_data(
        self,
        ds: xr.Dataset,
        profile_idx: int,
        profile_id: uuid.UUID,
    ) -> List[BGCData]:
        """Extract BGC data from NetCDF dataset."""
        bgc_data_list = []
        
        if "PRES" not in ds.data_vars:
            return bgc_data_list
        
        try:
            pressure = ds["PRES"].isel(N_PROF=profile_idx).values
            oxygen = ds["DOXY"].isel(N_PROF=profile_idx).values if "DOXY" in ds.data_vars else None
            chlorophyll = ds["CHLA"].isel(N_PROF=profile_idx).values if "CHLA" in ds.data_vars else None
            nitrate = ds["NITRATE"].isel(N_PROF=profile_idx).values if "NITRATE" in ds.data_vars else None
            
            num_levels = len(pressure)
            
            for level in range(num_levels):
                try:
                    pressure_val = pressure[level]
                    if np.isnan(pressure_val) or pressure_val < 0:
                        continue
                    
                    # Handle scalar vs array values
                    if hasattr(pressure_val, 'item'):
                        pressure_val = pressure_val.item()
                    
                    # Only create BGC data if at least one parameter exists
                    oxy_val = None
                    if oxygen is not None and level < len(oxygen):
                        oxy_val = oxygen[level]
                        if hasattr(oxy_val, 'item'):
                            oxy_val = oxy_val.item()
                        if np.isnan(oxy_val):
                            oxy_val = None
                    
                    chl_val = None
                    if chlorophyll is not None and level < len(chlorophyll):
                        chl_val = chlorophyll[level]
                        if hasattr(chl_val, 'item'):
                            chl_val = chl_val.item()
                        if np.isnan(chl_val):
                            chl_val = None
                    
                    nit_val = None
                    if nitrate is not None and level < len(nitrate):
                        nit_val = nitrate[level]
                        if hasattr(nit_val, 'item'):
                            nit_val = nit_val.item()
                        if np.isnan(nit_val):
                            nit_val = None
                    
                    if oxy_val is None and chl_val is None and nit_val is None:
                        continue
                    
                    bgc_data = BGCData(
                        id=uuid.uuid4(),
                        profile_id=profile_id,
                        level=level,
                        pressure=float(pressure_val),
                        depth=float(pressure_val) * 10,  # Approximate depth
                        oxygen=float(oxy_val) if oxy_val is not None else None,
                        chlorophyll=float(chl_val) if chl_val is not None else None,
                        nitrate=float(nit_val) if nit_val is not None else None,
                        oxygen_qc=1,
                        chlorophyll_qc=1,
                        nitrate_qc=1,
                    )
                    bgc_data_list.append(bgc_data)
                except Exception as e:
                    logger.warning(f"Failed to extract BGC data at level {level}", error=str(e))
                    continue
        except Exception as e:
            logger.error("Failed to extract BGC data", error=str(e))
        
        return bgc_data_list

