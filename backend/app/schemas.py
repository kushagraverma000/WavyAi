from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Location(BaseModel):
    lat: float
    lon: float


class Source(BaseModel):
    type: str
    id: str
    float_id: Optional[str] = None
    date: Optional[str] = None
    location: Optional[Location] = None


class Visualization(BaseModel):
    type: str
    title: str
    config: Dict[str, Any] = {}
    data: Optional[Any] = None
    profile_id: Optional[str] = None


class Profile(BaseModel):
    id: str
    float_id: str
    profile_number: int
    profile_date: datetime
    latitude: float
    longitude: float
    number_of_levels: Optional[int] = None
    pressure_min: Optional[float] = None
    pressure_max: Optional[float] = None
    depth_min: Optional[float] = None
    depth_max: Optional[float] = None
    has_temperature: bool
    has_salinity: bool
    has_pressure: bool
    has_bgc_data: bool
    summary: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Float(BaseModel):
    id: str
    float_id: str
    platform_number: str
    wmo_number: Optional[str] = None
    name: Optional[str] = None
    project_name: Optional[str] = None
    deployment_date: Optional[datetime] = None
    deployment_latitude: Optional[float] = None
    deployment_longitude: Optional[float] = None
    last_profile_date: Optional[datetime] = None
    last_latitude: Optional[float] = None
    last_longitude: Optional[float] = None
    current_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DataTable(BaseModel):
    profiles: Optional[List[Profile]] = None
    floats: Optional[List[Float]] = None


class QueryRequest(BaseModel):
    query: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    selected_date: Optional[date] = None
    context: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    response: str
    sources: List[Source]
    visualization: Optional[Visualization] = None
    data_table: Optional[DataTable] = None
    user_type: Optional[str] = None
    query_intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime


class PaginatedProfiles(BaseModel):
    profiles: List[Profile]
    total: int
    page: int
    page_size: int


class PaginatedFloats(BaseModel):
    floats: List[Float]
    total: int
    page: int
    page_size: int


class DataSummary(BaseModel):
    total_floats: int
    total_profiles: int
    total_files: int
    data_size_mb: float
    date_range: str
    last_updated: str


class DataStatus(BaseModel):
    status: str
    floats_loaded: int
    profiles_loaded: int
    ready_for_queries: bool
    message: str
