"""Visualization endpoints for maps, charts, and data export."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import json
import csv
import io
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.float import ARGOFloat
from app.models.profile import Profile
from app.models.measurement import Measurement
from app.models.bgc_data import BGCData

router = APIRouter()
logger = get_logger(__name__)


@router.get("/map/floats")
async def get_float_locations(
    db: Session = Depends(get_db),
    bbox: Optional[str] = Query(None, description="Bounding box: min_lon,min_lat,max_lon,max_lat"),
    status: Optional[str] = Query(None, description="Float status filter"),
    limit: int = Query(100, description="Maximum number of floats to return")
):
    """Get ARGO float locations for map visualization."""
    try:
        query = db.query(ARGOFloat)
        
        # Apply status filter
        if status:
            query = query.filter(ARGOFloat.current_status == status)
        
        # Apply bounding box filter
        if bbox:
            try:
                min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(','))
                query = query.filter(
                    and_(
                        ARGOFloat.last_longitude >= min_lon,
                        ARGOFloat.last_longitude <= max_lon,
                        ARGOFloat.last_latitude >= min_lat,
                        ARGOFloat.last_latitude <= max_lat
                    )
                )
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid bounding box format")
        
        floats = query.limit(limit).all()
        
        # Format for map display
        features = []
        for float_obj in floats:
            if float_obj.last_latitude and float_obj.last_longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float_obj.last_longitude, float_obj.last_latitude]
                    },
                    "properties": {
                        "float_id": float_obj.float_id,
                        "platform_number": float_obj.platform_number,
                        "status": float_obj.current_status,
                        "last_profile_date": float_obj.last_profile_date.isoformat() if float_obj.last_profile_date else None,
                        "project_name": float_obj.project_name,
                        "deployment_date": float_obj.deployment_date.isoformat() if float_obj.deployment_date else None,
                    }
                })
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "total_floats": len(features),
                "bbox": bbox,
                "status_filter": status
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting float locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map/profiles")
async def get_profile_locations(
    db: Session = Depends(get_db),
    bbox: Optional[str] = Query(None, description="Bounding box: min_lon,min_lat,max_lon,max_lat"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    has_bgc: Optional[bool] = Query(None, description="Filter profiles with BGC data"),
    limit: int = Query(200, description="Maximum number of profiles to return")
):
    """Get ARGO profile locations for map visualization."""
    try:
        query = db.query(Profile)
        
        # Apply date filters
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Profile.profile_date >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Profile.profile_date <= end_dt)
        
        # Apply BGC filter
        if has_bgc is not None:
            query = query.filter(Profile.has_bgc_data == has_bgc)
        
        # Apply bounding box filter
        if bbox:
            try:
                min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(','))
                query = query.filter(
                    and_(
                        Profile.longitude >= min_lon,
                        Profile.longitude <= max_lon,
                        Profile.latitude >= min_lat,
                        Profile.latitude <= max_lat
                    )
                )
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid bounding box format")
        
        profiles = query.order_by(Profile.profile_date.desc()).limit(limit).all()
        
        # Format for map display
        features = []
        for profile in profiles:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [profile.longitude, profile.latitude]
                },
                "properties": {
                    "profile_id": str(profile.id),
                    "float_id": str(profile.float_id),
                    "profile_number": profile.profile_number,
                    "profile_date": profile.profile_date.isoformat(),
                    "has_temperature": profile.has_temperature,
                    "has_salinity": profile.has_salinity,
                    "has_bgc_data": profile.has_bgc_data,
                    "depth_range": f"{profile.depth_min:.1f}-{profile.depth_max:.1f}m" if profile.depth_min and profile.depth_max else None,
                    "number_of_levels": profile.number_of_levels,
                }
            })
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "total_profiles": len(features),
                "bbox": bbox,
                "date_range": f"{start_date} to {end_date}" if start_date or end_date else None,
                "has_bgc_filter": has_bgc
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting profile locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/temperature-depth/{profile_id}")
async def get_temperature_depth_chart(
    profile_id: str,
    db: Session = Depends(get_db)
):
    """Get temperature-depth profile data for charting."""
    try:
        # Get profile
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Get measurements
        measurements = db.query(Measurement).filter(
            Measurement.profile_id == profile_id
        ).order_by(Measurement.pressure).all()
        
        if not measurements:
            raise HTTPException(status_code=404, detail="No measurements found for profile")
        
        # Format data for charting
        data = []
        for measurement in measurements:
            if measurement.temperature is not None and measurement.depth is not None:
                data.append({
                    "depth": measurement.depth,
                    "temperature": measurement.temperature,
                    "pressure": measurement.pressure,
                    "salinity": measurement.salinity,
                })
        
        return {
            "profile_info": {
                "profile_id": str(profile.id),
                "float_id": str(profile.float_id),
                "profile_number": profile.profile_number,
                "date": profile.profile_date.isoformat(),
                "location": [profile.longitude, profile.latitude],
            },
            "data": data,
            "chart_config": {
                "type": "line",
                "x_axis": "temperature",
                "y_axis": "depth",
                "title": f"Temperature Profile - Float {profile.float_id}",
                "x_label": "Temperature (°C)",
                "y_label": "Depth (m)",
                "invert_y": True  # Depth increases downward
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting temperature-depth chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/salinity-depth/{profile_id}")
async def get_salinity_depth_chart(
    profile_id: str,
    db: Session = Depends(get_db)
):
    """Get salinity-depth profile data for charting."""
    try:
        # Get profile
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Get measurements
        measurements = db.query(Measurement).filter(
            Measurement.profile_id == profile_id
        ).order_by(Measurement.pressure).all()
        
        if not measurements:
            raise HTTPException(status_code=404, detail="No measurements found for profile")
        
        # Format data for charting
        data = []
        for measurement in measurements:
            if measurement.salinity is not None and measurement.depth is not None:
                data.append({
                    "depth": measurement.depth,
                    "salinity": measurement.salinity,
                    "pressure": measurement.pressure,
                    "temperature": measurement.temperature,
                })
        
        return {
            "profile_info": {
                "profile_id": str(profile.id),
                "float_id": str(profile.float_id),
                "profile_number": profile.profile_number,
                "date": profile.profile_date.isoformat(),
                "location": [profile.longitude, profile.latitude],
            },
            "data": data,
            "chart_config": {
                "type": "line",
                "x_axis": "salinity",
                "y_axis": "depth",
                "title": f"Salinity Profile - Float {profile.float_id}",
                "x_label": "Salinity (PSU)",
                "y_label": "Depth (m)",
                "invert_y": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting salinity-depth chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/ts-diagram/{profile_id}")
async def get_ts_diagram(
    profile_id: str,
    db: Session = Depends(get_db)
):
    """Get Temperature-Salinity diagram data."""
    try:
        # Get profile
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Get measurements
        measurements = db.query(Measurement).filter(
            Measurement.profile_id == profile_id
        ).order_by(Measurement.pressure).all()
        
        if not measurements:
            raise HTTPException(status_code=404, detail="No measurements found for profile")
        
        # Format data for T-S diagram
        data = []
        for measurement in measurements:
            if measurement.temperature is not None and measurement.salinity is not None:
                data.append({
                    "temperature": measurement.temperature,
                    "salinity": measurement.salinity,
                    "depth": measurement.depth,
                    "pressure": measurement.pressure,
                })
        
        return {
            "profile_info": {
                "profile_id": str(profile.id),
                "float_id": str(profile.float_id),
                "profile_number": profile.profile_number,
                "date": profile.profile_date.isoformat(),
                "location": [profile.longitude, profile.latitude],
            },
            "data": data,
            "chart_config": {
                "type": "scatter",
                "x_axis": "salinity",
                "y_axis": "temperature",
                "title": f"T-S Diagram - Float {profile.float_id}",
                "x_label": "Salinity (PSU)",
                "y_label": "Temperature (°C)",
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting T-S diagram: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/csv/{profile_id}")
async def export_profile_csv(
    profile_id: str,
    db: Session = Depends(get_db)
):
    """Export profile data as CSV."""
    try:
        # Get profile
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Get measurements
        measurements = db.query(Measurement).filter(
            Measurement.profile_id == profile_id
        ).order_by(Measurement.pressure).all()
        
        # Get BGC data if available
        bgc_data = {}
        if profile.has_bgc_data:
            bgc_records = db.query(BGCData).filter(
                BGCData.profile_id == profile_id
            ).order_by(BGCData.pressure).all()
            
            for bgc in bgc_records:
                bgc_data[bgc.level] = {
                    'oxygen': bgc.oxygen,
                    'chlorophyll': bgc.chlorophyll,
                    'nitrate': bgc.nitrate,
                    'ph': bgc.ph
                }
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        header = ['level', 'pressure', 'depth', 'temperature', 'salinity']
        if profile.has_bgc_data:
            header.extend(['oxygen', 'chlorophyll', 'nitrate', 'ph'])
        writer.writerow(header)
        
        # Write data
        for measurement in measurements:
            row = [
                measurement.level,
                measurement.pressure,
                measurement.depth,
                measurement.temperature,
                measurement.salinity
            ]
            
            if profile.has_bgc_data and measurement.level in bgc_data:
                bgc = bgc_data[measurement.level]
                row.extend([
                    bgc.get('oxygen'),
                    bgc.get('chlorophyll'),
                    bgc.get('nitrate'),
                    bgc.get('ph')
                ])
            elif profile.has_bgc_data:
                row.extend([None, None, None, None])
            
            writer.writerow(row)
        
        # Create response
        output.seek(0)
        filename = f"argo_profile_{profile.float_id}_{profile.profile_number}.csv"
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/profiles")
async def search_profiles(
    db: Session = Depends(get_db),
    query: Optional[str] = Query(None, description="Search query"),
    bbox: Optional[str] = Query(None, description="Bounding box: min_lon,min_lat,max_lon,max_lat"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    has_temperature: Optional[bool] = Query(None, description="Filter profiles with temperature data"),
    has_salinity: Optional[bool] = Query(None, description="Filter profiles with salinity data"),
    has_bgc: Optional[bool] = Query(None, description="Filter profiles with BGC data"),
    min_depth: Optional[float] = Query(None, description="Minimum depth"),
    max_depth: Optional[float] = Query(None, description="Maximum depth"),
    limit: int = Query(50, description="Maximum number of results")
):
    """Search ARGO profiles with various filters."""
    try:
        query_obj = db.query(Profile)
        
        # Apply filters
        if bbox:
            try:
                min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(','))
                query_obj = query_obj.filter(
                    and_(
                        Profile.longitude >= min_lon,
                        Profile.longitude <= max_lon,
                        Profile.latitude >= min_lat,
                        Profile.latitude <= max_lat
                    )
                )
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid bounding box format")
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query_obj = query_obj.filter(Profile.profile_date >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query_obj = query_obj.filter(Profile.profile_date <= end_dt)
        
        if has_temperature is not None:
            query_obj = query_obj.filter(Profile.has_temperature == has_temperature)
        
        if has_salinity is not None:
            query_obj = query_obj.filter(Profile.has_salinity == has_salinity)
        
        if has_bgc is not None:
            query_obj = query_obj.filter(Profile.has_bgc_data == has_bgc)
        
        if min_depth is not None:
            query_obj = query_obj.filter(Profile.depth_max >= min_depth)
        
        if max_depth is not None:
            query_obj = query_obj.filter(Profile.depth_min <= max_depth)
        
        # Text search in summary if query provided
        if query:
            query_obj = query_obj.filter(Profile.summary.ilike(f"%{query}%"))
        
        profiles = query_obj.order_by(Profile.profile_date.desc()).limit(limit).all()
        
        # Format results
        results = []
        for profile in profiles:
            results.append({
                "profile_id": str(profile.id),
                "float_id": str(profile.float_id),
                "profile_number": profile.profile_number,
                "date": profile.profile_date.isoformat(),
                "location": [profile.longitude, profile.latitude],
                "depth_range": f"{profile.depth_min:.1f}-{profile.depth_max:.1f}m" if profile.depth_min and profile.depth_max else None,
                "has_temperature": profile.has_temperature,
                "has_salinity": profile.has_salinity,
                "has_bgc_data": profile.has_bgc_data,
                "number_of_levels": profile.number_of_levels,
                "summary": profile.summary,
            })
        
        return {
            "profiles": results,
            "total": len(results),
            "filters": {
                "bbox": bbox,
                "date_range": f"{start_date} to {end_date}" if start_date or end_date else None,
                "depth_range": f"{min_depth}-{max_depth}m" if min_depth or max_depth else None,
                "has_temperature": has_temperature,
                "has_salinity": has_salinity,
                "has_bgc_data": has_bgc,
                "query": query
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))
