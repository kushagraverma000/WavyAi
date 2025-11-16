from __future__ import annotations

from typing import Any, Dict, List


SAMPLE_FLOATS: List[Dict[str, Any]] = [
    {
        "id": "float-1",
        "float_id": "5906468",
        "platform_number": "NA-001",
        "wmo_number": None,
        "name": "North Atlantic Float",
        "project_name": "WavyAI Demo Mission",
        "deployment_date": "2024-01-15T00:00:00Z",
        "deployment_latitude": 45.2,
        "deployment_longitude": -30.1,
        "last_profile_date": "2024-11-10T00:00:00Z",
        "last_latitude": 45.2,
        "last_longitude": -30.1,
        "current_status": "active",
        "metadata": {"region": "North Atlantic", "cycles": 156},
    },
    {
        "id": "float-2",
        "float_id": "5905123",
        "platform_number": "SO-014",
        "wmo_number": None,
        "name": "Southern Ocean Float",
        "project_name": "Deep Waters Campaign",
        "deployment_date": "2023-09-03T00:00:00Z",
        "deployment_latitude": -55.8,
        "deployment_longitude": 140.3,
        "last_profile_date": "2024-10-02T00:00:00Z",
        "last_latitude": -55.2,
        "last_longitude": 142.1,
        "current_status": "active",
        "metadata": {"region": "Southern Ocean", "cycles": 98},
    },
]


SAMPLE_PROFILES: List[Dict[str, Any]] = [
    {
        "id": "profile-1",
        "float_id": "5906468",
        "profile_number": 156,
        "profile_date": "2024-11-10T00:00:00Z",
        "latitude": 45.2,
        "longitude": -30.1,
        "number_of_levels": 120,
        "pressure_min": 5.0,
        "pressure_max": 2000.0,
        "depth_min": 5.0,
        "depth_max": 2000.0,
        "has_temperature": True,
        "has_salinity": True,
        "has_pressure": True,
        "has_bgc_data": True,
        "summary": "Latest profile from the North Atlantic demonstration float.",
        "metadata": {"region": "North Atlantic"},
    },
    {
        "id": "profile-2",
        "float_id": "5905123",
        "profile_number": 98,
        "profile_date": "2024-10-02T00:00:00Z",
        "latitude": -55.2,
        "longitude": 142.1,
        "number_of_levels": 95,
        "pressure_min": 5.0,
        "pressure_max": 1500.0,
        "depth_min": 5.0,
        "depth_max": 1500.0,
        "has_temperature": True,
        "has_salinity": True,
        "has_pressure": True,
        "has_bgc_data": False,
        "summary": "Southern Ocean profile highlighting the Antarctic Circumpolar Current.",
        "metadata": {"region": "Southern Ocean"},
    },
]


TEMPERATURE_DEPTH_DATA: List[Dict[str, Any]] = [
    {"depth": i * 100, "temperature": 25 - i * 0.4} for i in range(20)
]


SALINITY_DEPTH_DATA: List[Dict[str, Any]] = [
    {"depth": i * 100, "salinity": 35 - i * 0.02} for i in range(20)
]
