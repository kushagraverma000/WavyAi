"""Data ingestion tasks."""
from celery import Task
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.services.data_ingestion import DataIngestionService
from app.services.embedding_service import get_embedding_service
from app.core.vector_db import get_vector_db
from app.models.profile import Profile

logger = get_logger(__name__)


@celery_app.task(bind=True, name="ingest_netcdf_file")
def ingest_netcdf_file(self: Task, file_path: str) -> dict:
    """Ingest a NetCDF file into the database."""
    db = SessionLocal()
    try:
        ingestion_service = DataIngestionService(db)
        result = ingestion_service.ingest_netcdf_file(file_path)
        logger.info("NetCDF ingestion completed", file_path=file_path, result=result)
        return result
    except Exception as e:
        logger.error("NetCDF ingestion failed", error=str(e), file_path=file_path, exc_info=True)
        raise
    finally:
        db.close()


@celery_app.task(bind=True, name="generate_embeddings")
def generate_embeddings(self: Task, profile_id: str) -> dict:
    """Generate embeddings for a profile."""
    db = SessionLocal()
    try:
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise ValueError(f"Profile not found: {profile_id}")
        
        embedding_service = get_embedding_service()
        vector_db = get_vector_db()
        
        if profile.summary and embedding_service and vector_db:
            embedding = embedding_service.generate_embedding(profile.summary)
            if embedding:
                vector_db.add_vectors([{
                    "id": str(profile.id),
                    "vector": embedding,
                    "payload": {
                        "profile_id": str(profile.id),
                        "float_id": str(profile.float_id),
                        "date": profile.profile_date.isoformat(),
                        "latitude": profile.latitude,
                        "longitude": profile.longitude,
                        "summary": profile.summary,
                    },
                }])
                logger.info("Embedding generated", profile_id=profile_id)
                return {"status": "success", "profile_id": profile_id}
        
        return {"status": "skipped", "profile_id": profile_id, "reason": "No summary or service unavailable"}
    except Exception as e:
        logger.error("Embedding generation failed", error=str(e), profile_id=profile_id, exc_info=True)
        raise
    finally:
        db.close()

