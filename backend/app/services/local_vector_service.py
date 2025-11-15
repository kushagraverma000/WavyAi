"""
Local vector database service using FAISS instead of Qdrant.
This runs entirely locally without Docker dependencies.
"""
import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import pickle

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available, using simple similarity search")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("SentenceTransformers not available, using simple text matching")


class LocalVectorService:
    """Local vector database service using FAISS."""
    
    def __init__(self):
        """Initialize local vector service."""
        self.vector_dir = Path("data/vectors")
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_path = self.vector_dir / "index.faiss"
        self.metadata_path = self.vector_dir / "metadata.json"
        self.embeddings_path = self.vector_dir / "embeddings.pkl"
        
        self.dimension = 384  # Default dimension for sentence transformers
        self.index = None
        self.metadata = []
        self.embeddings = []
        
        # Initialize embedding model
        self.embedding_model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded SentenceTransformer model")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
        
        # Load existing index
        self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index and metadata."""
        try:
            if FAISS_AVAILABLE and self.index_path.exists():
                self.index = faiss.read_index(str(self.index_path))
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            
            if self.metadata_path.exists():
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded {len(self.metadata)} metadata entries")
            
            if self.embeddings_path.exists():
                with open(self.embeddings_path, 'rb') as f:
                    self.embeddings = pickle.load(f)
                logger.info(f"Loaded {len(self.embeddings)} embeddings")
                
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            self._initialize_empty_index()
    
    def _initialize_empty_index(self):
        """Initialize empty FAISS index."""
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            logger.info("Initialized empty FAISS index")
        self.metadata = []
        self.embeddings = []
    
    def _save_index(self):
        """Save FAISS index and metadata."""
        try:
            if FAISS_AVAILABLE and self.index is not None:
                faiss.write_index(self.index, str(self.index_path))
            
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            with open(self.embeddings_path, 'wb') as f:
                pickle.dump(self.embeddings, f)
                
            logger.info("Saved vector index and metadata")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text."""
        if self.embedding_model:
            try:
                embedding = self.embedding_model.encode([text])[0]
                # Normalize for cosine similarity
                embedding = embedding / np.linalg.norm(embedding)
                return embedding.astype(np.float32)
            except Exception as e:
                logger.error(f"Failed to get embedding: {e}")
        
        # Fallback: simple hash-based embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        # Create a simple embedding from hash
        embedding = np.array([
            (hash_int >> i) & 1 for i in range(self.dimension)
        ], dtype=np.float32)
        
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        return embedding
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector index."""
        try:
            new_embeddings = []
            new_metadata = []
            
            for doc in documents:
                # Extract text content
                text_content = doc.get('content', '')
                if not text_content:
                    # Combine available text fields
                    text_parts = []
                    for field in ['title', 'description', 'text', 'summary']:
                        if field in doc and doc[field]:
                            text_parts.append(str(doc[field]))
                    text_content = ' '.join(text_parts)
                
                if not text_content:
                    logger.warning("Document has no text content, skipping")
                    continue
                
                # Get embedding
                embedding = self._get_embedding(text_content)
                new_embeddings.append(embedding)
                
                # Store metadata
                metadata = {
                    'id': doc.get('id', len(self.metadata)),
                    'content': text_content[:500],  # Truncate for storage
                    'source': doc.get('source', 'unknown'),
                    'type': doc.get('type', 'document'),
                    'timestamp': doc.get('timestamp'),
                    **{k: v for k, v in doc.items() if k not in ['content', 'embedding']}
                }
                new_metadata.append(metadata)
            
            if not new_embeddings:
                logger.warning("No valid documents to add")
                return False
            
            # Add to FAISS index
            if FAISS_AVAILABLE and self.index is not None:
                embeddings_array = np.vstack(new_embeddings)
                self.index.add(embeddings_array)
            
            # Update metadata and embeddings
            self.metadata.extend(new_metadata)
            self.embeddings.extend(new_embeddings)
            
            # Save to disk
            self._save_index()
            
            logger.info(f"Added {len(new_embeddings)} documents to vector index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    def search(self, query: str, limit: int = 10, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            if not self.metadata:
                logger.info("No documents in index")
                return []
            
            # Get query embedding
            query_embedding = self._get_embedding(query)
            
            results = []
            
            if FAISS_AVAILABLE and self.index is not None and self.index.ntotal > 0:
                # Use FAISS for search
                query_vector = query_embedding.reshape(1, -1)
                scores, indices = self.index.search(query_vector, min(limit, self.index.ntotal))
                
                for score, idx in zip(scores[0], indices[0]):
                    if idx >= 0 and idx < len(self.metadata) and score >= score_threshold:
                        result = self.metadata[idx].copy()
                        result['score'] = float(score)
                        results.append(result)
            
            else:
                # Fallback: compute similarities manually
                if self.embeddings:
                    similarities = []
                    for i, doc_embedding in enumerate(self.embeddings):
                        similarity = np.dot(query_embedding, doc_embedding)
                        similarities.append((similarity, i))
                    
                    # Sort by similarity
                    similarities.sort(reverse=True)
                    
                    # Get top results
                    for similarity, idx in similarities[:limit]:
                        if similarity >= score_threshold:
                            result = self.metadata[idx].copy()
                            result['score'] = float(similarity)
                            results.append(result)
                else:
                    # Simple text matching fallback
                    query_lower = query.lower()
                    for i, metadata in enumerate(self.metadata):
                        content = metadata.get('content', '').lower()
                        if query_lower in content:
                            result = metadata.copy()
                            result['score'] = 0.5  # Default score
                            results.append(result)
                            if len(results) >= limit:
                                break
            
            logger.info(f"Found {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        return {
            'total_documents': len(self.metadata),
            'dimension': self.dimension,
            'index_type': 'FAISS' if FAISS_AVAILABLE else 'Simple',
            'embedding_model': 'SentenceTransformer' if self.embedding_model else 'Hash-based',
            'storage_path': str(self.vector_dir)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        return {
            'status': 'healthy',
            'total_documents': len(self.metadata),
            'faiss_available': FAISS_AVAILABLE,
            'embedding_model_available': self.embedding_model is not None,
            'index_loaded': self.index is not None if FAISS_AVAILABLE else True
        }


# Global instance
_vector_service: Optional[LocalVectorService] = None


def get_vector_service() -> LocalVectorService:
    """Get vector service instance."""
    global _vector_service
    if _vector_service is None:
        _vector_service = LocalVectorService()
    return _vector_service
