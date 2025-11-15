"""Simple query service for prototype - no external dependencies."""
from typing import Dict, Any, Optional
from datetime import datetime

from app.services.simple_llm import simple_llm
from app.data.sample_ocean_data import get_sample_data

class SimpleQueryService:
    """Simple query service using rule-based LLM."""
    
    def __init__(self):
        self.llm = simple_llm
        self.sample_data = get_sample_data()
    
    def detect_user_type(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Detect user type based on query and context."""
        if context and "user_type" in context:
            return context["user_type"]
        
        query_lower = query.lower()
        
        # Simple keyword-based detection
        if any(word in query_lower for word in ["research", "analysis", "correlation", "statistical"]):
            return "researcher"
        elif any(word in query_lower for word in ["learn", "understand", "explain", "what is"]):
            return "student"
        elif any(word in query_lower for word in ["fish", "fishing", "catch", "marine life"]):
            return "fishery"
        elif any(word in query_lower for word in ["shipping", "navigation", "route", "vessel"]):
            return "shipping"
        elif any(word in query_lower for word in ["management", "policy", "decision", "planning"]):
            return "manager"
        else:
            return "general"
    
    async def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process a natural language query."""
        
        # Detect user type
        user_type = self.detect_user_type(query, context)
        
        # Generate response using simple LLM
        response_data = self.llm.generate_response(query, user_type)
        
        # Add visualization data based on query intent
        viz_type = response_data.get("visualization", {}).get("type", "map")
        data_source = response_data.get("visualization", {}).get("config", {}).get("data_source", "all_floats")
        
        # Add actual data for visualizations
        if viz_type == "map":
            # Add float locations for map
            floats_data = self.get_sample_floats()
            float_features = []
            for float_data in floats_data:
                float_features.append({
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
            response_data["visualization"]["data"] = {
                "type": "FeatureCollection",
                "features": float_features
            }
        
        elif viz_type in ["line_chart", "temperature_depth_chart", "salinity_depth_chart"]:
            # Add profile data for charts
            profiles = self.get_sample_profiles(10)
            if profiles:
                profile = profiles[0]  # Use first profile
                chart_data = []
                for measurement in profile.get("measurements", []):
                    if viz_type == "temperature_depth_chart":
                        chart_data.append({
                            "depth": measurement["depth"],
                            "temperature": measurement["temperature"]
                        })
                    elif viz_type == "salinity_depth_chart":
                        chart_data.append({
                            "depth": measurement["depth"],
                            "salinity": measurement["salinity"]
                        })
                    else:
                        chart_data.append({
                            "depth": measurement["depth"],
                            "temperature": measurement.get("temperature"),
                            "salinity": measurement.get("salinity")
                        })
                response_data["visualization"]["data"] = chart_data
                response_data["visualization"]["profile_id"] = profile["id"]
        
        elif viz_type == "time_series":
            # Add time series data
            profiles = self.get_sample_profiles(50)
            time_series_data = []
            for profile in profiles[:30]:  # Limit to 30 points
                measurements = profile.get("measurements", [])
                if measurements:
                    surface_temp = measurements[0]["temperature"]
                    time_series_data.append({
                        "date": profile["profile_date"],
                        "temperature": surface_temp,
                        "float_id": profile["float_id"]
                    })
            response_data["visualization"]["data"] = sorted(time_series_data, key=lambda x: x["date"])
        
        # Add downloadable data table
        profiles = self.get_sample_profiles(100)
        response_data["data_table"] = {
            "profiles": profiles[:50],  # Limit to 50 for display
            "floats": self.get_sample_floats()
        }
        
        # Add session information
        response_data.update({
            "session_id": session_id,
            "user_id": user_id,
            "context": context or {}
        })
        
        return response_data
    
    def get_sample_profiles(self, limit: int = 10) -> list:
        """Get sample profiles for visualization."""
        profiles = self.sample_data["profiles"]
        return profiles[:limit]
    
    def get_sample_floats(self) -> list:
        """Get sample float data."""
        return self.sample_data["floats"]
    
    def get_profile_data(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get specific profile data."""
        profiles = self.sample_data["profiles"]
        for profile in profiles:
            if profile["id"] == profile_id:
                return profile
        return None
    
    def get_float_data(self, float_id: str) -> Optional[Dict[str, Any]]:
        """Get specific float data."""
        floats = self.sample_data["floats"]
        for float_data in floats:
            if float_data["float_id"] == float_id:
                return float_data
        return None

# Global instance
simple_query_service = SimpleQueryService()
