"""RAG service for retrieval-augmented generation."""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.vector_db import get_vector_db
from app.core.redis_client import get_redis_client
from app.services.embedding_service import get_embedding_service
try:
    from app.services.vector_service import get_vector_service
except ImportError:
    from app.services.local_vector_service import get_vector_service
from app.models.user_context import UserContext
from app.models.profile import Profile

logger = get_logger(__name__)


class RAGService:
    """Service for RAG (Retrieval-Augmented Generation)."""

    def __init__(self, db: Session):
        """Initialize RAG service."""
        self.db = db
        self.vector_db = get_vector_db()
        self.redis_client = get_redis_client()
        self.embedding_service = get_embedding_service()
        self.gemini_service = get_gemini_service()

    async def search(
        self,
        query: str,
        user_context: Optional[UserContext],
        entities: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Perform hybrid search (vector + SQL)."""
        try:
            # Check cache first
            cache_key = f"rag_search:{hash(query)}"
            cached_result = self.redis_client.get(cache_key) if self.redis_client else None
            if cached_result:
                logger.info("Cache hit for RAG search", query=query)
                return cached_result

            results = {
                "profiles": [],
                "sources": [],
                "scores": [],
            }

            # 1. Vector search (semantic search)
            vector_results = []
            if self.embedding_service and self.vector_db:
                query_embedding = self.embedding_service.generate_embedding(query)
                if query_embedding:
                    vector_results = self.vector_db.search(
                        query_vector=query_embedding,
                        limit=10,
                    )
                    logger.info(f"Vector search found {len(vector_results)} results")

            # 2. SQL search (exact filtering)
            query_obj = self.db.query(Profile)
            
            # Filter by parameters
            if entities.get("parameters"):
                if "temperature" in entities["parameters"]:
                    query_obj = query_obj.filter(Profile.has_temperature == True)
                if "salinity" in entities["parameters"]:
                    query_obj = query_obj.filter(Profile.has_salinity == True)
                if "oxygen" in entities["parameters"]:
                    query_obj = query_obj.filter(Profile.has_bgc_data == True)
            
            # Filter by depth ranges
            if entities.get("depth_ranges"):
                # Filter by depth ranges if available
                pass  # TODO: Add depth filtering when measurements are loaded
            
            # Get SQL results
            sql_profiles = query_obj.limit(20).all()
            logger.info(f"SQL search found {len(sql_profiles)} profiles")

            # 3. Combine results (prioritize vector search, then SQL)
            profile_ids = set()
            
            # Add vector search results
            for vec_result in vector_results:
                profile_id = vec_result.get("payload", {}).get("profile_id")
                if profile_id:
                    profile_ids.add(profile_id)
                    results["sources"].append({
                        "type": "profile",
                        "id": str(profile_id),
                        "score": vec_result.get("score", 0.0),
                        **vec_result.get("payload", {}),
                    })
                    results["scores"].append(vec_result.get("score", 0.0))
            
            # Add SQL results (avoid duplicates)
            for profile in sql_profiles:
                if str(profile.id) not in profile_ids:
                    profile_ids.add(str(profile.id))
                    results["sources"].append({
                        "type": "profile",
                        "id": str(profile.id),
                        "float_id": str(profile.float_id),
                        "date": profile.profile_date.isoformat(),
                        "location": {"lat": profile.latitude, "lon": profile.longitude},
                        "score": 0.5,  # Default score for SQL results
                    })
                    results["scores"].append(0.5)
            
            results["profiles"] = list(profile_ids)
            
            # Limit total results
            results["sources"] = results["sources"][:10]
            results["scores"] = results["scores"][:10]
            results["profiles"] = results["profiles"][:10]

            # Cache results for 1 hour
            if self.redis_client:
                self.redis_client.set(cache_key, results, ttl=3600)

            return results

        except Exception as e:
            logger.error("RAG search failed", error=str(e), exc_info=True)
            return {"profiles": [], "sources": [], "scores": []}

    async def generate_response(
        self,
        query: str,
        rag_results: Dict[str, Any],
        user_context: Optional[UserContext],
        query_intent: Optional[str],
        entities: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate adaptive response based on user context."""
        try:
            # Check cache first
            cache_key = f"rag_response:{hash(query)}:{user_context.user_type if user_context else 'general'}"
            cached_response = self.redis_client.get(cache_key) if self.redis_client else None
            if cached_response:
                logger.info("Cache hit for RAG response", query=query)
                return cached_response

            user_type = user_context.user_type if user_context else "general"
            sources = rag_results.get("sources", [])
            
            # Build context from sources
            context = None
            if sources:
                context_lines = []
                for source in sources[:5]:
                    context_lines.append(
                        f"Profile {source.get('id', 'unknown')} at "
                        f"{source.get('location', {}).get('lat', 0):.2f}°N, "
                        f"{source.get('location', {}).get('lon', 0):.2f}°E "
                        f"on {source.get('date', 'unknown date')}"
                    )
                context = "\n".join(context_lines)

            # Generate response using Gemini
            response = self.gemini_service.generate_response(
                query=query,
                context=context,
                user_type=user_type,
                query_intent=query_intent,
                sources=sources,
            )

            # Cache response for 1 hour
            if self.redis_client:
                self.redis_client.set(cache_key, response, ttl=3600)

            return response

        except Exception as e:
            logger.error("Response generation failed", error=str(e), exc_info=True)
            return {
                "text": "I'm sorry, I encountered an error processing your query. Please try again.",
                "confidence": 0.0,
            }

    async def generate_visualization(
        self,
        query: str,
        rag_results: Dict[str, Any],
        user_context: Optional[UserContext],
    ) -> Optional[Dict[str, Any]]:
        """Generate visualization configuration."""
        try:
            # TODO: Implement visualization generation based on user type and data
            # For now, return a placeholder configuration

            user_type = user_context.user_type if user_context else "general"

            visualization_configs = {
                "researcher": {
                    "type": "ts_diagram",
                    "title": "Temperature-Salinity Diagram",
                    "config": {
                        "x_axis": "salinity",
                        "y_axis": "temperature",
                        "color_by": "depth",
                    },
                },
                "student": {
                    "type": "line_chart",
                    "title": "Ocean Profile",
                    "config": {
                        "x_axis": "depth",
                        "y_axis": "temperature",
                        "annotations": True,
                    },
                },
                "manager": {
                    "type": "map",
                    "title": "Data Overview",
                    "config": {
                        "layers": ["floats", "temperature"],
                        "time_animation": True,
                    },
                },
                "general": {
                    "type": "map",
                    "title": "ARGO Float Locations",
                    "config": {
                        "layers": ["floats"],
                    },
                },
            }

            return visualization_configs.get(user_type, visualization_configs["general"])

        except Exception as e:
            logger.error("Visualization generation failed", error=str(e))
            return None

