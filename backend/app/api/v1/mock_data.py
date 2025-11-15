"""Mock data endpoints for testing frontend functionality."""
from fastapi import APIRouter
from typing import Optional
import uuid
from datetime import datetime, timedelta
import random

router = APIRouter()

# Generate mock data
def generate_mock_floats(count: int = 10):
    """Generate mock float data."""
    features = []
    for i in range(count):
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    random.uniform(-180, 180),  # longitude
                    random.uniform(-60, 60)     # latitude
                ]
            },
            "properties": {
                "float_id": f"590{i:04d}",
                "platform_number": f"590{i:04d}",
                "status": random.choice(["active", "inactive"]),
                "last_profile_date": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                "project_name": "ARGO_GLOBAL",
                "deployment_date": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
            }
        })
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "total_floats": count,
            "bbox": None,
            "status_filter": None
        }
    }

def generate_mock_profiles(count: int = 20):
    """Generate mock profile data."""
    profiles = []
    for i in range(count):
        profile_id = str(uuid.uuid4())
        profiles.append({
            "profile_id": profile_id,
            "float_id": f"590{i//4:04d}",
            "profile_number": (i % 4) + 1,
            "date": (datetime.now() - timedelta(days=random.randint(0, 100))).isoformat(),
            "location": [
                random.uniform(-180, 180),  # longitude
                random.uniform(-60, 60)     # latitude
            ],
            "depth_range": f"{random.randint(5, 50)}-{random.randint(1500, 2000)}m",
            "has_temperature": True,
            "has_salinity": True,
            "has_bgc_data": random.choice([True, False]),
            "number_of_levels": random.randint(50, 150),
            "summary": f"ARGO profile {(i % 4) + 1} from float 590{i//4:04d} with temperature and salinity measurements"
        })
    
    return {
        "profiles": profiles,
        "total": count,
        "filters": {}
    }

def generate_mock_chart_data(chart_type: str = "temperature"):
    """Generate mock chart data."""
    data = []
    for i in range(50):
        depth = i * 40  # 0, 40, 80, ... 1960m
        pressure = depth / 1.02
        
        if chart_type == "temperature":
            temperature = 25 - (depth / 100) + random.uniform(-1, 1)
            temperature = max(temperature, 2)
            data.append({
                "depth": depth,
                "temperature": round(temperature, 2),
                "pressure": round(pressure, 1),
                "salinity": round(35 + random.uniform(-0.5, 0.5), 2)
            })
        elif chart_type == "salinity":
            salinity = 35 + (depth / 2000) * random.uniform(-0.5, 0.5) + random.uniform(-0.2, 0.2)
            data.append({
                "depth": depth,
                "salinity": round(salinity, 2),
                "pressure": round(pressure, 1),
                "temperature": round(25 - (depth / 100), 2)
            })
        elif chart_type == "ts-diagram":
            temperature = 25 - (depth / 100) + random.uniform(-1, 1)
            salinity = 35 + random.uniform(-0.5, 0.5)
            data.append({
                "temperature": round(temperature, 2),
                "salinity": round(salinity, 2),
                "depth": depth,
                "pressure": round(pressure, 1)
            })
    
    return {
        "profile_info": {
            "profile_id": str(uuid.uuid4()),
            "float_id": "59001",
            "profile_number": 1,
            "date": datetime.now().isoformat(),
            "location": [-40.0, 30.0]
        },
        "data": data,
        "chart_config": {
            "type": "line" if chart_type != "ts-diagram" else "scatter",
            "x_axis": chart_type if chart_type != "ts-diagram" else "salinity",
            "y_axis": "depth" if chart_type != "ts-diagram" else "temperature",
            "title": f"{chart_type.title()} Profile - Float 59001",
            "x_label": f"{chart_type.title()} ({'°C' if chart_type == 'temperature' else 'PSU' if chart_type == 'salinity' else 'PSU'})",
            "y_label": "Depth (m)" if chart_type != "ts-diagram" else "Temperature (°C)",
            "invert_y": chart_type != "ts-diagram"
        }
    }

@router.get("/mock/map/floats")
async def get_mock_float_locations(limit: int = 10):
    """Get mock float locations for map visualization."""
    return generate_mock_floats(limit)

@router.get("/mock/search/profiles")
async def search_mock_profiles(limit: int = 20):
    """Search mock profiles."""
    return generate_mock_profiles(limit)

@router.get("/mock/charts/temperature-depth/{profile_id}")
async def get_mock_temperature_chart(profile_id: str):
    """Get mock temperature-depth chart data."""
    return generate_mock_chart_data("temperature")

@router.get("/mock/charts/salinity-depth/{profile_id}")
async def get_mock_salinity_chart(profile_id: str):
    """Get mock salinity-depth chart data."""
    return generate_mock_chart_data("salinity")

@router.get("/mock/charts/ts-diagram/{profile_id}")
async def get_mock_ts_diagram(profile_id: str):
    """Get mock T-S diagram data."""
    return generate_mock_chart_data("ts-diagram")

@router.post("/mock/query")
async def mock_query_endpoint(request: dict):
    """Mock query endpoint."""
    query = request.get("query", "")
    
    # Generate a mock response based on the query
    response_text = f"Based on your query '{query}', I found relevant oceanographic data. "
    
    if "temperature" in query.lower():
        response_text += "The temperature profiles show typical oceanic stratification with warmer surface waters and cooler deep waters. "
    
    if "salinity" in query.lower():
        response_text += "Salinity measurements indicate typical ocean water mass characteristics. "
    
    if "atlantic" in query.lower():
        response_text += "Data from the Atlantic Ocean region shows characteristic water mass properties. "
    
    response_text += "You can view the detailed measurements in the charts and download the data for further analysis."
    
    return {
        "response": response_text,
        "sources": [
            {
                "type": "profile",
                "id": str(uuid.uuid4()),
                "float_id": "59001",
                "date": datetime.now().isoformat(),
                "location": {"lat": 30.0, "lon": -40.0}
            }
        ],
        "visualization": {
            "type": "map",
            "title": "ARGO Float Locations",
            "config": {"type": "map"}
        },
        "user_type": "researcher",
        "query_intent": "data_exploration",
        "entities": {"location": "Atlantic Ocean", "parameter": "temperature"},
        "metadata": {"model": "mock", "confidence": 0.9},
        "timestamp": datetime.now().isoformat()
    }
