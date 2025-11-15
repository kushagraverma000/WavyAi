"""Simple LLM service for prototype - no API keys required."""
import re
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.data.sample_ocean_data import OCEAN_KNOWLEDGE, SAMPLE_QA_PAIRS, get_sample_data

class SimpleLLMService:
    """Simple rule-based LLM service for prototype demonstration."""
    
    def __init__(self):
        self.sample_data = get_sample_data()
        self.knowledge = OCEAN_KNOWLEDGE
        self.qa_pairs = SAMPLE_QA_PAIRS
        
        # Keywords for different topics
        self.keywords = {
            "temperature": ["temperature", "temp", "thermal", "warm", "cold", "heat"],
            "salinity": ["salinity", "salt", "saline", "psu", "conductivity"],
            "depth": ["depth", "deep", "shallow", "surface", "bottom", "vertical"],
            "location": ["where", "location", "position", "latitude", "longitude", "region"],
            "float": ["float", "argo", "instrument", "sensor", "platform"],
            "profile": ["profile", "measurement", "data", "observation"],
            "trend": ["trend", "change", "time", "temporal", "variation", "pattern"],
            "structure": ["structure", "layer", "thermocline", "halocline", "mixed"]
        }
    
    def classify_query_intent(self, query: str) -> str:
        """Classify the intent of the user query."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["where", "location", "map", "position"]):
            return "location_query"
        elif any(word in query_lower for word in ["temperature", "temp", "thermal"]):
            return "temperature_query"
        elif any(word in query_lower for word in ["salinity", "salt"]):
            return "salinity_query"
        elif any(word in query_lower for word in ["trend", "change", "time"]):
            return "trend_query"
        elif any(word in query_lower for word in ["profile", "depth"]):
            return "profile_query"
        else:
            return "general_query"
    
    def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from the query."""
        entities = {}
        query_lower = query.lower()
        
        # Extract regions
        regions = {
            "north atlantic": ["north atlantic", "northern atlantic"],
            "pacific": ["pacific", "pacific ocean"],
            "southern ocean": ["southern ocean", "antarctic"],
            "equatorial": ["equatorial", "equator", "tropical"]
        }
        
        for region, keywords in regions.items():
            if any(keyword in query_lower for keyword in keywords):
                entities["region"] = region
                break
        
        # Extract depth ranges
        depth_match = re.search(r'(\d+)\s*(?:m|meter|metre)', query_lower)
        if depth_match:
            entities["depth"] = int(depth_match.group(1))
        
        # Extract parameters
        if any(word in query_lower for word in self.keywords["temperature"]):
            entities["parameter"] = "temperature"
        elif any(word in query_lower for word in self.keywords["salinity"]):
            entities["parameter"] = "salinity"
        
        return entities
    
    def find_best_qa_match(self, query: str) -> Optional[Dict[str, Any]]:
        """Find the best matching Q&A pair."""
        query_lower = query.lower()
        best_match = None
        best_score = 0
        
        for qa_pair in self.qa_pairs:
            qa_query_lower = qa_pair["query"].lower()
            
            # Simple keyword matching score
            query_words = set(query_lower.split())
            qa_words = set(qa_query_lower.split())
            
            # Calculate overlap score
            overlap = len(query_words.intersection(qa_words))
            total_words = len(query_words.union(qa_words))
            score = overlap / total_words if total_words > 0 else 0
            
            if score > best_score and score > 0.2:  # Minimum threshold
                best_score = score
                best_match = qa_pair
        
        return best_match
    
    def generate_response(self, query: str, user_type: str = "general") -> Dict[str, Any]:
        """Generate a response to the user query."""
        # First try to find a matching Q&A pair
        qa_match = self.find_best_qa_match(query)
        if qa_match:
            return self._format_qa_response(qa_match, user_type)
        
        # Otherwise, generate a response based on query classification
        intent = self.classify_query_intent(query)
        entities = self.extract_entities(query)
        
        return self._generate_custom_response(query, intent, entities, user_type)
    
    def _format_qa_response(self, qa_pair: Dict[str, Any], user_type: str) -> Dict[str, Any]:
        """Format a Q&A pair response."""
        response = qa_pair["response"]
        
        # Adapt response based on user type
        if user_type == "student":
            response += "\n\nFor learning more: ARGO floats are autonomous instruments that help scientists understand ocean conditions worldwide."
        elif user_type == "researcher":
            response += "\n\nTechnical note: Data shown includes quality control flags and measurement uncertainties typical of ARGO observations."
        
        # Generate visualization config
        viz_config = self._generate_visualization_config(
            qa_pair["visualization_type"], 
            qa_pair["data_source"]
        )
        
        return {
            "response": response,
            "visualization": viz_config,
            "sources": self._generate_sources(qa_pair["data_source"]),
            "user_type": user_type,
            "query_intent": qa_pair.get("intent", "data_exploration"),
            "entities": {},
            "metadata": {
                "confidence": 0.9,
                "source": "knowledge_base"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_custom_response(self, query: str, intent: str, entities: Dict[str, Any], user_type: str) -> Dict[str, Any]:
        """Generate a custom response based on query analysis."""
        
        if intent == "location_query":
            response = "Our ARGO float network currently includes floats in the North Atlantic (Float 5906468), Pacific Equatorial region (Float 5906469), and Southern Ocean (Float 5906470). These floats provide continuous monitoring of ocean conditions across different climate zones."
            viz_type = "map"
            data_source = "all_floats"
            
        elif intent == "temperature_query":
            region = entities.get("region", "global ocean")
            response = f"Temperature profiles in the {region} show the typical oceanic structure. Surface temperatures are warmest (15-25°C), decreasing rapidly through the thermocline to reach 2-6°C in deep waters. This vertical structure is maintained by solar heating at the surface and cold, dense water formation in polar regions."
            viz_type = "temperature_depth_chart"
            data_source = "float_001"
            
        elif intent == "salinity_query":
            response = "Ocean salinity typically ranges from 34-36 PSU (Practical Salinity Units) at the surface, with variations due to evaporation, precipitation, and freshwater input. Deep waters maintain more stable salinity around 34.6-34.8 PSU. The halocline (rapid salinity change layer) is often found in the upper few hundred meters."
            viz_type = "salinity_depth_chart"
            data_source = "float_002"
            
        elif intent == "trend_query":
            response = "Ocean temperature and salinity patterns show both seasonal and long-term variations. ARGO data reveals the persistent vertical structure with regional differences. Equatorial regions maintain warmer surface temperatures year-round, while polar regions show greater seasonal variation."
            viz_type = "temperature_trend_chart"
            data_source = "time_series"
            
        else:
            # General query
            response = "ARGO floats provide valuable oceanographic data including temperature and salinity profiles from surface to 2000m depth. Our current dataset includes measurements from multiple ocean regions, showing the diverse conditions across different climate zones. Each float follows a 10-day cycle, providing regular updates on ocean conditions."
            viz_type = "map"
            data_source = "all_floats"
        
        # Adapt response for user type
        if user_type == "student":
            response += "\n\n🎓 Learning tip: Ocean layers form due to differences in temperature and salinity, which affect water density."
        elif user_type == "researcher":
            response += "\n\n📊 Technical details: Data includes quality control information and follows ARGO data management standards."
        elif user_type == "fishery":
            response += "\n\n🐟 Fishery relevance: Ocean temperature and salinity affect fish distribution and marine ecosystem health."
        
        viz_config = self._generate_visualization_config(viz_type, data_source)
        
        return {
            "response": response,
            "visualization": viz_config,
            "sources": self._generate_sources(data_source),
            "user_type": user_type,
            "query_intent": intent,
            "entities": entities,
            "metadata": {
                "confidence": 0.8,
                "source": "rule_based_generation"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_visualization_config(self, viz_type: str, data_source: str) -> Dict[str, Any]:
        """Generate visualization configuration."""
        
        if viz_type == "map":
            return {
                "type": "map",
                "title": "ARGO Float Locations",
                "config": {
                    "center": [0, 0],
                    "zoom": 2,
                    "show_floats": True,
                    "show_trajectories": True,
                    "data_source": data_source
                }
            }
        
        elif viz_type == "temperature_depth_chart":
            return {
                "type": "line_chart",
                "title": "Temperature vs Depth Profile",
                "config": {
                    "x_axis": "temperature",
                    "y_axis": "depth",
                    "x_label": "Temperature (°C)",
                    "y_label": "Depth (m)",
                    "invert_y": True,
                    "data_source": data_source
                }
            }
        
        elif viz_type == "salinity_depth_chart":
            return {
                "type": "line_chart", 
                "title": "Salinity vs Depth Profile",
                "config": {
                    "x_axis": "salinity",
                    "y_axis": "depth",
                    "x_label": "Salinity (PSU)",
                    "y_label": "Depth (m)",
                    "invert_y": True,
                    "data_source": data_source
                }
            }
        
        elif viz_type == "temperature_trend_chart":
            return {
                "type": "time_series",
                "title": "Temperature Trends Over Time",
                "config": {
                    "x_axis": "time",
                    "y_axis": "temperature",
                    "x_label": "Date",
                    "y_label": "Temperature (°C)",
                    "data_source": data_source
                }
            }
        
        else:
            return {
                "type": "map",
                "title": "Ocean Data Visualization",
                "config": {
                    "center": [0, 0],
                    "zoom": 2,
                    "data_source": data_source
                }
            }
    
    def _generate_sources(self, data_source: str) -> List[Dict[str, Any]]:
        """Generate source information."""
        sources = []
        
        if data_source == "all_floats" or data_source == "multiple_floats":
            for float_data in self.sample_data["floats"]:
                sources.append({
                    "type": "argo_float",
                    "id": float_data["id"],
                    "float_id": float_data["float_id"],
                    "name": float_data["name"],
                    "location": {
                        "lat": float_data["last_latitude"],
                        "lon": float_data["last_longitude"]
                    },
                    "last_update": float_data["last_profile_date"]
                })
        
        elif data_source.startswith("float_"):
            # Find specific float
            float_num = data_source.split("_")[1]
            if float_num.isdigit():
                idx = int(float_num) - 1
                if 0 <= idx < len(self.sample_data["floats"]):
                    float_data = self.sample_data["floats"][idx]
                    sources.append({
                        "type": "argo_float",
                        "id": float_data["id"],
                        "float_id": float_data["float_id"],
                        "name": float_data["name"],
                        "location": {
                            "lat": float_data["last_latitude"],
                            "lon": float_data["last_longitude"]
                        },
                        "last_update": float_data["last_profile_date"]
                    })
        
        else:
            # Default source
            sources.append({
                "type": "argo_database",
                "id": "argo_global",
                "description": "Global ARGO float database",
                "last_update": datetime.now().strftime("%Y-%m-%d")
            })
        
        return sources

# Global instance
simple_llm = SimpleLLMService()
