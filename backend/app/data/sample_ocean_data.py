"""Sample ocean data for prototype demonstration."""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Sample ARGO float data
SAMPLE_FLOATS = [
    {
        "id": "float_001",
        "float_id": "5906468",
        "platform_number": "5906468",
        "wmo_number": "5906468",
        "name": "North Atlantic Float",
        "project_name": "ARGO",
        "deployment_date": "2023-01-15",
        "deployment_latitude": 45.2,
        "deployment_longitude": -30.1,
        "last_profile_date": "2024-11-10",
        "last_latitude": 46.8,
        "last_longitude": -28.5,
        "current_status": "active",
        "total_profiles": 156
    },
    {
        "id": "float_002", 
        "float_id": "5906469",
        "platform_number": "5906469",
        "wmo_number": "5906469",
        "name": "Pacific Equatorial Float",
        "project_name": "ARGO",
        "deployment_date": "2023-03-20",
        "deployment_latitude": 0.5,
        "deployment_longitude": -140.2,
        "last_profile_date": "2024-11-12",
        "last_latitude": 2.1,
        "last_longitude": -138.7,
        "current_status": "active",
        "total_profiles": 142
    },
    {
        "id": "float_003",
        "float_id": "5906470", 
        "platform_number": "5906470",
        "wmo_number": "5906470",
        "name": "Southern Ocean Float",
        "project_name": "ARGO",
        "deployment_date": "2023-02-10",
        "deployment_latitude": -55.3,
        "deployment_longitude": 85.4,
        "last_profile_date": "2024-11-08",
        "last_latitude": -52.1,
        "last_longitude": 88.2,
        "current_status": "active",
        "total_profiles": 168
    }
]

def generate_profile_data(float_id: str, profile_num: int, base_lat: float, base_lon: float, date: str) -> Dict[str, Any]:
    """Generate realistic profile data for a float."""
    # Add some drift to position
    lat_drift = random.uniform(-0.5, 0.5)
    lon_drift = random.uniform(-0.5, 0.5)
    
    # Generate depth levels (0-2000m)
    depths = list(range(5, 2001, 50))  # Every 50m from 5m to 2000m
    
    # Generate realistic temperature profile (warmer at surface, colder at depth)
    temperatures = []
    for depth in depths:
        if depth < 100:
            # Mixed layer - relatively constant temperature
            temp = 25.0 - depth * 0.05 + random.uniform(-0.5, 0.5)
        elif depth < 1000:
            # Thermocline - rapid temperature decrease
            temp = 20.0 - (depth - 100) * 0.015 + random.uniform(-0.3, 0.3)
        else:
            # Deep water - slowly decreasing temperature
            temp = 6.5 - (depth - 1000) * 0.002 + random.uniform(-0.2, 0.2)
        temperatures.append(max(temp, 2.0))  # Minimum temperature 2°C
    
    # Generate realistic salinity profile
    salinities = []
    for depth in depths:
        if depth < 50:
            # Surface mixed layer
            sal = 35.0 + random.uniform(-0.2, 0.2)
        elif depth < 500:
            # Halocline
            sal = 35.0 + (depth - 50) * 0.0005 + random.uniform(-0.1, 0.1)
        else:
            # Deep water - relatively stable
            sal = 34.8 + random.uniform(-0.05, 0.05)
        salinities.append(sal)
    
    # Generate pressure (approximately depth in decibars)
    pressures = [d * 1.02 + random.uniform(-0.5, 0.5) for d in depths]
    
    return {
        "id": f"profile_{float_id}_{profile_num:03d}",
        "float_id": float_id,
        "profile_number": profile_num,
        "profile_date": date,
        "latitude": base_lat + lat_drift,
        "longitude": base_lon + lon_drift,
        "number_of_levels": len(depths),
        "pressure_min": min(pressures),
        "pressure_max": max(pressures),
        "depth_min": min(depths),
        "depth_max": max(depths),
        "has_temperature": True,
        "has_salinity": True,
        "has_pressure": True,
        "has_bgc_data": random.choice([True, False]),
        "measurements": [
            {
                "level": i + 1,
                "pressure": pressures[i],
                "depth": depths[i],
                "temperature": temperatures[i],
                "salinity": salinities[i],
                "quality_flag": random.choice([1, 1, 1, 1, 2])  # Mostly good quality
            }
            for i in range(len(depths))
        ]
    }

def generate_sample_profiles() -> List[Dict[str, Any]]:
    """Generate sample profiles for all floats."""
    profiles = []
    
    for float_data in SAMPLE_FLOATS:
        float_id = float_data["float_id"]
        base_lat = float_data["deployment_latitude"]
        base_lon = float_data["deployment_longitude"]
        
        # Generate profiles over the last year
        start_date = datetime.strptime(float_data["deployment_date"], "%Y-%m-%d")
        end_date = datetime.now()
        
        profile_num = 1
        current_date = start_date
        
        while current_date <= end_date and profile_num <= float_data["total_profiles"]:
            # ARGO floats typically profile every 10 days
            profile_data = generate_profile_data(
                float_id, 
                profile_num, 
                base_lat, 
                base_lon, 
                current_date.strftime("%Y-%m-%d")
            )
            profiles.append(profile_data)
            
            # Move to next profile (10 days later)
            current_date += timedelta(days=10)
            profile_num += 1
            
            # Add some position drift over time
            base_lat += random.uniform(-0.1, 0.1)
            base_lon += random.uniform(-0.1, 0.1)
    
    return profiles

# Knowledge base for answering questions
OCEAN_KNOWLEDGE = {
    "temperature": {
        "description": "Ocean temperature varies with depth, latitude, and season. Surface waters are typically warmer, with temperature decreasing with depth.",
        "typical_ranges": {
            "surface": "15-30°C in most regions",
            "thermocline": "5-20°C rapid decrease zone",
            "deep_water": "2-6°C relatively stable"
        },
        "factors": ["solar heating", "latitude", "season", "ocean currents", "mixing"]
    },
    "salinity": {
        "description": "Ocean salinity measures dissolved salt content, typically around 35 PSU (Practical Salinity Units).",
        "typical_ranges": {
            "surface": "33-37 PSU depending on region",
            "deep_water": "34.6-34.8 PSU relatively stable"
        },
        "factors": ["evaporation", "precipitation", "river input", "ice formation/melting"]
    },
    "argo_floats": {
        "description": "ARGO floats are autonomous profiling instruments that measure temperature and salinity from surface to 2000m depth.",
        "cycle": "10-day cycle: drift at 1000m, dive to 2000m, profile while ascending, transmit data at surface",
        "coverage": "Global ocean coverage with ~4000 active floats",
        "data_quality": "Real-time and delayed-mode quality control"
    },
    "ocean_structure": {
        "mixed_layer": "Surface layer with relatively uniform temperature and salinity due to wind mixing",
        "thermocline": "Layer with rapid temperature decrease with depth",
        "halocline": "Layer with rapid salinity change with depth",
        "deep_water": "Cold, dense water masses below ~1000m"
    }
}

# Sample queries and responses for the prototype
SAMPLE_QA_PAIRS = [
    {
        "query": "What is the temperature profile in the North Atlantic?",
        "response": "Based on ARGO float data from the North Atlantic, the temperature profile shows typical oceanic structure. Surface temperatures range from 20-25°C, decreasing rapidly through the thermocline (100-1000m depth) to about 6-8°C, then gradually cooling to 2-4°C in deep waters below 1000m. This profile reflects the typical North Atlantic water mass structure with warm surface waters and cold deep waters.",
        "visualization_type": "temperature_depth_chart",
        "data_source": "float_001"
    },
    {
        "query": "How does salinity change with depth?",
        "response": "Salinity profiles show distinct patterns with depth. In most ocean regions, surface salinity ranges from 34-36 PSU, often with a halocline (rapid salinity change) in the upper few hundred meters. Deep waters typically maintain stable salinity around 34.6-34.8 PSU. The exact profile depends on local factors like evaporation, precipitation, and water mass mixing.",
        "visualization_type": "salinity_depth_chart",
        "data_source": "multiple_floats"
    },
    {
        "query": "Where are ARGO floats located?",
        "response": "ARGO floats provide global ocean coverage with approximately 4000 active floats worldwide. Our current dataset shows floats in the North Atlantic, Pacific Equatorial region, and Southern Ocean. Each float follows a 10-day cycle, profiling from surface to 2000m depth while drifting with ocean currents.",
        "visualization_type": "map",
        "data_source": "all_floats"
    },
    {
        "query": "What is the ocean temperature trend?",
        "response": "Ocean temperature analysis from ARGO data shows the characteristic vertical structure with warm surface waters (20-25°C) transitioning through the thermocline to cold deep waters (2-6°C). Regional variations exist, with equatorial regions showing warmer surface temperatures and polar regions showing cooler profiles throughout the water column.",
        "visualization_type": "temperature_trend_chart",
        "data_source": "time_series"
    }
]

def get_sample_data():
    """Get all sample data for the prototype."""
    return {
        "floats": SAMPLE_FLOATS,
        "profiles": generate_sample_profiles(),
        "knowledge": OCEAN_KNOWLEDGE,
        "qa_pairs": SAMPLE_QA_PAIRS
    }
