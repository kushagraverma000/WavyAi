"""User profiling service for detecting user type and extracting entities."""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
import re
import uuid
from datetime import datetime

from app.core.logging import get_logger
from app.models.user_context import UserContext

logger = get_logger(__name__)


class UserProfilingService:
    """Service for user profiling and context management."""

    def __init__(self, db: Session):
        """Initialize user profiling service."""
        self.db = db

        # Keywords for user type detection
        self.researcher_keywords = [
            "qc", "quality control", "adjusted", "uncertainty", "bias",
            "calibration", "metadata", "doi", "citation", "publication",
            "statistical", "regression", "correlation", "anomaly detection",
        ]
        self.student_keywords = [
            "what is", "explain", "how does", "why", "tell me about",
            "help me understand", "simple", "basic", "beginner",
        ]
        self.manager_keywords = [
            "trend", "summary", "report", "decision", "recommendation",
            "impact", "risk", "assessment", "action", "strategy",
        ]
        self.fishery_keywords = [
            "fishing", "fish", "catch", "oxygen", "hypoxia", "zone",
            "season", "fishery", "aquaculture", "marine life",
        ]
        self.shipping_keywords = [
            "route", "navigation", "shipping", "vessel", "current",
            "wave", "storm", "alert", "safety", "passage",
        ]
        self.ngo_keywords = [
            "conservation", "protection", "environment", "climate",
            "pollution", "ecosystem", "biodiversity", "sustainability",
        ]

    async def detect_and_update_user_context(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Optional[UserContext]:
        """Detect user type from query and update context."""
        try:
            # Get or create user context
            user_context = self._get_or_create_context(session_id, user_id)

            # Detect user type from query
            user_type = self._detect_user_type(query)
            if user_type:
                user_context.user_type = user_type

            # Detect expertise level
            expertise_level = self._detect_expertise_level(query, user_type)
            if expertise_level:
                user_context.expertise_level = expertise_level

            # Update query count and history
            user_context.total_queries += 1
            user_context.last_query_date = datetime.utcnow()

            # Update interaction history
            if user_context.interaction_history is None:
                user_context.interaction_history = []
            user_context.interaction_history.append({
                "query": query,
                "timestamp": datetime.utcnow().isoformat(),
                "user_type": user_type,
            })

            # Keep only last 50 interactions
            if len(user_context.interaction_history) > 50:
                user_context.interaction_history = user_context.interaction_history[-50:]

            # Update recent queries
            if user_context.recent_queries is None:
                user_context.recent_queries = []
            user_context.recent_queries.append(query)
            if len(user_context.recent_queries) > 10:
                user_context.recent_queries = user_context.recent_queries[-10:]

            self.db.commit()
            self.db.refresh(user_context)

            return user_context

        except Exception as e:
            logger.error("Failed to update user context", error=str(e))
            self.db.rollback()
            return None

    def _get_or_create_context(
        self,
        session_id: Optional[str],
        user_id: Optional[str],
    ) -> UserContext:
        """Get or create user context."""
        if user_id:
            context = self.db.query(UserContext).filter(
                UserContext.user_id == user_id
            ).first()
        elif session_id:
            context = self.db.query(UserContext).filter(
                UserContext.session_id == session_id
            ).first()
        else:
            context = None

        if not context:
            context = UserContext(
                id=uuid.uuid4(),
                session_id=session_id,
                user_id=user_id,
                total_queries=0,
            )
            self.db.add(context)
            self.db.commit()
            self.db.refresh(context)

        return context

    def _detect_user_type(self, query: str) -> Optional[str]:
        """Detect user type from query text."""
        query_lower = query.lower()

        # Count keyword matches
        scores = {
            "researcher": sum(1 for kw in self.researcher_keywords if kw in query_lower),
            "student": sum(1 for kw in self.student_keywords if kw in query_lower),
            "manager": sum(1 for kw in self.manager_keywords if kw in query_lower),
            "fishery": sum(1 for kw in self.fishery_keywords if kw in query_lower),
            "shipping": sum(1 for kw in self.shipping_keywords if kw in query_lower),
            "ngo": sum(1 for kw in self.ngo_keywords if kw in query_lower),
        }

        # Get user type with highest score
        max_score = max(scores.values())
        if max_score > 0:
            user_type = max(scores, key=scores.get)
            return user_type

        return None

    def _detect_expertise_level(
        self,
        query: str,
        user_type: Optional[str],
    ) -> Optional[str]:
        """Detect expertise level from query."""
        query_lower = query.lower()

        # Simple heuristic based on query complexity
        if any(word in query_lower for word in ["simple", "basic", "explain", "what is"]):
            return "beginner"
        elif any(word in query_lower for word in ["advanced", "statistical", "regression", "correlation"]):
            return "expert"
        elif user_type == "researcher":
            return "expert"
        elif user_type == "student":
            return "beginner"
        else:
            return "intermediate"

    async def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from query (locations, parameters, time ranges, etc.)."""
        entities = {
            "locations": [],
            "parameters": [],
            "time_ranges": [],
            "depth_ranges": [],
        }

        query_lower = query.lower()

        # Extract parameters
        parameters = [
            "temperature", "salinity", "pressure", "oxygen", "chlorophyll",
            "nitrate", "ph", "depth", "density", "current", "wave",
        ]
        for param in parameters:
            if param in query_lower:
                entities["parameters"].append(param)

        # Extract depth ranges (simple pattern matching)
        depth_pattern = r"(\d+)\s*(?:meter|m|depth)"
        depth_matches = re.findall(depth_pattern, query_lower)
        if depth_matches:
            entities["depth_ranges"].extend([int(d) for d in depth_matches])

        # Extract time ranges (simple pattern matching)
        time_patterns = [
            r"(\d{4})",  # Year
            r"(january|february|march|april|may|june|july|august|september|october|november|december)",
            r"(last\s+\d+\s+(?:day|month|year))",
        ]
        for pattern in time_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                entities["time_ranges"].extend(matches)

        return entities

    async def detect_query_intent(self, query: str) -> Optional[str]:
        """Detect query intent."""
        query_lower = query.lower()

        if any(word in query_lower for word in ["explore", "show", "find", "search", "list"]):
            return "data_exploration"
        elif any(word in query_lower for word in ["recommend", "should", "decision", "best", "optimal"]):
            return "decision_support"
        elif any(word in query_lower for word in ["explain", "what is", "how", "why", "learn"]):
            return "learning"
        elif any(word in query_lower for word in ["alert", "monitor", "track", "watch"]):
            return "monitoring"
        elif any(word in query_lower for word in ["download", "export", "save", "get data"]):
            return "export"
        else:
            return "data_exploration"

