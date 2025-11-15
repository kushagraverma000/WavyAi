"""Data export endpoints for CSV and NetCDF downloads."""
import io
import csv
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import xarray as xr
import numpy as np

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.profile import Profile
from app.models.measurement import Measurement
from app.models.bgc_data import BGCData
from app.models.float import ARGOFloat

router = APIRouter()
logger = get_logger(__name__)


@router.get("/profiles/csv")
async def export_profiles_csv(
    float_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lon: Optional[float] = None,
    max_lon: Optional[float] = None,
    limit: int = 1000,
    db: Session = Depends(get_db),
):
    """Export profile data as CSV."""
    try:
        # Build query
        query = db.query(Profile).join(ARGOFloat)
        
        # Apply filters
        if float_id:
            query = query.filter(ARGOFloat.float_id == float_id)
        if start_date:
            query = query.filter(Profile.profile_date >= start_date)
        if end_date:
            query = query.filter(Profile.profile_date <= end_date)
        if min_lat is not None:
            query = query.filter(Profile.latitude >= min_lat)
        if max_lat is not None:
            query = query.filter(Profile.latitude <= max_lat)
        if min_lon is not None:
            query = query.filter(Profile.longitude >= min_lon)
        if max_lon is not None:
            query = query.filter(Profile.longitude <= max_lon)
        
        profiles = query.limit(limit).all()
        
        if not profiles:
            raise HTTPException(status_code=404, detail="No profiles found matching criteria")
        
        # Create CSV data
        csv_data = []
        for profile in profiles:
            csv_data.append({
                'profile_id': str(profile.id),
                'float_id': profile.float_obj.float_id,
                'platform_number': profile.float_obj.platform_number,
                'profile_number': profile.profile_number,
                'date': profile.profile_date.isoformat(),
                'latitude': profile.latitude,
                'longitude': profile.longitude,
                'number_of_levels': profile.number_of_levels,
                'pressure_min': profile.pressure_min,
                'pressure_max': profile.pressure_max,
                'depth_min': profile.depth_min,
                'depth_max': profile.depth_max,
                'has_temperature': profile.has_temperature,
                'has_salinity': profile.has_salinity,
                'has_pressure': profile.has_pressure,
                'has_bgc_data': profile.has_bgc_data,
            })
        
        # Create CSV string
        output = io.StringIO()
        if csv_data:
            writer = csv.DictWriter(output, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
        
        # Create response
        csv_content = output.getvalue()
        filename = f"argo_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error("CSV export failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/measurements/csv")
async def export_measurements_csv(
    profile_id: str,
    db: Session = Depends(get_db),
):
    """Export measurement data for a specific profile as CSV."""
    try:
        # Get profile
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Get measurements
        measurements = db.query(Measurement).filter(
            Measurement.profile_id == profile_id
        ).order_by(Measurement.pressure).all()
        
        # Get BGC data
        bgc_data = db.query(BGCData).filter(
            BGCData.profile_id == profile_id
        ).order_by(BGCData.pressure).all()
        
        # Create combined dataset
        csv_data = []
        
        # Add measurements
        for measurement in measurements:
            row = {
                'profile_id': str(profile.id),
                'float_id': profile.float_obj.float_id,
                'date': profile.profile_date.isoformat(),
                'latitude': profile.latitude,
                'longitude': profile.longitude,
                'pressure': measurement.pressure,
                'depth': measurement.depth,
                'temperature': measurement.temperature,
                'temperature_qc': measurement.temperature_qc,
                'salinity': measurement.salinity,
                'salinity_qc': measurement.salinity_qc,
                'oxygen': None,
                'chlorophyll': None,
                'nitrate': None,
                'ph': None,
            }
            
            # Add BGC data if available at same pressure level
            for bgc in bgc_data:
                if abs(bgc.pressure - measurement.pressure) < 0.1:  # Match within 0.1 dbar
                    row.update({
                        'oxygen': bgc.oxygen,
                        'chlorophyll': bgc.chlorophyll,
                        'nitrate': bgc.nitrate,
                        'ph': bgc.ph,
                    })
                    break
            
            csv_data.append(row)
        
        if not csv_data:
            raise HTTPException(status_code=404, detail="No measurements found for profile")
        
        # Create CSV string
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=csv_data[0].keys())
        writer.writeheader()
        writer.writerows(csv_data)
        
        # Create response
        csv_content = output.getvalue()
        filename = f"argo_measurements_{profile.float_obj.float_id}_{profile.profile_number}.csv"
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error("Measurements CSV export failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/profiles/netcdf")
async def export_profiles_netcdf(
    float_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Export profile data as ARGO-compliant NetCDF."""
    try:
        # Build query
        query = db.query(Profile).join(ARGOFloat)
        
        # Apply filters
        if float_id:
            query = query.filter(ARGOFloat.float_id == float_id)
        if start_date:
            query = query.filter(Profile.profile_date >= start_date)
        if end_date:
            query = query.filter(Profile.profile_date <= end_date)
        
        profiles = query.limit(limit).all()
        
        if not profiles:
            raise HTTPException(status_code=404, detail="No profiles found matching criteria")
        
        # Create xarray dataset
        profile_data = []
        for profile in profiles:
            # Get measurements for this profile
            measurements = db.query(Measurement).filter(
                Measurement.profile_id == profile.id
            ).order_by(Measurement.pressure).all()
            
            if measurements:
                profile_data.append({
                    'profile_id': str(profile.id),
                    'float_id': profile.float_obj.float_id,
                    'platform_number': profile.float_obj.platform_number,
                    'cycle_number': profile.profile_number,
                    'juld': profile.profile_date,
                    'latitude': profile.latitude,
                    'longitude': profile.longitude,
                    'pressure': [m.pressure for m in measurements],
                    'temperature': [m.temperature for m in measurements],
                    'salinity': [m.salinity for m in measurements],
                    'depth': [m.depth for m in measurements],
                })
        
        if not profile_data:
            raise HTTPException(status_code=404, detail="No measurement data found")
        
        # Create NetCDF structure (simplified ARGO format)
        max_levels = max(len(p['pressure']) for p in profile_data)
        n_profiles = len(profile_data)
        
        # Initialize arrays
        pressure_data = np.full((n_profiles, max_levels), np.nan)
        temp_data = np.full((n_profiles, max_levels), np.nan)
        sal_data = np.full((n_profiles, max_levels), np.nan)
        depth_data = np.full((n_profiles, max_levels), np.nan)
        
        # Profile metadata
        juld = []
        latitude = []
        longitude = []
        platform_number = []
        cycle_number = []
        
        for i, profile in enumerate(profile_data):
            n_levels = len(profile['pressure'])
            pressure_data[i, :n_levels] = profile['pressure']
            temp_data[i, :n_levels] = profile['temperature']
            sal_data[i, :n_levels] = profile['salinity']
            depth_data[i, :n_levels] = profile['depth']
            
            juld.append(profile['juld'])
            latitude.append(profile['latitude'])
            longitude.append(profile['longitude'])
            platform_number.append(profile['platform_number'])
            cycle_number.append(profile['cycle_number'])
        
        # Create xarray dataset
        ds = xr.Dataset({
            'PRES': (['N_PROF', 'N_LEVELS'], pressure_data),
            'TEMP': (['N_PROF', 'N_LEVELS'], temp_data),
            'PSAL': (['N_PROF', 'N_LEVELS'], sal_data),
            'DEPTH': (['N_PROF', 'N_LEVELS'], depth_data),
            'JULD': (['N_PROF'], juld),
            'LATITUDE': (['N_PROF'], latitude),
            'LONGITUDE': (['N_PROF'], longitude),
            'PLATFORM_NUMBER': (['N_PROF'], platform_number),
            'CYCLE_NUMBER': (['N_PROF'], cycle_number),
        })
        
        # Add attributes
        ds.attrs.update({
            'title': 'ARGO Float Profiles',
            'institution': 'WavyAI',
            'source': 'ARGO Float Data',
            'history': f'Created on {datetime.now().isoformat()}',
            'Conventions': 'CF-1.6',
        })
        
        # Save to bytes
        output = io.BytesIO()
        ds.to_netcdf(output, format='NETCDF4')
        output.seek(0)
        
        filename = f"argo_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.nc"
        
        return StreamingResponse(
            output,
            media_type="application/netcdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error("NetCDF export failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
