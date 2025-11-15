"""Query service for processing natural language queries."""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.schemas.query import QueryResponse
from app.services.user_profiling import UserProfilingService
from app.services.rag_service import RAGService

logger = get_logger(__name__)


class QueryService:
    """Service for processing natural language queries."""

    def __init__(self, db: Session):
        """Initialize query service."""
        self.db = db
        self.user_profiling_service = UserProfilingService(db)
        self.rag_service = RAGService(db)

    async def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> QueryResponse:
        """Process a natural language query."""
        try:
            # 1. Detect user type and update context
            user_context = await self.user_profiling_service.detect_and_update_user_context(
                query=query,
                session_id=session_id,
                user_id=user_id,
            )

            # 2. Extract entities (locations, parameters, time ranges, etc.)
            entities = await self.user_profiling_service.extract_entities(query)

            # 3. Detect query intent
            query_intent = await self.user_profiling_service.detect_query_intent(query)

            # 4. Perform RAG search
            rag_results = await self.rag_service.search(
                query=query,
                user_context=user_context,
                entities=entities,
            )

            # 5. Generate adaptive response
            response = await self.rag_service.generate_response(
                query=query,
                rag_results=rag_results,
                user_context=user_context,
                query_intent=query_intent,
                entities=entities,
            )

            # 6. Generate visualization configuration
            visualization = await self.rag_service.generate_visualization(
                query=query,
                rag_results=rag_results,
                user_context=user_context,
            )

            return QueryResponse(
                response=response["text"],
                sources=rag_results.get("sources", []),
                visualization=visualization,
                user_type=user_context.user_type if user_context else None,
                query_intent=query_intent,
                entities=entities,
                metadata={
                    "model": "claude-3.5-sonnet",
                    "confidence": response.get("confidence", 0.0),
                },
            )

        except Exception as e:
            logger.error("Query processing failed", error=str(e), query=query)
            raise

