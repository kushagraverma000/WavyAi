"""Simple visualization endpoints for prototype."""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, List
import json
import random

from app.core.logging import get_logger
from app.services.simple_query_service import simple_query_service

router = APIRouter()
logger = get_logger(__name__)


@router.get("/floats")
async def get_float_locations():
    """Get ARGO float locations for map visualization."""
    try:
        floats = simple_query_service.get_sample_floats()
        
        # Format for map visualization
        features = []
        for float_data in floats:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float_data["last_longitude"], float_data["last_latitude"]]
                },
                "properties": {
                    "id": float_data["float_id"],
                    "name": float_data["name"],
                    "status": float_data["current_status"],
                    "last_update": float_data["last_profile_date"],
                    "total_profiles": float_data["total_profiles"]
                }
            })
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
        
    except Exception as e:
        logger.error("Failed to get float locations", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get float locations: {str(e)}")


@router.get("/profiles/{profile_id}/temperature-depth")
async def get_temperature_depth_data(profile_id: str):
    """Get temperature vs depth data for a profile."""
    try:
        profile = simple_query_service.get_profile_data(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Extract temperature-depth data
        data = []
        for measurement in profile.get("measurements", []):
            data.append({
                "depth": measurement["depth"],
                "temperature": measurement["temperature"],
                "quality_flag": measurement["quality_flag"]
            })
        
        return {
            "profile_id": profile_id,
            "float_id": profile["float_id"],
            "date": profile["profile_date"],
            "location": {
                "latitude": profile["latitude"],
                "longitude": profile["longitude"]
            },
            "data": data,
            "metadata": {
                "parameter": "temperature",
                "units": "°C",
                "depth_units": "meters"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get temperature-depth data", error=str(e), profile_id=profile_id)
        raise HTTPException(status_code=500, detail=f"Failed to get temperature-depth data: {str(e)}")


@router.get("/profiles/{profile_id}/salinity-depth")
async def get_salinity_depth_data(profile_id: str):
    """Get salinity vs depth data for a profile."""
    try:
        profile = simple_query_service.get_profile_data(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Extract salinity-depth data
        data = []
        for measurement in profile.get("measurements", []):
            data.append({
                "depth": measurement["depth"],
                "salinity": measurement["salinity"],
                "quality_flag": measurement["quality_flag"]
            })
        
        return {
            "profile_id": profile_id,
            "float_id": profile["float_id"],
            "date": profile["profile_date"],
            "location": {
                "latitude": profile["latitude"],
                "longitude": profile["longitude"]
            },
            "data": data,
            "metadata": {
                "parameter": "salinity",
                "units": "PSU",
                "depth_units": "meters"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get salinity-depth data", error=str(e), profile_id=profile_id)
        raise HTTPException(status_code=500, detail=f"Failed to get salinity-depth data: {str(e)}")


@router.get("/temperature-trend")
async def get_temperature_trend():
    """Get temperature trend data over time."""
    try:
        profiles = simple_query_service.get_sample_profiles(50)
        
        # Create time series data
        data = []
        for profile in profiles:
            # Get surface temperature (first measurement)
            measurements = profile.get("measurements", [])
            if measurements:
                surface_temp = measurements[0]["temperature"]
                data.append({
                    "date": profile["profile_date"],
                    "temperature": surface_temp,
                    "float_id": profile["float_id"],
                    "location": {
                        "latitude": profile["latitude"],
                        "longitude": profile["longitude"]
                    }
                })
        
        # Sort by date
        data.sort(key=lambda x: x["date"])
        
        return {
            "data": data,
            "metadata": {
                "parameter": "surface_temperature",
                "units": "°C",
                "description": "Surface temperature trends from ARGO floats"
            }
        }
        
    except Exception as e:
        logger.error("Failed to get temperature trend", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get temperature trend: {str(e)}")


@router.get("/export/csv/{profile_id}")
async def export_profile_csv(profile_id: str):
    """Export profile data as CSV."""
    try:
        profile = simple_query_service.get_profile_data(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Generate CSV content
        csv_lines = [
            "level,pressure,depth,temperature,salinity,quality_flag"
        ]
        
        for i, measurement in enumerate(profile.get("measurements", [])):
            csv_lines.append(
                f"{i+1},{measurement['pressure']:.2f},{measurement['depth']:.1f},"
                f"{measurement['temperature']:.3f},{measurement['salinity']:.3f},"
                f"{measurement['quality_flag']}"
            )
        
        csv_content = "\n".join(csv_lines)
        
        return {
            "filename": f"argo_profile_{profile_id}.csv",
            "content": csv_content,
            "content_type": "text/csv",
            "metadata": {
                "profile_id": profile_id,
                "float_id": profile["float_id"],
                "date": profile["profile_date"],
                "location": {
                    "latitude": profile["latitude"],
                    "longitude": profile["longitude"]
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to export CSV", error=str(e), profile_id=profile_id)
        raise HTTPException(status_code=500, detail=f"Failed to export CSV: {str(e)}")


@router.get("/search")
async def search_profiles(
    q: Optional[str] = None,
    region: Optional[str] = None,
    parameter: Optional[str] = None,
    limit: int = 20
):
    """Search profiles based on query parameters."""
    try:
        profiles = simple_query_service.get_sample_profiles(limit * 2)  # Get more to filter
        
        # Simple filtering
        filtered_profiles = []
        for profile in profiles:
            include = True
            
            # Filter by region (simple keyword matching)
            if region:
                region_lower = region.lower()
                float_data = simple_query_service.get_float_data(profile["float_id"])
                if float_data:
                    float_name_lower = float_data["name"].lower()
                    if region_lower not in float_name_lower:
                        include = False
            
            # Filter by parameter availability
            if parameter:
                param_lower = parameter.lower()
                if param_lower == "temperature" and not profile.get("has_temperature"):
                    include = False
                elif param_lower == "salinity" and not profile.get("has_salinity"):
                    include = False
                elif param_lower == "bgc" and not profile.get("has_bgc_data"):
                    include = False
            
            if include:
                filtered_profiles.append(profile)
            
            if len(filtered_profiles) >= limit:
                break
        
        # Format profiles with profile_id for frontend
        formatted_profiles = []
        for profile in filtered_profiles[:limit]:
            formatted_profile = profile.copy()
            formatted_profile["profile_id"] = profile["id"]
            formatted_profiles.append(formatted_profile)
        
        return {
            "profiles": formatted_profiles,
            "total": len(filtered_profiles),
            "query": {
                "text": q,
                "region": region,
                "parameter": parameter,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error("Failed to search profiles", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to search profiles: {str(e)}")


@router.get("/export/profiles/csv")
async def export_all_profiles_csv():
    """Export all sample profiles as CSV."""
    try:
        from fastapi.responses import Response
        import csv
        import io
        
        profiles = simple_query_service.get_sample_profiles(100)
        
        # Create CSV content
        output = io.StringIO()
        if profiles:
            # Get all field names from first profile
            fieldnames = ["id", "float_id", "profile_number", "profile_date", 
                         "latitude", "longitude", "number_of_levels", 
                         "pressure_min", "pressure_max", "depth_min", "depth_max",
                         "has_temperature", "has_salinity", "has_pressure", "has_bgc_data"]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for profile in profiles:
                row = {field: profile.get(field, "") for field in fieldnames}
                writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        from datetime import datetime
        filename = f"argo_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error("Failed to export profiles CSV", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to export CSV: {str(e)}")


@router.get("/export/measurements/{profile_id}/csv")
async def export_measurements_csv(profile_id: str):
    """Export measurements for a profile as CSV."""
    try:
        from fastapi.responses import Response
        import csv
        import io
        
        profile = simple_query_service.get_profile_data(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Create CSV content
        output = io.StringIO()
        fieldnames = ["level", "pressure", "depth", "temperature", "salinity", "quality_flag"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, measurement in enumerate(profile.get("measurements", []), 1):
            writer.writerow({
                "level": i,
                "pressure": f"{measurement['pressure']:.2f}",
                "depth": f"{measurement['depth']:.1f}",
                "temperature": f"{measurement['temperature']:.3f}",
                "salinity": f"{measurement['salinity']:.3f}",
                "quality_flag": measurement['quality_flag']
            })
        
        csv_content = output.getvalue()
        output.close()
        
        filename = f"argo_measurements_{profile_id}.csv"
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to export measurements CSV", error=str(e), profile_id=profile_id)
        raise HTTPException(status_code=500, detail=f"Failed to export CSV: {str(e)}")


@router.get("/profiles")
async def get_simple_profiles(
    page: int = 1,
    page_size: int = 20
):
    """Get sample profiles (fallback endpoint that doesn't require database)."""
    try:
        profiles = simple_query_service.get_sample_profiles(page_size * 2)
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_profiles = profiles[start:end]
        
        return {
            "profiles": paginated_profiles,
            "total": len(profiles),
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        logger.error("Failed to get simple profiles", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get profiles: {str(e)}")


@router.get("/floats/list")
async def get_simple_floats_list(
    page: int = 1,
    page_size: int = 20
):
    """Get sample floats as list (fallback endpoint that doesn't require database)."""
    try:
        floats = simple_query_service.get_sample_floats()
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_floats = floats[start:end]
        
        return {
            "floats": paginated_floats,
            "total": len(floats),
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        logger.error("Failed to get simple floats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get floats: {str(e)}")
