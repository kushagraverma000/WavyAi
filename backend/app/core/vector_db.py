"""Vector database configuration and client."""
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http import models

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class VectorDB:
    """Vector database client for Qdrant."""

    def __init__(self):
        """Initialize Qdrant client."""
        try:
            self.client = QdrantClient(url=settings.QDRANT_URL)
            self.collection_name = "argo_profiles"
            self.vector_size = 384  # all-MiniLM-L6-v2 embedding size
            self._ensure_collection()
        except Exception as e:
            logger.error("Failed to initialize Qdrant client", error=str(e))
            self.client = None

    def _ensure_collection(self):
        """Ensure collection exists."""
        if not self.client:
            return
        
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error("Failed to ensure collection", error=str(e))

    def add_vectors(
        self,
        points: List[Dict[str, Any]],
    ) -> bool:
        """Add vectors to the collection."""
        if not self.client:
            return False
        
        try:
            point_structs = []
            for point in points:
                # Convert UUID string to int for Qdrant
                point_id = point["id"]
                try:
                    import uuid as uuid_lib
                    if isinstance(point_id, str):
                        uuid_obj = uuid_lib.UUID(point_id)
                        point_id_int = uuid_obj.int % (2**63)  # Qdrant uses int64
                    else:
                        point_id_int = int(point_id)
                except Exception:
                    # If not UUID, use hash
                    point_id_int = hash(str(point_id)) % (2**63)
                
                point_structs.append(
                    PointStruct(
                        id=point_id_int,
                        vector=point["vector"],
                        payload=point.get("payload", {}),
                    )
                )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=point_structs,
            )
            return True
        except Exception as e:
            logger.error("Failed to add vectors", error=str(e))
            return False

    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        if not self.client:
            return []
        
        try:
            search_filter = None
            if filter:
                search_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value),
                        )
                        for key, value in filter.items()
                    ]
                )
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=search_filter,
            )
            
            return [
                {
                    "id": str(result.payload.get("profile_id", result.id)),
                    "score": result.score,
                    "payload": result.payload,
                }
                for result in results
            ]
        except Exception as e:
            logger.error("Vector search failed", error=str(e))
            return []

    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors by IDs."""
        if not self.client:
            return False
        
        try:
            # Convert UUID strings to integers for Qdrant
            point_ids = []
            for id_str in ids:
                try:
                    # Try to convert UUID to int hash
                    import uuid as uuid_lib
                    uuid_obj = uuid_lib.UUID(id_str)
                    point_ids.append(uuid_obj.int % (2**63))  # Qdrant uses int64
                except Exception:
                    # If not UUID, try direct int conversion
                    point_ids.append(int(id_str))
            
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=point_ids,
                ),
            )
            return True
        except Exception as e:
            logger.error("Failed to delete vectors", error=str(e))
            return False


# Global vector DB instance
_vector_db: Optional[VectorDB] = None


def get_vector_db() -> VectorDB:
    """Get vector database instance."""
    global _vector_db
    if _vector_db is None:
        _vector_db = VectorDB()
    return _vector_db
