"""Query endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any

from app.core.logging import get_logger
from app.services.simple_query_service import simple_query_service

router = APIRouter()
logger = get_logger(__name__)


@router.post("")
async def query(request: Dict[str, Any]):
    """Process a natural language query."""
    try:
        # Extract request data
        query_text = request.get("query", "")
        session_id = request.get("session_id")
        user_id = request.get("user_id")
        context = request.get("context", {})
        
        if not query_text:
            raise HTTPException(status_code=400, detail="Query text is required")
        
        # Process query using simple service
        response = await simple_query_service.process_query(
            query=query_text,
            session_id=session_id,
            user_id=user_id,
            context=context,
        )
        
        return response
        
    except Exception as e:
        logger.error("Query processing failed", error=str(e), query=request.get("query", ""))
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

